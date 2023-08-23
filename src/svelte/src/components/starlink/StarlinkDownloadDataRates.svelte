<script>
    import LineChart from "../d3/LineChart.svelte";
    import {starlinkGraphHistory, starlinkStatus} from "../../stores";
    import {onDestroy} from "svelte";

    export let chartWidth = 600;
    export let chartHeight = 300;

    let downloadMbps = 0.0
    let downloadMaxMbps = 0.0
    let downloadAvgMbps = 0.0
    let downloadChartData = []

    const unsubscribeStatus = starlinkStatus.subscribe(status => {
        if (status.hasOwnProperty("downlink_throughput_bps")) {
            downloadMbps = (status.downlink_throughput_bps / 1000000).toFixed(2)
        }
    });

    const unsubscribeHistory = starlinkGraphHistory.subscribe(history => {
        if (history.hasOwnProperty("downlink_bps")) {
            downloadChartData = [[]]
            history.downlink_bps.forEach((value, i) => {
                downloadChartData[0].unshift({"x": history.uplink_bps.length - i, "y": value / 1000000})
            });
            downloadMaxMbps = (history.maximum_downlink_bps / 1000000).toFixed(2)
            downloadAvgMbps = (history.average_downlink_bps / 1000000).toFixed(2)
        }
    });

    onDestroy(unsubscribeStatus);
    onDestroy(unsubscribeHistory);
</script>
<div style="display:flex; flex-flow:column; justify-content: flex-start; align-items: center;">
    <span class="mediumSmallText">Download Speeds</span>
    <div style="display: flex; flex-flow: row; gap:10px;">
        <LineChart XAxisTitle="Elapsed Seconds" YAxisTitle="Download (MBps)" datasets={downloadChartData} width={chartWidth}
               height={chartHeight}/>
        <div style="display: flex; flex-flow: column; justify-content: flex-start;">
            <span class="mediumSmallText">Cur: {downloadMbps}</span>
            <span class="mediumSmallText">Avg: {downloadAvgMbps}</span>
            <span class="mediumSmallText">Max: {downloadMaxMbps}</span>
        </div>
    </div>
</div>
