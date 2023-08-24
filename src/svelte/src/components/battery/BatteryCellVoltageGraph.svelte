<script>
    import {onDestroy} from 'svelte'
    import {currentView, powerGraphDuration} from "../../stores";
    import DurationalLineChart from "../d3/DurationalLineChart.svelte";
    import {get} from "svelte/store";

    export let chartWidth=800
    export let chartHeight=300

    let battery_name = $currentView.replace('battery_cell_graph_', '')
    let graphData = [];
    let graphInterval;
    let titleHeight = 0;

    function updateGraphData() {
        fetch(`/graphBatteryData?days=${get(powerGraphDuration)}&dataField=cell_voltage_one&dataField=cell_voltage_two&dataField=cell_voltage_three&dataField=cell_voltage_four&battery_name=` + battery_name, {
            headers: {
                "Accept": "application/json"
            }
        })
            .then(d => d.json())
            .then(data => {
                if (data.hasOwnProperty("time")) {
                    graphData = [[], [], [], []];
                    data?.time?.forEach((d, i) => {
                        // Reduce the amount of data based on the duration as there are many data points
                        if (i % ($powerGraphDuration * 20) == 0) {
                            graphData[0].unshift({
                                x: Date.parse(d.slice(0, -4)),
                                y: data?.cell_voltage_one?.[i] ? data?.cell_voltage_one?.[i] : 0
                            });
                            graphData[1].unshift({
                                x: Date.parse(d.slice(0, -4)),
                                y: data?.cell_voltage_two?.[i] ? data?.cell_voltage_two?.[i] : 0
                            })
                            graphData[2].unshift({
                                x: Date.parse(d.slice(0, -4)),
                                y: data?.cell_voltage_three?.[i] ? data?.cell_voltage_three?.[i] : 0
                            })
                            graphData[3].unshift({
                                x: Date.parse(d.slice(0, -4)),
                                y: data?.cell_voltage_four?.[i] ? data?.cell_voltage_four?.[i] : 0
                            })
                        }
                    })
                }
            })
    }



    $: {
        updateGraphData();
        clearInterval(graphInterval)
        graphInterval = setInterval(updateGraphData, 30000)
    }

    $: $powerGraphDuration && updateGraphData()

    onDestroy(() => { clearInterval(graphInterval)});
</script>
<div bind:clientWidth={chartWidth} bind:clientHeight={chartHeight}
     style="display:flex; flex-flow:column; justify-content: center; align-items: center; width: 100%;">
    <div on:click={() => currentView.set('battery_dashboard')}  bind:clientHeight={titleHeight} ><span class="normalText">{battery_name} Cell Voltages</span></div>
    <DurationalLineChart chartHeight={chartHeight - (titleHeight + (titleHeight * 0.1))} chartWidth={chartWidth - (chartWidth * 0.03)} yAxisLabel="Volts"
                         graphDataSets={graphData} duration={powerGraphDuration} curveType="curveBundle"/>
</div>