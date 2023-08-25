<script>
    import {onDestroy} from 'svelte'
    import {group} from "d3"
    import {batteryBankCellVoltageGraphData, powerGraphDuration} from "../../stores";
    import DurationalLineChart from "../d3/DurationalLineChart.svelte";

    export let chartWidth=800
    export let chartHeight=300

    let graphData = [];
    const unsubscribeGraph = batteryBankCellVoltageGraphData.subscribe(data => {
        graphData = [];
        let groupData = [];
        if (data.hasOwnProperty("time")) {
            data?.time?.forEach((d, i) => {
                let cellVoltages = [data.cell_voltage_one[i], data.cell_voltage_two[i], data.cell_voltage_three[i], data.cell_voltage_four[i]];
                let value = (Math.max(...cellVoltages) - Math.min(...cellVoltages)).toFixed(2);
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
    <DurationalLineChart chartHeight={chartHeight} chartWidth={chartWidth} yAxisLabel="Volt Difference"
                         graphDataSets={graphData} duration={powerGraphDuration}/>
</div>