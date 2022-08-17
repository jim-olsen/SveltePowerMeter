<script>
    import { select } from "d3-selection";
    import { axisBottom, axisLeft } from "d3-axis";

    export let innerHeight;
    export let margin;
    export let width;
    export let position;
    export let scale;
    export let tickFormat = null;
    export let numTicks = null;

    let transform;
    let g;

    $: {
        select(g).selectAll("*").remove();

        let axis;
        switch (position) {
            case "bottom":
                axis = axisBottom(scale)
                    .tickSizeOuter(0)
                if (tickFormat != null) {
                    axis = axis.tickFormat(tickFormat)
                }
                if (numTicks != null) {
                    axis = axis.ticks(numTicks)
                }
                transform = `translate(0, ${innerHeight})`;
                break;
            case "left":
                axis = axisLeft(scale).tickSizeInner(-width);
                if (tickFormat != null) {
                    axis = axis.tickFormat(tickFormat)
                }
                if (numTicks != null) {
                    axis = axis.ticks(numTicks)
                }
                transform = `translate(${margin}, 0)`;
        }

        select(g).call(axis);
        select(g).selectAll(".tick line").attr("stroke-dasharray", "10, 10");
    }
</script>

<g class="axis" bind:this={g} {transform} />
