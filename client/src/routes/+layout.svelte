<script lang="ts">
    import "../app.css";
    import favicon from "$lib/assets/favicon.ico";

    let { children } = $props();

    import { SvelteToast } from "@zerodevx/svelte-toast";

    const options = {
        duration: 3000,
        position: "top-right",
        dismissable: true,
    };
</script>

<svelte:head>
    <link rel="icon" href={favicon} />
    <title>Draw2Route</title>
</svelte:head>

<SvelteToast {options} />

{@render children?.()}
