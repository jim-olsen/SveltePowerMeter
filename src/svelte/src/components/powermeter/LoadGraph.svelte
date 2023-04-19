<script>
    import {onDestroy} from 'svelte'
    import {loadWattsGraphData} from "../../stores";
    import {powerGraphDuration} from "../../stores";
    import LineChart from "../d3/LineChart.svelte";

    export let chartWidth=800
    export let chartHeight=300

    let graphData = [];

    const unsubscribeGraph = loadWattsGraphData.subscribe(data => {
        graphData = [];
        if (data.hasOwnProperty("time")) {
            data?.time?.forEach((d, i) => {
                let value = data?.load_watts?.[i] ? data?.load_watts?.[i] : 0;
                if ( value != 0 ) {
                    graphData.unshift({x: Date.parse(d.slice(0, -4)), y: value})
                }
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
                    $powerGraphDuration > 1 ? $powerGraphDuration-= 1 : $powerGraphDuration = 1;
                    break;
                case "s":
                    $powerGraphDuration+= 1;
                    break;
            }
        }
    }

</script>
<svelte:window on:keydown={handleKeyDown}/>
<div style="display:flex; flex-flow:row">
    <LineChart XAxisTitle="Time" YAxisTitle="Battery Load" dataset={graphData}
           height={chartHeight} width={chartWidth} XAxisTickFormat={formatTime} />
    <div style="display:flex; flex-flow:column">
        <button on:click={()=> {$powerGraphDuration+= 1;}}>&nbsp;&nbsp;+&nbsp;&nbsp;</button>
        <button on:click={()=> {$powerGraphDuration > 1 ? $powerGraphDuration-= 1 : $powerGraphDuration = 1;}}>&nbsp;&nbsp;-&nbsp;&nbsp;</button>
    </div>
</div>