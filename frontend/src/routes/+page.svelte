<script>
    import { writable, derived } from "svelte/store"
    import CascadeDropdown from "../lib/components/cascadedropdown.svelte";
    import Heatmap from "../lib/components/heatmap.svelte"
    import { createCore } from "../lib/stores/core"
    import Navbar from '../lib/components/navbar.svelte'
	import { createIntParam, createListParam } from "../lib/stores/param";

    let { metadata, curr_selection, curr_heatmap } = createCore('https://d33ldq8s2ek4w8.cloudfront.net/crispri/metadata.json');//"./export/metadata.json.gz"

    let subview_param = createIntParam('subview', 0, true);
    let selection_param = createListParam('selection', true, ['subview']);


    const getters = derived(metadata, ($metadata, set) => {$metadata?.value && set([
        {name: 'Sequences', options: (job_id) => Object.keys($metadata.value.user_sequences).toSorted()},
        {name: 'Chromatin features', options: (job_id, enh_id) => $metadata.value.headings}
    ])});
</script>

<Navbar/>

<div class="mx-12 mt-12">
{#if $curr_heatmap !== undefined }
    <Heatmap bind:data={curr_heatmap} bind:subview={subview_param}/>
{:else}
    <div role="status" class="w-full p-4 border border-gray-200 rounded shadow animate-pulse md:p-6 dark:border-gray-700">
        <div class="flex items-baseline mt-4">
            {#each {length: 20} as _, i}
            <div style="height: {Math.random() * 100 + 200}px" class="w-full bg-gray-200 rounded-t-lg ms-6 dark:bg-gray-700"></div>
            {/each}
        </div>
        <span class="sr-only">Loading...</span>
    </div>
{/if}
</div>

<div class="mx-48 my-12">
    {#if $getters !== undefined }
        <CascadeDropdown getters={$getters} bind:selected={selection_param} bind:selected_detail={curr_selection}/>
    {:else}
        <div role="status" class="w-full p-4 border border-gray-200 rounded shadow animate-pulse md:p-6 dark:border-gray-700">
            <div class="h-2.5 bg-gray-200 rounded-full dark:bg-gray-700 mb-2.5"></div>
            <div class="h-2 mb-10 bg-gray-200 rounded-full dark:bg-gray-700"></div>
        </div>
    {/if}
</div>
