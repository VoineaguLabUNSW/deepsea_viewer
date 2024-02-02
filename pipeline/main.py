import requests, concurrent.futures, csv, contextlib, zlib, json, os, gzip, functools, re, collections
import data_pb2

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

def make_jobs_local(job_ids, dest, heading_filter=None):
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
            r = requests.get(f'https://hb.flatironinstitute.org/api/deepsea/jobs/{job_id}')
            data = r.json()

            keys = [k for k,v in data['files'].items() if 'logits' in v]
            names = [data['files'][k]['logits']['name'] for k in keys]
            urls = [data['files'][k]['logits']['url'] for k in keys]

            with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
                paths = executor.map(functools.partial(store, dest=out), urls)

            for name, path in zip(names, paths):
                print('processing user sequence ' + name)
                with gzip.open(path, 'rt', newline='') as g:
                    reader = csv.reader(g, delimiter='\t')
                    ranges, curr_headings = iter_to_binary(reader, writer, heading_filter)
                    if headings and (len(headings) != len(curr_headings) or any(headings[i] != curr_headings[i] for i in range(len(headings)))):
                        raise Exception('Headings inconsistent')
                    headings = curr_headings
                    if name in user_sequences: raise Exception(f'Duplicate user sequence ${name}, merging jobs failed')
                    user_sequences[name] = [r[0] for r in ranges] + [ranges[-1][1]]

    with gzip.open(os.path.join(dest, 'metadata.json.gz'), 'wt') as f:
        json.dump(dict(user_sequences=user_sequences, headings=headings), f)

if __name__ == '__main__':
    make_jobs_local([
        '1d57acde-1d71-48c8-90d1-dcc45702a5fb',
        '65fb5c0e-ae5d-41a8-9f28-90a467c0fed1',
        'b87d5aee-42d0-4a05-9c90-3a2a969a4baf',
        '3172fe98-0069-43a1-9fc1-2e2e8a0a3187',
        '8fd1a2ae-3aeb-42a1-9326-d1157a8be82f',
        'cd4c218a-16b0-47ea-a1a2-9d71ca48f813',
        '54bc223e-15a2-4461-9b1c-171ca42fb1ef',
        'a4300dd3-05a9-45ac-8e23-57bcfc81a88e',
        'f27f9f00-bfbe-4de1-ade1-d8bef56a218f',
        '611cab83-06c1-4409-9002-44bccff8b0c6',
        ], './export', r'^NH_A_Astrocytes.*')
