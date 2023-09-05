<script>
    import {onDestroy} from 'svelte'
    import {group} from "d3"
    import {batteryBankTemperatureGraphData, powerGraphDuration} from "../../stores";
    import DurationalLineChart from "../d3/DurationalLineChart.svelte";

    export let chartWidth=800
    export let chartHeight=300

    let graphData = [];
    const unsubscribeGraph = batteryBankTemperatureGraphData.subscribe(data => {
        graphData = [];
        let groupData = [];
        if (data.hasOwnProperty("time")) {
            data?.time?.forEach((d, i) => {
                let value = data?.battery_temp_two?.[i] ? data?.battery_temp_two?.[i] : 0;
                groupData.unshift({x: Date.parse(d.slice(0, -4)), y: value, name: data?.name?.[i]})
            })
        }
        groupData = group(groupData, d => d.name);
        groupData.forEach(d => {
            graphData.push(d)
        })
    });

    onDestroy(unsubscribeGraph);
</script>
<div style="display:flex; flex-flow:row">
    <DurationalLineChart chartHeight={chartHeight} chartWidth={chartWidth} yAxisLabel="Volts"
                         graphDataSets={graphData} duration={powerGraphDuration}/>
</div>