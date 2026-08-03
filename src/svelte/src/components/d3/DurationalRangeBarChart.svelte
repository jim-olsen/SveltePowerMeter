<script>
    import Fa from "svelte-fa";
    import {faChevronDown, faChevronUp} from "@fortawesome/free-solid-svg-icons";
    import RangeBarChart from "./RangeBarChart.svelte";

    export let chartWidth = 800;
    export let chartHeight = 300;
    export let duration = 1;
    export let dataset = [];
    export let yAxisLabel = '';
    export let minColor = "#5EC6FF";
    export let maxColor = "#FF5C5C";
    export let showMinLabel = true;
    export let unit = "%";
    export let valueFormat = (v) => v;
    export let signed = false;

    let buttonWidth = 0;

    function handleKeyDown(event) {
        if (!event.repeat) {
            switch(event.key) {
                case "-":
                case "_":
                    decreaseDuration();
                    break;
                case "+":
                case "=":
                    increaseDuration();
                    break;
            }
        }
    }

    function decreaseDuration() {
        dataset = [];
        $duration > 1 ? $duration-= 1 : $duration = 1;
    }

    function increaseDuration() {
        dataset = [];
        $duration+= 1;
    }

</script>
<svelte:window on:keydown={handleKeyDown}/>
<div style="display:flex; flex-flow:row">
    <RangeBarChart XAxisTitle="Day" YAxisTitle={yAxisLabel} dataset={dataset}
               height={chartHeight} width={chartWidth - buttonWidth}
               minColor={minColor} maxColor={maxColor} showMinLabel={showMinLabel} unit={unit}
               valueFormat={valueFormat} signed={signed}/>
    <div style="display:flex; flex-flow:column" bind:clientWidth={buttonWidth}>
        <button on:click={increaseDuration} style="width:8vw; height: 8vw;">
            <Fa icon={faChevronUp} style="font-size: 4vw;" />
        </button>
        <button on:click={decreaseDuration}
                style="width:8vw; height: 8vw;">
            <Fa icon={faChevronDown} style="font-size: 4vw;"/>
        </button>
    </div>
</div>
