<script>
    import {onDestroy} from 'svelte'
    import {solarWhGraphData, solarWhGraphDuration} from "../../stores.svelte.js";
    import DurationalRangeBarChart from "../d3/DurationalRangeBarChart.svelte";

    export let chartWidth=800
    export let chartHeight=300

    let graphData = [];
    const unsubscribeGraph = solarWhGraphData.subscribe(data => {
        graphData = [];
        if (data.hasOwnProperty("time")) {
            data.time.forEach((d, i) => {
                graphData.push({
                    x: d,
                    yMin: 0,
                    yMax: data?.solar_wh?.[i] ? Math.round(data.solar_wh[i]) : 0
                });
            });
        }
    });

    onDestroy(unsubscribeGraph);
</script>
<div style="display:flex; flex-flow:row">
    <DurationalRangeBarChart chartHeight={chartHeight} chartWidth={chartWidth} yAxisLabel="Solar Wh"
                             dataset={graphData} duration={solarWhGraphDuration}
                             minColor="#FFD700" maxColor="#FFD700" showMinLabel={false} unit="Wh"/>
</div>
