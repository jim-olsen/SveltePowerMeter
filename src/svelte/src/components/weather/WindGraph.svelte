<script>
    import {onDestroy} from 'svelte'
    import {windGraphData, weatherGraphDuration} from "../../stores";
    import DurationalLineChart from "../d3/DurationalLineChart.svelte";

    export let chartWidth=800
    export let chartHeight=300

    let graphData = [];

    const unsubscribeGraph = windGraphData.subscribe(data => {
        graphData = [[],[]];
        if (data.hasOwnProperty("time")) {
            data?.time?.forEach((d, i) => {
                let value = data?.wind_average?.[i] ? data?.wind_average?.[i] : 0;
                graphData[0].unshift({x: Date.parse(d.slice(0, -4)), y: value})
                value = data?.windSpeed_mph?.[i] ? data?.windSpeed_mph?.[i] : 0;
                graphData[1].unshift({x: Date.parse(d.slice(0, -4)), y: value})
            })
        }
    });

    onDestroy(unsubscribeGraph);

</script>
<div style="display:flex; flex-flow:row">
    <DurationalLineChart chartHeight={chartHeight} chartWidth={chartWidth} yAxisLabel="Wind MPH"
                         graphDataSets={graphData} duration={weatherGraphDuration} />
</div>