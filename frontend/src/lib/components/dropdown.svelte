<script>
    import { Button, Dropdown, Search} from 'flowbite-svelte';

    export let selected;
    export let optional = false;

    export let groups;
    export let title = '';
    export let placeholder = 'Select...';
    export let mainClass = '';
    export let color = 'light';

    let open = false;
    let filter = '';
    let disabled = '';
    
    $: disabled = !groups || Array.from(groups.values()).reduce((acc, arr) => acc + arr.length, 0) == 0
    $: if(!open) filter = '';
  </script>
  
<div class='flex w-52 flex-col items-stretch'>
    <div class='text-sm ml-2'>{title}</div>
    <Button class={mainClass} disabled={disabled} color={color}>
        <span class="overflow-x-hidden text-ellipsis">
            {$selected?.name || placeholder}
        </span><i class='fas fa-angle-down pl-2 text-gray-200'/></Button>
    <Dropdown placement='down' headerClass="m-2" containerClass='w-60 z-50' bind:open class="overflow-y-auto px-3 pb-3 text-sm h-44 divide-y divide-gray-100">
    <div slot="header">
        <Search autofocus placeholder='Filter...' bind:value={filter} size="md"/>
    </div>
    {#each Array.from(groups).map(([key, values]) => [key, values.filter(v => key.toLowerCase().includes(filter.toLowerCase()) || v.name.toLowerCase().includes(filter.toLowerCase()))]).filter(([_, values]) => values.length) as [key, values]}
        <div class='p-2 text-gray-400'>{key}</div>
        {#each values as v }
            {#key v}
                {#if v.disabled}
                    <li class="rounded pl-4 p-2 bg-gray-100 dark:hover:bg-gray-600">{v.name}</li>
                {:else if v.id == $selected?.id}
                    <li class="rounded pl-4 p-2 bg-gray-100 dark:bg-gray-600 overflow-x-hidden text-ellipsis" on:click={() => {optional && selected.set(undefined); open=false}}>{v.name}</li>
                {:else}
                    <li class="rounded pl-4 p-2 hover:bg-gray-100 dark:hover:bg-gray-600  overflow-x-hidden text-ellipsis" on:click={() => {selected.set(v); open=false}}>{v.name}</li>
                {/if}
            {/key}
        {/each}
    {/each}
    </Dropdown>
</div>