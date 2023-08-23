<script>
    import {onDestroy} from 'svelte'
    import {humidityGraphData, weatherGraphDuration} from "../../stores";
    import DurationalLineChart from "../d3/DurationalLineChart.svelte";

    export let chartWidth = 800;
    export let chartHeight = 300;

    let graphData = [];
    const unsubscribeGraph = humidityGraphData.subscribe(data => {
        graphData = [[]];
        if (data.hasOwnProperty("time")) {
            data?.time?.forEach((d, i) => {
                let value = data?.outHumidity?.[i] ? data?.outHumidity?.[i] : 0;
                graphData[0].unshift({x: Date.parse(d.slice(0, -4)), y: value})
            })
        }
    });

    onDestroy(unsubscribeGraph);

</script>
<div style="display:flex; flex-flow:row">
    <DurationalLineChart chartHeight={chartHeight} chartWidth={chartWidth} yAxisLabel="Humidity %"
                         graphDataSets={graphData} duration={weatherGraphDuration} />
</div>