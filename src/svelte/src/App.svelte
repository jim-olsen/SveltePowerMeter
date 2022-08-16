<script>
    let outerWidth = 0
    let stats = true;
    let graphs = false;
</script>

<svelte:window bind:outerWidth />

<div style="display:flex; flex-flow:row">
    <button class="tabButton" on:click={()=> {stats=true; graphs=false;}}>Stats</button>
    <button class="tabButton" on:click={()=> {stats=false; graphs=true}}>Graphs</button>
</div>
{#if graphs}
{/if}

{#if stats}
{/if}
