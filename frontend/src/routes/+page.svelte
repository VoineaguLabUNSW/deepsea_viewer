<script>
    import { derived } from "svelte/store"
    import CascadeDropdown from "../lib/components/cascadedropdown.svelte";
    import Heatmap from "../lib/components/heatmap.svelte"
    import { getContext } from 'svelte'
    import Navbar from '../lib/components/navbar.svelte'
	import { createListParam } from "../lib/stores/param";
    import { goto } from '$app/navigation';
    import { base } from '$app/paths';

    let { metadata, curr_selection, curr_heatmap } = getContext('core');

    let selection_param = createListParam('selection', true);

    function paramMessageReceiver(e) {
        if (e.origin !== window.location.origin) return
        if(typeof e.data !== 'object') return
        if(e.data.type !== 'heatmap_goto') return
        goto(base + e.data.path)
    }

    const getters = derived(metadata, ($metadata, set) => {$metadata?.value && set([
        {name: 'Sequences', options: (job_id) => {let ret = Object.keys($metadata.value.user_sequences); ret.sort(); return ret}},
        {name: 'Chromatin features', options: (job_id, enh_id) => $metadata.value.headings.map(h => {let [c, f, t] = h.split('|'); return `Cell type: ${c} | Chromatin feature type: ${f} | Treatment: ${t}`})}
    ])});
</script>

<svelte:window on:message={paramMessageReceiver}/>

<Navbar/>

<div class="mx-12 mt-12 relative">
    <div class='{$metadata?.error || "hidden"} absolute m-[20%] z-50 text-red-600 bg-[#ffffff77] rounded-md p-4'>{$metadata?.error || ''}</div>
{#if $curr_heatmap !== undefined}
    <Heatmap/>
{:else}
    <div role="status" class="w-full p-4 border border-gray-200 rounded shadow md:p-6 dark:border-gray-700 {$metadata?.error || 'animate-pulse'}">
        <div class="flex items-baseline mt-4">
            {#each {length: 20} as _, i}
            <div style="height: {Math.random() * 100 + 200}px" class="w-full bg-gray-200 rounded-t-lg ms-6 dark:bg-gray-700"></div>
            {/each}
        </div>
        <span class="sr-only">Loading...</span>
    </div>
{/if}
</div>

<div class="mx-[20%] my-12">
    {#if $getters !== undefined }
        <CascadeDropdown getters={$getters} bind:selected={selection_param} bind:selected_detail={curr_selection}/>
    {:else}
        <div role="status" class="w-full p-4 border border-gray-200 rounded shadow animate-pulse md:p-6 dark:border-gray-700">
            <div class="h-2.5 bg-gray-200 rounded-full dark:bg-gray-700 mb-2.5"></div>
            <div class="h-2 mb-10 bg-gray-200 rounded-full dark:bg-gray-700"></div>
        </div>
    {/if}
</div>
