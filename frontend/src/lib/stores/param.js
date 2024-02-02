import { goto } from '$app/navigation';
import { page } from '$app/stores';
import { derived, get } from 'svelte/store';

function createParam(param, defaultVal='', fn=v => v, preventSideEffects=false, invalidates=[]) {
    const store = derived(page, ($page)=> $page && fn($page.url.searchParams.get(param)) || defaultVal, defaultVal)
    return {
        set: v => {
            let lastPage = get(page);
            if(lastPage.url.searchParams.get(param) == v) return; //attempt to debounce, but won't work beyond primitive types
            let query = new URLSearchParams(lastPage.url.searchParams.toString());
            query.set(param, v);
            invalidates.forEach(iv => query.delete(iv))
            goto(`${lastPage.url.pathname}?${query.toString()}`,  preventSideEffects && { keepFocus: true, noScroll: true});
        },
        subscribe: store.subscribe
    }
}

function createIntParam(param, defaultVal=1, preventSideEffects=false, invalidates=[]) {
    return createParam(param, defaultVal, parseInt, preventSideEffects, invalidates);
}

function createListParam(param, preventSideEffects=false, invalidates=[]) {
    return createParam(param, [], (v) => v && v.split(','), preventSideEffects, invalidates);
}

export { createIntParam, createParam, createListParam};
