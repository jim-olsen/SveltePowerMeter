<script>
    import {onDestroy} from 'svelte'
    import {windGraphData} from "../../stores";
    import {weatherGraphDuration} from "../../stores";
    import LineChart from "../d3/LineChart.svelte";

    export let chartWidth=800
    export let chartHeight=300

    let graphData = [];
    let secondGraphData = [];

    const unsubscribeGraph = windGraphData.subscribe(data => {
        graphData = [];
        secondGraphData = [];
        if (data.hasOwnProperty("time")) {
            data?.time?.forEach((d, i) => {
                let value = data?.wind_average?.[i] ? data?.wind_average?.[i] : 0;
                graphData.unshift({x: Date.parse(d.slice(0, -4)), y: value})
                value = data?.windSpeed_mph?.[i] ? data?.windSpeed_mph?.[i] : 0;
                secondGraphData.unshift({x: Date.parse(d.slice(0, -4)), y: value})
            })
        }
    });

    onDestroy(unsubscribeGraph);

    function formatTime(timeVal, index) {
        return new Intl.DateTimeFormat( 'en-US', { month: 'numeric', day: 'numeric', hour: 'numeric', minute: 'numeric'})
            .format(new Date(timeVal));
    }

    function handleKeyDown(event) {
        if (!event.repeat) {
            switch(event.key) {
                case "a":
                    $weatherGraphDuration > 1 ? $weatherGraphDuration-= 1 : $weatherGraphDuration = 1;
                    break;
                case "s":
                    $weatherGraphDuration+= 1;
                    break;
            }
        }
    }
</script>
<svelte:window on:keydown={handleKeyDown}/>
<div style="display:flex; flex-flow:row">
    <LineChart XAxisTitle="Time" YAxisTitle="Wind MPH" dataset={graphData} additionalDataSet={secondGraphData}
           height={chartHeight} width={chartWidth} XAxisTickFormat={formatTime} />
    <div style="display:flex; flex-flow:column">
        <button on:click={()=> {$weatherGraphDuration+= 1;}}>&nbsp;&nbsp;+&nbsp;&nbsp;</button>
        <button on:click={()=> {$weatherGraphDuration > 1 ? $weatherGraphDuration-= 1 : $weatherGraphDuration = 1;}}>&nbsp;&nbsp;-&nbsp;&nbsp;</button>
    </div>
</div>