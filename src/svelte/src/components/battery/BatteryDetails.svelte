<script xmlns="http://www.w3.org/1999/html">
    import {batteryCurrentData, currentView} from "../../stores";
    import {onMount} from "svelte";
    import Cell from "./Cell.svelte";

    let battery_name = $currentView.replace('battery_details_', '')
    let battery = {};
    let cells = [];
    let temps = [];
    let status = "Unknown";
    let cycles = 0;
    let protection_status = [];

    onMount(async () => {
        $batteryCurrentData.forEach(batt => { if (batt.name === battery_name) {
            battery = batt;
            cells = battery.cell_block_voltages;
            temps = battery.battery_temps_f;
            status = battery.control_status
            cycles = battery.cycles
        }});
    });

</script>
<div style="display:flex; flex-flow:column; justify-content: space-evenly; align-items: center; width: 100%;" on:click={() => currentView.set('battery_dashboard')}>
    <span class="largeText">{battery_name}</span>
    <div style="display:flex; flex-flow:row wrap; justify-content: space-between; width: 90%;">
        {#each cells as cell_voltage, index}
            <div style="display:flex; flex-flow:column; justify-content: center; align-items: stretch;">
                <Cell voltageIndex={index} battery_name={battery_name} />
                <span class="normalText">{cell_voltage}</span>
            </div>
        {/each}
    </div>
    <div style="display:flex; justify-content: center">
        <div><span class="normalText">Battery Temperatures</span></div>
    </div>
    <div style="display:flex; flex-flow:row wrap; justify-content: space-between; width: 100%;">
        {#each temps as temp}
            <div><span class="normalText">{temp.toFixed(1)} F</span></div>
        {/each}
    </div>
    <div style="display:flex; justify-content: space-between; width: 100%;">
        <div><span class="normalText">Status: {status}</span></div>
        <div><span class="normalText">Cycles: {cycles}</span></div>
    </div>
    <div style="display:flex; flex-flow:row wrap; justify-content: space-between; width: 100%;">
        {#each protection_status as status}
            <div><span class="normalText">{status}</span></div>
        {:else}
            <div><span class="normalText">No Protection Issues</span></div>
        {/each}
    </div>

</div>