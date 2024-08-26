<script>
    import {onDestroy} from 'svelte';
    import LineChart from "../d3/LineChart.svelte";
    import {starlinkGraphHistory} from "../../stores";

    export let chartWidth = 600;
    export let chartHeight = 300;

    let powerIn = 0.0;
    let powerInMax = 0.0;
    let powerInMin = 0.0;
    let powerInAvg = 0.0;
    let powerInChartData = [];

    const unsubscribeHistory = starlinkGraphHistory.subscribe(history => {
        if (history.hasOwnProperty("uplink_bps")) {
            powerInChartData = [[]];
            history.power_in.forEach((value, i) => {
                powerInChartData[0].unshift({"x": history.power_in.length - i, "y": value});
            });
            powerInMin = history.minimum_power_in.toFixed(1);
            powerInMax = history.maximum_power_in.toFixed(1);
            powerInAvg = history.average_power_in.toFixed(1);
            powerIn = history.power_in[0]?.toFixed(2);
        }
    });

    onDestroy(unsubscribeHistory);
</script>
<div style="display:flex; flex-flow:column; justify-content: flex-start; align-items: center;">
    <span class="mediumSmallText">Starlink Power In (W)</span>
    <div style="display:flex; flex-flow:row;gap: 10px;">
        <LineChart XAxisTitle="Elapsed Seconds" YAxisTitle="Power (w)" datasets={powerInChartData} width={chartWidth}
               height={chartHeight}/>
        <div style="display:flex; flex-flow:column; justify-content: flex-start">
            <span class="mediumSmallerText">Cur: {powerIn}</span>
            <span class="mediumSmallerText">Avg: {powerInAvg}</span>
            <span class="mediumSmallerText">Min: {powerInMin}</span>
            <span class="mediumSmallerText">Max: {powerInMax}</span>
        </div>
    </div>
</div>
