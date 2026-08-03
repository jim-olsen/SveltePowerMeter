<script>
    import {onDestroy} from 'svelte'
    import {batteryWhGraphData, batteryWhGraphDuration} from "../../stores.svelte.js";
    import DurationalRangeBarChart from "../d3/DurationalRangeBarChart.svelte";

    export let chartWidth=800
    export let chartHeight=300

    let graphData = [];
    const unsubscribeGraph = batteryWhGraphData.subscribe(data => {
        graphData = [];
        if (data.hasOwnProperty("time")) {
            data.time.forEach((d, i) => {
                let value = data?.batt_wh?.[i] ? Math.round(data.batt_wh[i]) : 0;
                graphData.push({
                    x: d,
                    yMin: Math.min(0, value),
                    yMax: Math.max(0, value)
                });
            });
        }
    });

    onDestroy(unsubscribeGraph);
</script>
<div style="display:flex; flex-flow:row">
    <DurationalRangeBarChart chartHeight={chartHeight} chartWidth={chartWidth} yAxisLabel="Batt Wh"
                             dataset={graphData} duration={batteryWhGraphDuration}
                             minColor="#FF5C5C" maxColor="#7CFF9A" showMinLabel={false} unit="Wh"/>
</div>
