<script xmlns="http://www.w3.org/1999/html">
    import {batteryCurrentData, currentView} from "../../stores";
    import Battery from "./Battery.svelte";

    let battery_overall_percent = 0;

    function getOverallAveragePercent() {
        let percentTotal = 0
        $batteryCurrentData.forEach(battery => percentTotal+=  battery.capacity_percent);

        battery_overall_percent = percentTotal / $batteryCurrentData.length;
    }

    $: $batteryCurrentData, getOverallAveragePercent();
</script>
<div style="display:flex; flex-flow:column; justify-content: flex-start; align-items: center; width: 100%;" on:click={() => currentView.set('dashboard')}>
    <span class="largeText">Total Percent {battery_overall_percent.toFixed(2)}%</span>
    {#each $batteryCurrentData as battery}
        <div style="display:flex; flex-flow: row; justify-content: space-around; align-items: center; width: 100%" on:click={() => currentView.set('battery_details_' + battery.name)}>
            <div style="display:flex; flex-grow: 1; width: 100%;"><span class="mediumSmallText" style="width:100%;">{battery.name}</span></div>
            <div style="display:flex; flex-grow: 1; width: 100%;" on:click={() => currentView.set('batteryBankTemperatureGraph')}><span class="normalText" style="width:100%; text-align: center;">{battery.capacity_percent}%</span></div>
            <div style="display:flex; flex-grow: 1; width: 100%;" on:click={() => currentView.set('batteryBankVoltageGraph')}><span class="normalText">{battery.voltage.toFixed(2)}</span></div>
            <div style="display:flex; flex-grow: 1; width: 100%;" on:click={() => currentView.set('batteryCellPressureGraph')}><span class="normalText">{battery.current}A</span></div>
            <div style="display:flex; flex-grow: 1; width: 100%;" on:click={() => currentView.set('battery_cell_graph_' + battery.name)}>
                <Battery battery="{battery}"/>
            </div>
        </div>
    {/each}
</div>