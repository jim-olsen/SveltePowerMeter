<script>
    import StarlinkStatusIndicator from "./StarlinkStatusIndicator.svelte";
    import StarlinkObstructionMap from "./StarlinkObstructionMap.svelte";
    import StarlinkFirmwareVersion from "./StarlinkFirmwareVersion.svelte";
    import StarlinkUpTime from "./StarlinkUpTime.svelte";
    import StarlinkAlerts from "./StarlinkAlerts.svelte";
    import {currentView} from "../../stores";
    import StarlinkAntenna from "./StarlinkAntenna.svelte";

    let displayAntenna = false;

    let obstructionMapWidth, obstructionMapHeight;
    let outerHeight, outerWidth;
</script>

<div style="display:flex; flex-flow: column; justify-content: space-between; width: 100%;">
    <div style="display:flex; flex-flow: row; justify-content: space-evenly; align-items: center; flex: 9; gap: 10px;"
         on:click|self={() => $currentView = 'dashboard'}>
        <div on:click={() => $currentView = 'dashboard'} style="display:flex; flex-flow: column; justify-content: space-between; gap: 20px" class="card"
             bind:clientHeight={outerHeight} bind:clientWidth={outerWidth}>
            <StarlinkStatusIndicator />
            <div style="display:flex; justify-content: center; flex-flow: column; align-items: center;gap: 10px">
                <span class="smallText"><b>Alerts</b></span>
                <StarlinkAlerts/>
            </div>
        </div>
        {#if displayAntenna}
            <div on:click={()=> displayAntenna = !displayAntenna}
                 style="display:flex; justify-content: center; flex-flow: column; align-items: center; gap: 10px; width: 40%;">
                <span class="smallText"><b>Antenna Orientation</b></span>
                <StarlinkAntenna chartHeight={Math.min(outerWidth / 2, outerHeight / 2)}/>
            </div>
        {:else}
            <div on:click={()=> displayAntenna = !displayAntenna} style="display:flex; justify-content: flex-start; flex-flow: column; align-items: center; gap: 10px; width: 40%;"
             bind:clientWidth={obstructionMapWidth} bind:clientHeight={obstructionMapHeight}>
                <span class="smallText"><b>Obstruction Map</b></span>
                <div style="width: 100%;">
                    <StarlinkObstructionMap width={Math.min(outerWidth, outerHeight)}
                                    height={Math.min(outerWidth, outerHeight)}/>
                </div>
            </div>
        {/if}

    </div>
    <div on:click|self={() => $currentView = 'dashboard'}
         style="display:flex; flex-flow: row; justify-content: space-around; flex-wrap: wrap; flex: 1;" class="card">
        <StarlinkFirmwareVersion/>
        <StarlinkUpTime/>
    </div>
</div>
