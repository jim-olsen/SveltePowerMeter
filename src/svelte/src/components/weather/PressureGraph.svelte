<script>
    import {onDestroy} from 'svelte'
    import {pressureGraphData, weatherGraphDuration} from "../../stores";
    import DurationalLineChart from "../d3/DurationalLineChart.svelte";

    export let chartWidth = 800
    export let chartHeight = 300

    let graphData = [];
    const unsubscribeGraph = pressureGraphData.subscribe(data => {
        graphData = [];
        if (data.hasOwnProperty("time")) {
            data?.time?.forEach((d, i) => {
                let value = data?.pressure_inHg?.[i] ? data?.pressure_inHg?.[i] : 0;
                graphData.unshift({x: Date.parse(d.slice(0, -4)), y: value})
            })
        }
    });

    onDestroy(unsubscribeGraph);

</script>
<div style="display:flex; flex-flow:row">
    <DurationalLineChart chartHeight={chartHeight} chartWidth={chartWidth} yAxisLabel="in Hg"
                         graphData={graphData} duration={weatherGraphDuration} />
</div>