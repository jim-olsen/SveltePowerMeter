<script>
    import {onDestroy} from 'svelte';
    import LineChart from "../d3/LineChart.svelte";
    import {starlinkGraphHistory} from "../../stores";

    export let chartWidth = 600;
    export let chartHeight = 300;

    let pingLatency = 0.0;
    let pingLatencyMax = 0.0;
    let pingLatencyMin = 0.0;
    let pingLatencyAvg = 0.0;
    let pingLatencyChartData = [];

    const unsubscribeHistory = starlinkGraphHistory.subscribe(history => {
        if (history.hasOwnProperty("ping_latency") && history.ping_latency.length > 0) {
            pingLatencyChartData = [[]];
            history.ping_latency.forEach((value, i) => {
                pingLatencyChartData[0].unshift({"x": history.uplink_bps.length - i, "y": value});
            });
            pingLatencyMin = history.minimum_ping_latency.toFixed(2);
            pingLatencyMax = history.maximum_ping_latency.toFixed(2);
            pingLatencyAvg = history.average_ping_latency.toFixed(2);
            pingLatency = history.ping_latency[0].toFixed(2);
        }
    });

    onDestroy(unsubscribeHistory);
</script>
<div style="display:flex; flex-flow:column; justify-content: flex-start; align-items: center;">
    <span class="mediumSmallText">Ping Latency (ms)</span>
    <div style="display:flex; flex-flow:row;gap: 10px;">
        <LineChart XAxisTitle="Elapsed Seconds" YAxisTitle="Latency (ms)" datasets={pingLatencyChartData} width={chartWidth}
               height={chartHeight}/>
        <div style="display:flex; flex-flow:column; justify-content: flex-start">
            <span class="mediumSmallerText">Cur: {pingLatency}</span>
            <span class="mediumSmallerText">Avg: {pingLatencyAvg}</span>
            <span class="mediumSmallerText">Min: {pingLatencyMin}</span>
            <span class="mediumSmallerText">Max: {pingLatencyMax}</span>
        </div>
    </div>
</div>
