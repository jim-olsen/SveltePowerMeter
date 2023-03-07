<script xmlns="http://www.w3.org/1999/html">
    import {onDestroy} from 'svelte'
    import {get} from 'svelte/store'
    import {blueIrisAlert} from "../../stores";

    let currentAlert = get(blueIrisAlert);

    const unsubscribeBlueIris = blueIrisAlert.subscribe(data => {
        currentAlert = data;
    });

    onDestroy(unsubscribeBlueIris)
</script>
<style>
    h2 {
        font-size: 30px;
        color: #fca503;
    }
</style>
<div style="display:flex; flex-flow:column; justify-content: center;">
    {#if currentAlert.hasOwnProperty("alertImage")}
        <h2>Blue Iris Alert on {currentAlert.hasOwnProperty("camera") ? currentAlert.camera : 'None'} {currentAlert.hasOwnProperty("time") ? 'at ' + new Date(currentAlert.time).toLocaleString() : ''}</h2>
        <img src="{'data:image/png;base64, ' + currentAlert.alertImage}" style="height: 85vh;"/>
    {:else}
        <h2>No Current Alerts</h2>
    {/if}
</div>