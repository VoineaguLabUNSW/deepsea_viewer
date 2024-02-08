import { goto } from '$app/navigation';
import { page } from '$app/stores';
import { derived, get } from 'svelte/store';

function createParam(param, defaultVal='', fnStore=v => v, fnLoad=v => v, preventSideEffects=false, invalidates=[], invalidates_fn=undefined) {
    const store = derived(page, ($page)=> $page && fnLoad($page.url.searchParams.get(param)) || defaultVal, defaultVal)
    return {
        set: v => {
            let vStore = fnStore(v)
            let lastPage = get(page);
            if(lastPage.url.searchParams.get(param) == vStore) return; //attempt to debounce, but won't work beyond primitive types
            let query = new URLSearchParams(lastPage.url.searchParams.toString());
            query.set(param, vStore);
            if(invalidates_fn && invalidates_fn(fnLoad(lastPage.url.searchParams.get(param)), v)) {
                invalidates.forEach(iv => query.delete(iv));
            }
            goto(`${lastPage.url.pathname}?${query.toString()}`,  preventSideEffects && { keepFocus: true, noScroll: true});
        },
        subscribe: store.subscribe,
    }
}

function createIntParam(param, defaultVal=1, preventSideEffects=false, invalidates=[], invalidates_fn=undefined) {
    return createParam(param, defaultVal, (v) => v, parseInt, preventSideEffects, invalidates, invalidates_fn);
}

function createListParam(param, preventSideEffects=false, invalidates=[], invalidates_fn=undefined) {
    return createParam(param, [], (v) => v && v.join(','), (v) => v && v.split(',').map(s => s ? s : undefined), preventSideEffects, invalidates, invalidates_fn);
}

export { createIntParam, createParam, createListParam};
