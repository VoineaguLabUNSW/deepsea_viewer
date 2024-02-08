import concurrent.futures, csv, contextlib, zlib, json, os, gzip, functools, re, collections, argparse, threading, webbrowser, time, sys, http.server
import requests, RangeHTTPServer
import deepsea_viewer.data_pb2 as data_pb2

types = [
    'AA', 'AG', 'AC', 'AT',
    'GA', 'GG', 'GC', 'GT',
    'CA', 'CG', 'CC', 'CT',
    'TA', 'TG', 'TC', 'TT']

def store(url, dest):
    path = os.path.join(dest, os.path.basename(url) + '.gz')
    if not os.path.exists(path):
        with gzip.open(path + '.part', 'wb') as f:
            with requests.get(url, stream=True) as r:
                for d in r.iter_content(chunk_size=16384):
                    if not d: break
                    f.write(d)
        os.rename(path + '.part', path)
    return path

@contextlib.contextmanager
def write_compressed_ranges(path: str):
    '''Write independently retrievable gzipped float ranges to a binary file'''
    with open(path, 'wb') as f:
        def write_row(binary):
            start = f.tell()
            f.write(zlib.compress(binary, level=-1))
            return start, f.tell()
        yield write_row, f.tell

def iter_to_binary(reader, writer, heading_filter=None):
    headings = [e for e in enumerate(next(reader)[3:]) if (not heading_filter) or re.search(heading_filter, e[1])]
    heatmaps = [data_pb2.Heatmap() for _ in headings]

    for row in reader:
        type = types.index(row[1] + row[2])
        for i, e in enumerate(headings):
            heatmaps[i].types.append(type)
            heatmaps[i].values.append(float(row[3 + e[0]]))
    ranges = [writer(heatmaps[i].SerializeToString()) for i in range(len(headings))]
    return ranges, [e[1] for e in headings]

def make_jobs_local(job_ids, dest, heading_filter=None, desc=None):
    job_metadata = {}
    user_sequences=collections.OrderedDict()
    headings = []
    paths = []
    with write_compressed_ranges(os.path.join(dest, 'data.bin')) as writer_utils:
        writer, _ = writer_utils
        for job_id in job_ids:
            print('processing job ' + job_id)
            out = os.path.join(dest, job_id)
            os.makedirs(out, exist_ok=True)

            # Obtain paths, use cache as fallback
            paths = None
            try:
                r = requests.get(f'https://hb.flatironinstitute.org/api/deepsea/jobs/{job_id}')
                r.raise_for_status()
                data = r.json()
                keys = [k for k,v in data['files'].items() if 'logits' in v]
                urls = [data['files'][k]['logits']['url'] for k in keys]
                with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
                    paths = executor.map(functools.partial(store, dest=out), urls)
            except requests.exceptions.HTTPError as e:
                if e.response.status_code != 404: raise Exception(f'issue fetching job {job_id} ({e})')
                try: paths = [os.path.join(out, p) for p in os.listdir(out) if p.endswith('.tsv.gz')]
                except FileNotFoundError: raise Exception(f'job id {job_id} not found online or in cache')

            # Append to binary
            for path in paths:
                name = os.path.basename(path).replace('_logits.tsv.gz', '')
                print('processing user sequence ' + name)
                with gzip.open(path, 'rt', newline='') as g:
                    reader = csv.reader(g, delimiter='\t')
                    ranges, curr_headings = iter_to_binary(reader, writer, heading_filter)
                    if headings and (len(headings) != len(curr_headings) or any(headings[i] != curr_headings[i] for i in range(len(headings)))):
                        raise Exception('Headings inconsistent')
                    headings = curr_headings
                    if name in user_sequences: raise Exception(f'Duplicate user sequence ${name}, merging jobs failed')
                    user_sequences[name] = [r[0] for r in ranges] + [ranges[-1][1]]

    with open(os.path.join(dest, 'metadata.json'), 'w') as f:
        json.dump(dict(user_sequences=user_sequences, headings=headings, description=desc), f)

def main():
    parser = argparse.ArgumentParser(description='Utility for repackaging and serving deepsea heatmap data.')
    subparsers = parser.add_subparsers(title='commands', dest='command', required=True)

    create_parser = subparsers.add_parser('create', help='Create heatmap data')
    create_parser.add_argument('jobs', nargs='+', help='List of jobs to merge')
    create_parser.add_argument('-d', '--destination', required=True, help='Destination folder')
    create_parser.add_argument('-r', '--pattern', required=True, help='Regex pattern to filter headings')
    create_parser.add_argument('-desc', '--description', help='Description')

    serve_parser = subparsers.add_parser('serve', help='Serve heatmap data')
    serve_parser.add_argument('-d', '--destination', required=True, help='Destination folder')
    serve_parser.add_argument('-p', '--port', type=int, default=8000, help='Port')
    serve_parser.add_argument('-b', '--base', default='https://voineagulabunsw.github.io/deepsea_viewer', help='Base URL to launch viewer')

    args = parser.parse_args()

    if args.command == 'create':
        # Create destination folder
        make_jobs_local(args.jobs, args.destination, args.pattern, args.description)
    elif args.command == 'serve':
        # Serve destination folder with range requests/cors
        class CORSRequestHandler(RangeHTTPServer.RangeRequestHandler):
            def end_headers (self):
                self.send_header('Access-Control-Allow-Origin', '*')
                RangeHTTPServer.RangeRequestHandler.end_headers(self)
        def start_server():
            os.chdir(args.destination)
            httpd = http.server.HTTPServer(('localhost', args.port), CORSRequestHandler)
            httpd.serve_forever()

        threading.Thread(target=start_server,daemon=False).start()
        webbrowser.open_new(f'{args.base}?source=http://localhost:{args.port}/metadata.json')
