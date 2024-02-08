<script>
    import { onDestroy } from 'svelte'
    import { writable, get, derived } from 'svelte/store'
    import { Button, Dropdown, DropdownItem, Search } from 'flowbite-svelte';

    // NOTE: bind:selected causes an unecessary update, will be fixed in svelte 5 (https://github.com/sveltejs/svelte/issues/4265)
    export let getters = []; // function that takes all depending selected and returns options
    export let selected = writable([]);

    let open = writable(undefined);
    let search = ''; // internal shared search state, reset when dropdowns close

    $: console.log($selected)

    let selected_detail_cache = [];
    export let selected_detail = writable([])
    let unsubscribe = selected.subscribe(($selected) => {
        let should_recalc = false;
        for(let level=0; level<getters.length; ++level) {
            should_recalc |= ($selected[level] === undefined || $selected[level] !== selected_detail_cache?.value)
            if(!should_recalc) continue;
            let options = getters[level].options(...$selected.slice(0, level));
            let index = options.indexOf($selected[level]);
            let error = undefined;
            if(index === -1) {
                if($selected[level] !== undefined) {
                    error = `Requested option not found: "${$selected[level]}"`
                }
                index = 0;
            }
            let value = options[index];
            selected_detail_cache[level] = {value, index, options, error};
        }
        selected_detail.set(selected_detail_cache);
    });

    function clickHandler(e) {
        open.set(undefined)
        const curr_selected = get(selected);
        let level = parseInt(e.target.dataset.level);
        let value =  e.target.dataset.value;
        if(curr_selected[level]?.value === value) return;
        curr_selected[level] = value;
        selected.set(curr_selected);
    }
    onDestroy(unsubscribe);
</script>

<div class="flex flex-col gap-y-4">
    {#each $selected_detail as s, i }
        <div class='flex w-full flex-col items-stretch'>
            <div class='flex flex-row'>
                <div class='text-sm ml-2'>{getters[i].name} ({s.options.length})</div>
                <div class='text-sm ml-2 text-red-500'>{s.error || ''}</div>
            </div>

            <Button size="sm" class="text-dark dark:text-white" color='light'>
                <span class="overflow-x-hidden text-ellipsis">
                    {s.value}
                </span>
                <i class='fas fa-angle-down pl-2 text-gray-200'/></Button>
            <Dropdown open={$open===i} placement='bottom' headerClass="m-2" containerClass='w-full z-50' on:show={(e) => {open.set(i); if(!e.detail) search=''}} class="overflow-y-auto px-3 pb-3 text-sm h-44 divide-y divide-gray-100">
                <div slot="header">
                    <Search autofocus placeholder='Filter...' bind:value={search} size="md"/>
                </div>
                {#each s.options as option, j}
                    {#if option.toLowerCase().includes(search.toLowerCase())}
                    <DropdownItem data-level={i} data-value={option} defaultClass="{s.index === j && 'bg-gray-200'} rounded p-2 hover:bg-gray-100 dark:hover:bg-gray-600" on:click={clickHandler}>
                        {option}
                    </DropdownItem>
                    {/if}
                {/each}
            </Dropdown>
        </div>
    {/each}
</div>
