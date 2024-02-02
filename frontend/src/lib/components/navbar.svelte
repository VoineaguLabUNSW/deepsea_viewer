<script>
import { page } from '$app/stores';
import { Navbar, NavBrand, NavLi, NavUl, NavHamburger } from 'flowbite-svelte';
import { base } from '$app/paths';
</script>

<Navbar>
  <NavBrand href="/">
      <svg class="w-6 h-6 text-gray-800 dark:text-white" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" fill="currentColor" viewBox="0 0 24 24">
          <path fill-rule="evenodd" d="M20 10H4v8a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-8ZM9 13v-1h6v1c0 .6-.4 1-1 1h-4a1 1 0 0 1-1-1Z" clip-rule="evenodd"/>
          <path d="M2 6c0-1.1.9-2 2-2h16a2 2 0 1 1 0 4H4a2 2 0 0 1-2-2Z"/>
        </svg>
    <span class="self-center whitespace-nowrap text-xl font-semibold dark:text-white">Deepsea Archive Viewer</span>
  </NavBrand>
  <NavHamburger  />
  <NavUl activeUrl={$page.url.pathname}>
    <NavLi href="{base}/">Viewer</NavLi>
    <NavLi href="{base}/about">About</NavLi>
  </NavUl>
</Navbar>
