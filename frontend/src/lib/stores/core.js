import * as pako from 'pako';
import { asyncDerived, writable, get } from "@square/svelte-store";
import * as protobuf from '../../gen/data_pb'

function createCore(url) {
    const metadata = asyncDerived(url,
        async ($url) => {
            try { return {url: $url, value: await (await fetch($url)).json()}; }
            catch(e) { console.log(e); return {error: `Unable to load source ${$url}: (${e})`}; }
        }
    );

    let curr_selection = writable([]);
    let curr_heatmap = writable(undefined);
    curr_selection.subscribe(async ($curr_selection) => {
        if($curr_selection.some(s => s?.value === undefined)) return
        let $metadata = get(metadata)
        if($metadata === undefined) return;
        if($metadata.error) curr_heatmap.set({error: $metadata.error})

        curr_heatmap.set({loading: true});

        const sequence = $metadata.value.user_sequences[$curr_selection[0].value]
        const ranges = sequence.bytes;
        const index = $curr_selection[1].index
        const controller = new AbortController();
        const response = await fetch($metadata.url.slice(0, $metadata.url.lastIndexOf('/')) + '/data.bin' , {
            signal: controller.signal,
            headers: {'Range': 'bytes=' + `${ranges[index]}-${ranges[index+1]-1}`},
        });

        if(response.status !== 206) {
            controller.abort();
            curr_heatmap.set({error: `Expected 206, got ${response.status}`});
        } else {
            try {
                curr_heatmap.set(createHeatmapData(await response.arrayBuffer(), $curr_selection[0].value, sequence.desc, sequence.size));
            } catch(e) {
                curr_heatmap.set({error: `Unexpected data - ${e}`});
            }
        }
    });
    return { metadata, curr_selection, curr_heatmap };
}

/*
* Storage format is closer to original mutation representation rather than simple matrix
* The type of mutation is stored in a single enum
*/
const MUTATION_DISPLAY_ORDER = 'CGTA';
const TYPE_TO_ORDER = [
    'AA', 'AG', 'AC', 'AT',
    'GA', 'GG', 'GC', 'GT',
    'CA', 'CG', 'CC', 'CT',
    'TA', 'TG', 'TC', 'TT'
].map(t => ({from: t[0], to: t[1], annot: `${t[0]}->${t[1]}`, y: MUTATION_DISPLAY_ORDER.indexOf(t[1])}));
function createHeatmapData(arraybuffer, name, description, size) {
    const data = protobuf.Heatmap.fromBinary(pako.inflate(new Uint8Array(arraybuffer)));
    const values = data.values;
    const cells = data.types.map(t => TYPE_TO_ORDER[t]);
    const headings = cells.filter((_, i) => !(i % 3)).map(p => p.from);
    const timestamp = Date.now();
    return { values, cells, headings, name, description, size, timestamp }
}

/*
* Similar to realtime/core implementation but complicated by the fact that we want to display progress
* Each selection/file is roughly 30Mb and must be rearranged in-memory
*/
async function batchDownloadSelections(curr_download, $metadata, selections) {
    let [xhr, aborted] = [undefined, false];
    const cancel_func = () => { aborted = true; xhr?.abort(); }
    if (selections === undefined) selections = [Object.keys($metadata.value.user_sequences)[0]]
    curr_download.set({current: selections[0], progress: 0, cancel: cancel_func})
    let [total, loaded, estTotal] = [0, 0, 0];
    try {
        for (let i=0; i<selections.length && !aborted; ++i) {
            let first = true;
            const sequence = $metadata.value.user_sequences[selections[i]];
            const ranges = sequence.bytes;
            await new Promise(function (resolve, reject) {
                xhr = new XMLHttpRequest();
                xhr.open('GET', $metadata.url.slice(0, $metadata.url.lastIndexOf('/')) + '/data.bin', true);
                xhr.setRequestHeader('Range', 'bytes=' + `${ranges[0]}-${ranges[ranges.length - 1] - 1}`);
                xhr.responseType = 'arraybuffer';
                xhr.onload = function () {
                    const results = $metadata.value.headings.map((h, j) => createHeatmapData(xhr.response.slice(ranges[j]-ranges[0], ranges[j + 1]-ranges[0]), selections[i], sequence.desc, sequence.size));
                    const tsv = 'pos\tref\talt\t' + $metadata.value.headings.join('\t') + '\n' + results[0].cells.map((c, y) => `${Math.floor(y / 3)}\t${c.from}\t${c.to}\t${results.map(r => r.values[y]).join('\t')}`).join('\n')
                    downloadCSV(tsv, `${selections[i]}_logits.tsv`)
                    resolve();
                };
                let prevProgress = 0;
                xhr.onprogress = function (e) {
                    if (first) {
                        if (xhr.status != 206 || !e.lengthComputable) xhr.abort();
                        total += e.total;
                        first = false;
                    }
                    loaded += (e.loaded - prevProgress);
                    prevProgress = e.loaded;
                    estTotal = total + (total / (i+1)) * (selections.length - (i+1));
                    curr_download.set({current: selections[i], progress: loaded / estTotal, cancel: cancel_func})
                };
                xhr.onerror = xhr.onabort = reject
                xhr.send();
            });
        }
        curr_download.set({});
    } catch(e) {
        curr_download.set(!aborted ? { error: 'network error - download failed' } : {});
    }
}

function downloadCSV(string, fileName) {
    var blob = new Blob([string]);
    if (navigator.msSaveBlob) {
        // IE 10+
        navigator.msSaveBlob(blob, fileName);
    } else if (navigator.userAgent.match(/iPhone|iPad|iPod/i)) {
        var hiddenElement = window.document.createElement("a");
        hiddenElement.href = "data:text/csv;charset=utf-8," + encodeURI(string);
        hiddenElement.target = "_blank";
        hiddenElement.download = fileName;
        hiddenElement.click();
    } else {
        let link = document.createElement("a");
        if (link.download !== undefined) {
            // Browsers that support HTML5 download attribute
            var url = URL.createObjectURL(blob);
            link.setAttribute("href", url);
            link.setAttribute("download", fileName);
            link.style.visibility = "hidden";
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        }
    }
}

export { createCore, batchDownloadSelections, createHeatmapData };
