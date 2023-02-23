<script>
    import {onDestroy} from 'svelte'
    import {powerGraphData} from "../../stores";
    import {powerGraphDuration} from "../../stores";
    import LineChart from "../d3/LineChart.svelte";

    export let chartWidth=800
    export let chartHeight=300

    let graphData = [];
    let secondGraphData = [];

    const unsubscribeGraph = powerGraphData.subscribe(data => {
        graphData = [];
        secondGraphData = [];
        if (data.hasOwnProperty("time")) {
            data?.time?.forEach((d, i) => {
                let value = data?.battvoltage?.[i] ? data?.battvoltage?.[i] : 0;
                if ( value != 0 ) {
                    graphData.unshift({x: Date.parse(d.slice(0, -4)), y: value})
                }
                if (data.hasOwnProperty("targetbattvoltage")) {
                    if (data.targetbattvoltage?.[i] == 0) {
                        value = data?.battvoltage?.[i] ? data?.battvoltage?.[i] : 0;
                    } else {
                        value = data?.targetbattvoltage?.[i] ? data?.targetbattvoltage?.[i] : 0;
                    }
                }
                if (value != 0) {
                    secondGraphData.unshift({x: Date.parse(d.slice(0, -4)), y: value})
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
    <LineChart XAxisTitle="Time" YAxisTitle="Volts" dataset={graphData} additionalDataSet={secondGraphData}
           height={chartHeight} width={chartWidth} XAxisTickFormat={formatTime} />
    <div style="display:flex; flex-flow:column">
        <button on:click={()=> {$powerGraphDuration+= 1;}}>&nbsp;&nbsp;+&nbsp;&nbsp;</button>
        <button on:click={()=> {$powerGraphDuration > 1 ? $powerGraphDuration-= 1 : $powerGraphDuration = 1;}}>&nbsp;&nbsp;-&nbsp;&nbsp;</button>
    </div>
</div>