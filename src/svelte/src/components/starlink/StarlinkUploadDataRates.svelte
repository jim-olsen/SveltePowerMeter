<script>
    import {onDestroy} from 'svelte';
    import LineChart from "../d3/LineChart.svelte";
    import {starlinkStatus} from "../../stores";
    import {starlinkGraphHistory} from "../../stores";

    export let chartWidth = 600;
    export let chartHeight = 300;

    let uploadMbps = 0.0
    let uploadMaxMbps = 0.0
    let uploadAvgMbps = 0.0
    let uploadChartData = []

    const unsubscribeStatus = starlinkStatus.subscribe(status => {
        if (status.hasOwnProperty("uplink_throughput_bps")) {
            uploadMbps = (status.uplink_throughput_bps / 1000000).toFixed(2)
        }
    });

    const unsubscribeHistory = starlinkGraphHistory.subscribe(history => {
        if (history.hasOwnProperty("uplink_bps")) {
            uploadChartData = [[]]
            history.uplink_bps.forEach((value, i) => {
                uploadChartData[0].unshift({"x": history.uplink_bps.length - i, "y": value / 1000000})
            });
            uploadMaxMbps = (history.maximum_uplink_bps / 1000000).toFixed(2)
            uploadAvgMbps = (history.average_uplink_bps / 1000000).toFixed(2)
        }
    });

    onDestroy(unsubscribeStatus);
    onDestroy(unsubscribeHistory);
</script>
<div style="display:flex; flex-flow:column; justify-content: flex-start; align-items: center;">
    <span class="mediumSmallText">Upload Speeds</span>
    <div style="display:flex; flex-flow: row; gap:10px">
        <LineChart XAxisTitle="Elapsed Seconds" YAxisTitle="Upload (MBps)" datasets={uploadChartData} width={chartWidth}
               height={chartHeight}/>
        <div style="display:flex; flex-flow: column;justify-content: flex-start;">
            <span class="mediumSmallText">Cur: {uploadMbps}</span>
            <span class="mediumSmallText">Avg: {uploadAvgMbps}</span>
            <span class="mediumSmallText">Max: {uploadMaxMbps}</span>
        </div>
    </div>
</div>
