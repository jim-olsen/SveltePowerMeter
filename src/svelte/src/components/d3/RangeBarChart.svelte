<script>
    import {scaleLinear} from "d3";
    import Axis from "./Axis.svelte";

    export let XAxisTitle = "";
    export let YAxisTitle = "";
    export let dataset = []; // [{x, yMin, yMax}]
    export let width = 900,
        height = 600,
        barWidth = 80;
    export let minColor = "#5EC6FF";
    export let maxColor = "#FF5C5C";
    export let showMinLabel = true;
    export let unit = "%";
    const margin = { top: 40, bottom: 50, left: 50, right: 20 };

    $: innerHeight = height - margin.top - margin.bottom;
    $: innerWidth = width - margin.left - margin.right;

    $: xScale = scaleLinear()
        .domain([0, dataset.length])
        .range([0, innerWidth])
        .nice();

    $: yScale = scaleLinear()
        .domain([0, Math.max(100, ...dataset.map((d) => d.yMax), 0)])
        .range([innerHeight, 0])
        .nice();
</script>

<main>
    <svg {width} {height}>
        <g class="rangeBarChart" transform={`translate(${margin.left},${margin.top})`}>
            <Axis {innerHeight} {margin} scale={xScale} position="bottom" numTicks={dataset.length - 1}
                  tickFormat={function(d) {if (d < dataset.length && Number.isInteger(d)) return dataset[d].x; else return null;}} />
            <Axis {innerHeight} {margin} scale={yScale} position="left" />
            <text transform={`translate(${-30},${innerHeight / 2}) rotate(-90)`}>{YAxisTitle}</text>
            {#each dataset as point, i}
                {#if showMinLabel}
                    <rect
                        x = "{xScale(i) - (barWidth/2)}"
                        y = "{yScale(point.yMin)}"
                        width = "{barWidth - 4}"
                        height = "{yScale(0) - yScale(point.yMin)}"
                        fill={minColor}></rect>
                {/if}
                <rect
                    x = "{xScale(i) - (barWidth/2)}"
                    y = "{yScale(point.yMax)}"
                    width = "{barWidth - 4}"
                    height = "{yScale(showMinLabel ? point.yMin : 0) - yScale(point.yMax)}"
                    fill={maxColor}></rect>
                <text x={xScale(i)} y={yScale(point.yMax) - 10} text-anchor="middle" class="range-label">{point.yMax}{unit}</text>
                {#if showMinLabel}
                    <text x={xScale(i)} y={yScale(point.yMin) + 26} text-anchor="middle" class="range-label">{point.yMin}{unit}</text>
                {/if}
            {/each}
            <text x={innerWidth / 2} y={innerHeight + 35}>{XAxisTitle}</text>
        </g>
    </svg>
</main>

<style>
    .range-label {
        font-size: 22px;
        font-weight: 700;
        fill: #fca503;
    }
</style>
