<script xmlns="http://www.w3.org/1999/html">
    import {blueIrisAlert, currentView} from "../../stores";
</script>
<div style="display:flex; flex-flow:column; justify-content: center; align-items: center; width: 100%;" on:click={() => currentView.set('dashboard')}>
    {#if $blueIrisAlert.hasOwnProperty("alertImage")}
        <h2>Blue Iris Alert on {$blueIrisAlert.hasOwnProperty("camera") ? $blueIrisAlert.camera : 'None'} {$blueIrisAlert.hasOwnProperty("time") ? 'at ' + new Date($blueIrisAlert.time).toLocaleString() : ''}</h2>
        <img src="{'data:image/png;base64, ' + $blueIrisAlert.alertImage}" style="height: 85vh;"/>
    {:else}
        <h2>No Current Alerts</h2>
    {/if}
</div>