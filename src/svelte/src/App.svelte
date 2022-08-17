<script>
    import Statistics from "./components/powermeter/Statistics.svelte";
    import PowerDataFetcher from "./components/powermeter/PowerDataFetcher.svelte";
    import CurrentValues from "./components/powermeter/CurrentValues.svelte";
    import VoltageGraph from "./components/powermeter/VoltageGraph.svelte";

    let outerWidth = 0
    let stats = true;
    let graphs = false;
</script>

<svelte:window bind:outerWidth />
<PowerDataFetcher />

{#if graphs}
    <VoltageGraph />
{/if}

{#if stats}
    <CurrentValues />
    <Statistics />
{/if}
<div style="display:flex; flex-flow:row;justify-content: space-between;">
    <button class="tabButton" on:click={()=> {stats=true; graphs=false;}}>Statistics</button>
    <button class="tabButton" on:click={()=> {stats=false; graphs=true}}>Graphs</button>
</div>
