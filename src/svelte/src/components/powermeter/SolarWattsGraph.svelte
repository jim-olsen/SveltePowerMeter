<script>
    import {onDestroy} from 'svelte'
    import {solarWattsGraphData, powerGraphDuration} from "../../stores";
    import DurationalLineChart from "../d3/DurationalLineChart.svelte";

    export let chartWidth=800
    export let chartHeight=300

    let graphData = [];
    const unsubscribeGraph = solarWattsGraphData.subscribe(data => {
        graphData = [[]];
        if (data.hasOwnProperty("time")) {
            data?.time?.forEach((d, i) => {
                let value = data?.solar_watts?.[i] ? data?.solar_watts?.[i] : 0;
                if ( value != 0 ) {
                    graphData[0].unshift({x: Date.parse(d.slice(0, -4)), y: value})
                }
            })
        }
    });

    onDestroy(unsubscribeGraph);
</script>
<div style="display:flex; flex-flow:row">
    <DurationalLineChart chartHeight={chartHeight} chartWidth={chartWidth}
                         graphDataSets={graphData} duration={powerGraphDuration} yAxisLabel="Watts"/>
</div>