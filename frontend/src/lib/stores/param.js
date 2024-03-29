import { goto } from '$app/navigation';
import { page } from '$app/stores';
import { derived, get } from 'svelte/store';

function createParam(param, defaultVal='', fnStore=v => v, fnLoad=v => v, preventSideEffects=false) {
    const store = derived(page, ($page)=> $page && fnLoad($page.url.searchParams.get(param)) || defaultVal, defaultVal)
    return {
        set: v => {
            let vStore = fnStore(v)
            let lastPage = get(page);
            if(lastPage.url.searchParams.get(param) == vStore) return; //attempt to debounce, but won't work beyond primitive types
            let query = new URLSearchParams(lastPage.url.searchParams.toString());
            query.set(param, vStore);
            goto(`${lastPage.url.pathname}?${query.toString()}`,  preventSideEffects && { keepFocus: true, noScroll: true});
        },
        subscribe: store.subscribe,
    }
}

function createIntParam(param, defaultVal=1, preventSideEffects=false) {
    return createParam(param, defaultVal, (v) => v, parseInt, preventSideEffects);
}

function createListParam(param, preventSideEffects=false) {
    return createParam(param, [], (v) => v && v.join(','), (v) => v && v.split(',').map(s => s ? s : undefined), preventSideEffects);
}

export { createIntParam, createParam, createListParam};
