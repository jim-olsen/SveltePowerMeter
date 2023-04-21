<script>
    import {onDestroy} from 'svelte'
    import {batteryVoltageGraphData, powerGraphDuration} from "../../stores";
    import DurationalLineChart from "../d3/DurationalLineChart.svelte";

    export let chartWidth=800
    export let chartHeight=300

    let graphData = [];
    let secondGraphData = [];
    const unsubscribeGraph = batteryVoltageGraphData.subscribe(data => {
        graphData = [];
        secondGraphData = [];
        if (data.hasOwnProperty("time")) {
            data?.time?.forEach((d, i) => {
                let value = data?.battery_voltage?.[i] ? data?.battery_voltage?.[i] : 0;
                if ( value != 0 ) {
                    graphData.unshift({x: Date.parse(d.slice(0, -4)), y: value})
                }
                if (data.hasOwnProperty("target_regulation_voltage")) {
                    if (data.target_regulation_voltage?.[i] == 0) {
                        value = data?.battery_voltage?.[i] ? data?.battery_voltage?.[i] : 0;
                    } else {
                        value = data?.target_regulation_voltage?.[i] ? data?.target_regulation_voltage?.[i] : 0;
                    }
                }
                if (value != 0) {
                    secondGraphData.unshift({x: Date.parse(d.slice(0, -4)), y: value})
                }
            })
        }
    });

    onDestroy(unsubscribeGraph);
</script>
<div style="display:flex; flex-flow:row">
    <DurationalLineChart chartHeight={chartHeight} chartWidth={chartWidth}
                         graphData={graphData} additionalGraphData={secondGraphData} duration={powerGraphDuration} />
</div>