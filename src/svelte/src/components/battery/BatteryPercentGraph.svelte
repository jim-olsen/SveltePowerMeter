<script>
    import {onDestroy} from 'svelte'
    import {batteryPercentMinMaxGraphData, batteryPercentGraphDuration} from "../../stores.svelte.js";
    import DurationalRangeBarChart from "../d3/DurationalRangeBarChart.svelte";

    export let chartWidth=800
    export let chartHeight=300

    let graphData = [];
    const unsubscribeGraph = batteryPercentMinMaxGraphData.subscribe(data => {
        graphData = [];
        if (data.hasOwnProperty("time")) {
            data.time.forEach((d, i) => {
                graphData.push({
                    x: d,
                    yMin: data?.min_percent?.[i] ? data.min_percent[i] : 0,
                    yMax: data?.max_percent?.[i] ? data.max_percent[i] : 0
                });
            });
        }
    });

    onDestroy(unsubscribeGraph);
</script>
<div style="display:flex; flex-flow:row">
    <DurationalRangeBarChart chartHeight={chartHeight} chartWidth={chartWidth} yAxisLabel="Battery %"
                             dataset={graphData} duration={batteryPercentGraphDuration}
                             minColor="#8B0000" maxColor="#7CFF9A"
                             valueFormat={(v) => Number(v).toFixed(1)}/>
</div>
