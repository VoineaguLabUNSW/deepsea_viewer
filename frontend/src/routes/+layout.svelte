<script>
    import './../../node_modules/fontawesome-free/css/all.min.css';
    import '../app.css';

    import { setContext } from 'svelte';
    import { createCore } from '../lib/stores/core.js';

    setContext('core', createCore('https://d33ldq8s2ek4w8.cloudfront.net/crispri/metadata.json'));
</script>

<slot/>
