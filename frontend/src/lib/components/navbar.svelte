<script>
import { page } from '$app/stores';
import { Navbar, NavBrand, NavLi, NavUl, NavHamburger } from 'flowbite-svelte';
import { base } from '$app/paths';

</script>

<Navbar>
  <NavBrand href="{base}/{$page.url.search}"></NavBrand>
  <NavHamburger  />
  <NavUl activeUrl={$page.url.pathname + $page.url.search}>
    <NavLi href="{base}/{$page.url.search}">Viewer</NavLi>
    <NavLi href="{base}/about{$page.url.search}">About</NavLi>
  </NavUl>
</Navbar>
