import csv, requests, liftover

converter = liftover.get_lifter('hg38', 'hg19')
r = requests.get('https://raw.githubusercontent.com/VoineaguLabUNSW/astrocyte_crispri_resource/main/docs/Website_ResultsMx.csv')
reader = csv.reader(r.iter_lines(decode_unicode=True), delimiter=',')
heading = next(reader)
coord_col = heading.index('')

enh_i, coord_i = [heading.index(h) for h in ('EnhancerID', 'EnhancerCoordinates')]
with open('metadata.tsv', 'w', newline='') as f:
    writer = csv.writer(f, delimiter='\t')
    written = {}
    for row in reader:
        if not len(row) or row[enh_i] in written: continue
        
        # Liftover coordinates (ignore)
        chrom, range = row[coord_i].split(':')
        chrom = chrom[3:]
        start, end = range.split('-')
        new_start = converter[chrom][int(start)]
        new_end = converter[chrom][int(end)]
        new_pos = f'{new_start[0][0]}:{new_start[0][1]}-{new_end[0][1]}'
        
        # Write TSV of sequence name \t size \t sequence description
        writer.writerow([row[enh_i], new_end[0][1]-new_start[0][1], f'{row[enh_i]} - {new_pos}'])
        written[row[enh_i]] = True
        