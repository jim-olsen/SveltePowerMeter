<script>
    import {
        extent,
        scaleLinear,
        line,
        curveBasis,
        curveStep,
        curveLinear,
        curveBundle
    } from "d3";

    import Axis from "./Axis.svelte";

    export let XAxisTitle = "";
    export let YAxisTitle = "";
    export let XAxisTickFormat = null;
    export let datasets = [];
    export let width = 900,
        height = 600;
    export let curveType="curveBasis"

    const margin = { top: 15, bottom: 50, left: 50, right: 20 };
    const color = [
        '#ffffff',
        '#a65628',
        '#e41a1c',
        '#377eb8',
        '#4daf4a',
        '#984ea3',
        '#ffff33',
        '#ff7f00',
        '#f781bf',
        '#999999']

    function concatAllDatasets(dataToConcat) {
        let all_data = [];

        dataToConcat.forEach((dataset) => all_data = all_data.concat(dataset));

        return all_data;
    }

    function getDataSet(values, data) {
        return values;
    }

    $: innerHeight = height - margin.top - margin.bottom;
    $: innerWidth = width - margin.left - margin.right;

    $: xScale = scaleLinear()
        .domain(extent(concatAllDatasets(datasets), (d) => d.x))
        .range([0, innerWidth])
        .nice();

    $: yScale = scaleLinear()
        .domain(extent(concatAllDatasets(datasets), (d) => d.y))
        .range([innerHeight, 0])
        .nice();

    $: line_gen =  values => line()
        .curve(curveType == "curveBasis" ? curveBasis :
            curveType == "curveBundle" ? curveBundle :
                curveType == "curveStep" ? curveStep :
                    curveType == "curveLinear" ? curveLinear:
                        curveBasis)
        .x((d) => xScale(d.x))
        .y((d) => yScale(d.y))(getDataSet(values, datasets));

</script>

<main>
    <svg {width} {height}>
        <g class="lineChart" transform={`translate(${margin.left},${margin.top})`}>
            <Axis {innerHeight} {margin} {width} scale={xScale} position="bottom" tickFormat={XAxisTickFormat}/>
            <Axis {innerHeight} {margin} {width} scale={yScale} position="left" />
            <text transform={`translate(${-30},${innerHeight}) rotate(-90)`}>{YAxisTitle}</text>
            {#each datasets as dataset, i}
                <path d={line_gen(dataset)} style="stroke: {color[i]}"/>
            {/each}
            <text x={innerWidth / 3} y={innerHeight + 35}>{XAxisTitle}</text>
        </g>
    </svg>
</main>

<style>
    path {
        fill: transparent;
        stroke: rgb(18, 153, 90);
        stroke-width: 2.5;
        stroke-linejoin: round;
    }
</style>
