
<script>
import Navbar from '../../lib/components/navbar.svelte'
import { Input, Label, Helper, A } from 'flowbite-svelte';
import { getContext } from 'svelte';

let source = getContext('source');
let { metadata } = getContext('core');

</script>

<Navbar/>

<div class="mx-[20%] my-12">
    <p class='text-center'>Simple static heatmap viewer to display Deepsea jobs indefinitely from either local or cloud storage. Double click the main heatmap to re-centre, click anywhere on the miniature overview to jump to a position.</p>
    <div class="my-6">
      <Label for="error" class="block mb-2">Source URL:</Label>
      <Input id="error" color={$metadata?.error && "red"} placeholder="Error input" value={$source} on:blur={(e) => source.set(e.target.value)}/>
      <Helper class="mt-2" color="red">
        {$metadata?.error || ''}
      </Helper>
    </div>
    <p class='text-center'>New source URLs can be created using the simple <A href='https://github.com/VoineaguLabUNSW/deepsea_viewer' target="_blank">pipeline</A>.</p>
</div>
