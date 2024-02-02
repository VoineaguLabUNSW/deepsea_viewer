<script>
    import { writable, get } from 'svelte/store'
    import { Button, Dropdown, DropdownItem, Search } from 'flowbite-svelte';
    import { createCascadeParam } from '../stores/param.js'
    import { goto } from '$app/navigation';
    import { page } from '$app/stores';

    // NOTE: bind:selected causes an unecessary update, will be fixed in svelte 5 (https://github.com/sveltejs/svelte/issues/4265)

    export let getters = []; // function that takes all depending selected and returns options
    export let selected = writable([]);

    let current = undefined; // current open dropdown level
    let search = ''; // internal shared search state, reset when dropdowns close

    // Supply all dependant selections as arguments to user-provided getters
    function getValidOptions(level, curr_selected) {
        return getters[level].options(...curr_selected.slice(0, level).map(s => s.value));
    }

    // Recursively update dependent dropdowns, keeping existing values if still valid - only .value is required
    function tryUpdateSelected(new_selected, strict=false, level=0) {
        if(level >= getters.length) return selected.set(new_selected)
        const options = getValidOptions(level, new_selected)
        let index = level >= new_selected.length ? 0 : options.indexOf(new_selected[level]?.value);
        if(index === -1) {
            index = 0;
            if(strict) throw new Error('Invalid dropdown configuration requested');
        }
        new_selected[level] = {value: options[index], index, options}
        tryUpdateSelected(new_selected, strict, level+1);
    }

    // Strict setter for manual setting e.g. query parameters - or should it
    export const try_selected = {subscribe: selected.subscribe, set: (new_selected) => tryUpdateSelected(new_selected, true)}

    // Handle clicks / initialization
    function updateChildren(e=undefined) {
        current=undefined
        const curr_selected = get(selected);
        let level, index, options, value;
        if(!e) {
            level = 0;
            index = 0;
            options = getValidOptions(0, curr_selected)
            value = options[0];
        } else {
            level = parseInt(e.target.dataset.level);
            index = parseInt(e.target.dataset.index);
            options = curr_selected[level]?.options || getValidOptions(level, curr_selected);
            value = e.target.dataset.value;
        }
        if(curr_selected[level]?.value === value) return;
        curr_selected[level] = {index, value, options};
        tryUpdateSelected(curr_selected, false, level+1);
    }
    updateChildren()
</script>

<div class="flex flex-col gap-y-4">
    {#each $selected as s, i }
        <div class='flex w-full flex-col items-stretch'>
            <div class='text-sm ml-2'>{getters[i].name} ({s.options.length})</div>
            <Button size="sm" on:click={() => current=i} class="text-dark dark:text-white" color='light'>
                <span class="overflow-x-hidden text-ellipsis">
                    {s.value}
                </span>
                <i class='fas fa-angle-down pl-2 text-gray-200'/></Button>
            <Dropdown placement='bottom' open={current===i} headerClass="m-2" containerClass='w-full z-50' on:show={(e) => {if(!e.detail) {search=''; current=undefined}}} class="overflow-y-auto px-3 pb-3 text-sm h-44 divide-y divide-gray-100">
                <div slot="header">
                    <Search autofocus placeholder='Filter...' bind:value={search} size="md"/>
                </div>
                {#each s.options as option, j}
                    {#if option.toLowerCase().includes(search.toLowerCase())}
                    <DropdownItem data-level={i} data-index={j} data-value={option} class="rounded p-2 hover:bg-gray-100 dark:hover:bg-gray-600" on:click={updateChildren}>
                        {option}
                    </DropdownItem>
                    {/if}
                {/each}
            </Dropdown>
        </div>
    {/each}
</div>
