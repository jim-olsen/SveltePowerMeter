<script>
    import {onDestroy} from 'svelte'
    import {powerGraphData} from "../../stores";
    import LineChart from "../d3/LineChart.svelte";

    export let chartWidth=800
    export let chartHeight=300

    let graphData = [];

    const unsubscribeGraph = powerGraphData.subscribe(data => {
        graphData = [];
        if (data.hasOwnProperty("time")) {
            data?.time?.forEach((d, i) => {
                graphData.push({x: Date.parse(d), y: data?.battvoltage?.[i] ? data?.battvoltage?.[i] : 0 })
            })
        }
    });

    onDestroy(unsubscribeGraph);

    function formatTime(timeVal, index) {
        return new Intl.DateTimeFormat( 'en-US', { month: 'numeric', day: 'numeric', hour: 'numeric', minute: 'numeric'})
            .format(new Date(timeVal));
    }

</script>
<LineChart XAxisTitle="Time" YAxisTitle="Volts" dataset={graphData} height={chartHeight} width={chartWidth} XAxisTickFormat={formatTime} />