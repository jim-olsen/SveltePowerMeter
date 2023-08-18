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
<div style="display:flex; flex-flow:column; justify-content: space-evenly; align-items: center; width: 100%;" on:click={() => currentView.set('dashboard')}>
    <h1>Total Percent {battery_overall_percent}%</h1>
    {#each $batteryCurrentData as battery}
        <div style="display:flex; flex-flow: row; justify-content: space-around; width: 100%">
            <div style="display:flex; flex-grow: 1; width: 100%;"><span>{battery.name}</span></div>
            <div style="display:flex; flex-grow: 1; width: 100%;"><span>{battery.capacity_percent}%</span></div>
            <div style="display:flex; flex-grow: 1; width: 100%;"><span>{battery.current}A</span></div>
            <div style="display:flex; flex-grow: 1; width: 100%;">
                <Battery battery="{battery}" height=50 />
            </div>
        </div>
    {/each}
</div>