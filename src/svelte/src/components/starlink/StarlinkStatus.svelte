<script>
    import StarlinkStatusIndicator from "./StarlinkStatusIndicator.svelte";
    import StarlinkObstructionMap from "./StarlinkObstructionMap.svelte";
    import StarlinkFirmwareVersion from "./StarlinkFirmwareVersion.svelte";
    import StarlinkUpTime from "./StarlinkUpTime.svelte";
    import StarlinkAlerts from "./StarlinkAlerts.svelte";
    import {currentView} from "../../stores";

    let obstructionMapWidth, obstructionMapHeight;
</script>

<div style="display:flex; flex-flow: column; justify-content: space-between; width: 100%;" on:click={() => $currentView = 'dashboard'}>
    <div style="display:flex; flex-flow: row; justify-content: space-evenly; align-items: center; flex: 9; gap: 10px;">
        <div style="display:flex; flex-flow: column; justify-content: space-between; gap: 20px" class="card">
            <StarlinkStatusIndicator />
            <div style="display:flex; justify-content: center; flex-flow: column; align-items: center;gap: 10px">
                <span class="smallText"><b>Alerts</b></span>
                <StarlinkAlerts/>
            </div>
        </div>
        <div style="display:flex; justify-content: flex-start; flex-flow: column; align-items: center; gap: 10px; width: 40%;"
             bind:clientWidth={obstructionMapWidth} bind:clientHeight={obstructionMapHeight}>
            <span class="smallText"><b>Obstruction Map</b></span>
            <StarlinkObstructionMap width={Math.min(obstructionMapWidth, obstructionMapHeight)}
                                    height={Math.min(obstructionMapWidth, obstructionMapHeight)}/>
        </div>
    </div>
    <div style="display:flex; flex-flow: row; justify-content: space-around; flex-wrap: wrap; flex: 1;" class="card">
        <StarlinkFirmwareVersion/>
        <StarlinkUpTime/>
    </div>
</div>
