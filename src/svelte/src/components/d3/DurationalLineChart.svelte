<script>
    import Fa from "svelte-fa";
    import {faChevronDown, faChevronUp} from "@fortawesome/free-solid-svg-icons";
    import LineChart from "./LineChart.svelte";

    export let chartWidth = 800;
    export let chartHeight = 300;
    export let duration = 1;
    export let graphData = [];
    export let additionalGraphData = [];
    export let yAxisLabel = '';

    let buttonWidth = 0;

    function formatTime(timeVal, index) {
        return new Intl.DateTimeFormat( 'en-US', { month: 'numeric', day: 'numeric', hour: 'numeric', minute: 'numeric'})
            .format(new Date(timeVal));
    }

    function handleKeyDown(event) {
        if (!event.repeat) {
            switch(event.key) {
                case "a":
                    decreaseDuration();
                    break;
                case "s":
                    increaseDuration();
                    break;
            }
        }
    }

    function decreaseDuration() {
        graphData = [];
        additionalGraphData = [];
        $duration > 1 ? $duration-= 1 : $duration = 1;
    }

    function increaseDuration() {
        graphData = [];
        additionalGraphData = [];
        $duration+= 1;
    }

</script>
<div style="display:flex; flex-flow:row">
    <LineChart XAxisTitle="Time" YAxisTitle={yAxisLabel} dataset={graphData} additionalDataSet={additionalGraphData}
               height={chartHeight} width={chartWidth - buttonWidth} XAxisTickFormat={formatTime} />
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