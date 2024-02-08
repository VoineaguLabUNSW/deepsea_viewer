<script>
    import './../../node_modules/fontawesome-free/css/all.min.css';
    import '../app.css';

    import { setContext } from 'svelte';
    import { createCore } from '../lib/stores/core.js';
    import { createParam } from '../lib/stores/param';

    let source = createParam('source', 'https://d33ldq8s2ek4w8.cloudfront.net/crispri/metadata.json');
    setContext('source', source)
    setContext('core', createCore(source));
</script>

<slot/>
