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

        const ranges = $metadata.value.user_sequences[$curr_selection[0].value];
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
                const buffer = await response.arrayBuffer();
                const unpacked = protobuf.Heatmap.fromBinary(pako.inflate(new Uint8Array(buffer)));
                curr_heatmap.set({data: unpacked});
            } catch(e) {
                curr_heatmap.set({error: `Unexpected data - ${e}`});
            }
        }
    });
    return { metadata, curr_selection, curr_heatmap };
}

export { createCore };
