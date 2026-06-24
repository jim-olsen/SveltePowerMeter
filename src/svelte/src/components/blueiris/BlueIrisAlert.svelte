<script>
    import {blueIrisAlert} from "../../stores.svelte.js";
    import {currentView} from "../../states.svelte.js";
</script>
<div role="button" tabindex="0" style="display:flex; flex-flow:column; justify-content: center; align-items: center; width: 100%;" on:click={() => currentView.value = 'dashboard'} on:keydown={(event) => {if (event.key === 'Enter' || event.key === ' ') currentView.value = 'dashboard'}}>
    {#if $blueIrisAlert.hasOwnProperty("alertImage")}
        <h2>Blue Iris Alert on {$blueIrisAlert.hasOwnProperty("camera") ? $blueIrisAlert.camera : 'None'} {$blueIrisAlert.hasOwnProperty("time") ? 'at ' + new Date($blueIrisAlert.time).toLocaleString() : ''}</h2>
        <img src="{'data:image/png;base64, ' + $blueIrisAlert.alertImage}" alt="Blue Iris alert snapshot" style="height: 85vh;"/>
    {:else}
        <h2>No Current Alerts</h2>
    {/if}
</div>


