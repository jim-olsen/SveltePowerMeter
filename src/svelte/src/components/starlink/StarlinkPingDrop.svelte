<script>
    import {onDestroy} from 'svelte';
    import LineChart from "../d3/LineChart.svelte";
    import {starlinkGraphHistory} from "../../stores";

    export let chartWidth = 600;
    export let chartHeight = 300;

    let pingDrop = 0.0;
    let pingDropMax = 0.0;
    let pingDropAvg = 0.0;
    let pingDropChartData = [];

    const unsubscribeHistory = starlinkGraphHistory.subscribe(history => {
        if (history.hasOwnProperty("ping_drop_rate")) {
            pingDropChartData = [[]];
            history.ping_drop_rate.forEach((value, i) => {
                pingDropChartData[0].unshift({"x": history.ping_drop_rate.length - i, "y": (1 - value) * 100});
            });
            pingDropMax = (history.maximum_ping_drop_rate * 100).toFixed(2);
            pingDropAvg = (history.average_ping_drop_rate * 100).toFixed(2);
            pingDrop = (history.ping_drop_rate[0] * 100).toFixed(2);
        }
    });

    onDestroy(unsubscribeHistory);
</script>
<div style="display:flex; flex-flow:column; justify-content: flex-start; align-items: center;">
    <span class="mediumSmallText">Ping Drop Percent</span>
    <div style="display:flex; flex-flow: row;gap: 10px;">
        <LineChart XAxisTitle="Elapsed Seconds" YAxisTitle="Success %" datasets={pingDropChartData} height={chartHeight}
               width={chartWidth}/>
        <div style="display:flex; flex-flow: column; justify-content: flex-start;">
            <span class="mediumSmallerText">Cur: {pingDrop}%</span>
            <span class="mediumSmallerText">Avg: {pingDropAvg}%</span>
            <span class="mediumSmallerText">Max: {pingDropMax}%</span>
        </div>
    </div>
</div>
