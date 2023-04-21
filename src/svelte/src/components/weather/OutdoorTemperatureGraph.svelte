<script>
    import {onDestroy} from 'svelte'
    import {temperatureGraphData, weatherGraphDuration} from "../../stores";
    import DurationalLineChart from "../d3/DurationalLineChart.svelte";

    export let chartWidth=800
    export let chartHeight=300

    let graphData = [];
    let secondGraphData = [];
    const unsubscribeGraph = temperatureGraphData.subscribe(data => {
        graphData = [];
        secondGraphData = [];
        if (data.hasOwnProperty("time")) {
            data?.time?.forEach((d, i) => {
                let value = data?.outTemp_F?.[i] ? data?.outTemp_F?.[i] : 0;
                graphData.unshift({x: Date.parse(d.slice(0, -4)), y: value})
                value = data?.windchill_F?.[i] ? data?.windchill_F?.[i] : 0;
                secondGraphData.unshift({x: Date.parse(d.slice(0, -4)), y: value})
            })
        }
    });

    onDestroy(unsubscribeGraph);

</script>
<div style="display:flex; flex-flow:row">
    <DurationalLineChart chartHeight={chartHeight} chartWidth={chartWidth}
                         graphData={graphData} additionalGraphData={secondGraphData}
                         duration={weatherGraphDuration} />
</div>