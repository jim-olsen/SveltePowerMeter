<script xmlns="http://www.w3.org/1999/html">
    import {batteryCurrentData, currentView} from "../../stores";

    let battery_overall_percent = 0;

    function getOverallAveragePercent() {
        let percentTotal = 0
        $batteryCurrentData.forEach(battery => percentTotal+=  battery.capacity_percent);

        battery_overall_percent = percentTotal / $batteryCurrentData.length;
    }

    $: $batteryCurrentData, getOverallAveragePercent();
</script>
<div style="display:flex; flex-flow:column; justify-content: center; align-items: center; width: 100%;" on:click={() => currentView.set('dashboard')}>
    <h1>Current Battery Status</h1>
    <h1>Total Percent {battery_overall_percent}%</h1>
    {#each $batteryCurrentData as battery}
        <div style="display:flex; flex-flow: row; justify-content: space-around; width: 100%">
            <div><span>{battery.name}</span></div><div><span>{battery.capacity_percent}%</span></div><div><span>{battery.current}A</span></div>
        </div>
    {/each}
</div>