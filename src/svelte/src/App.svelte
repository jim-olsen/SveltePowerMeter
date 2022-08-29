<script>
    import Statistics from "./components/powermeter/Statistics.svelte";
    import PowerDataFetcher from "./components/powermeter/PowerDataFetcher.svelte";
    import CurrentValues from "./components/powermeter/CurrentValues.svelte";
    import VoltageGraph from "./components/powermeter/VoltageGraph.svelte";
    import SolarWattsGraph from "./components/powermeter/SolarWattsGraph.svelte";
    import BatteryWattsGraph from "./components/powermeter/BatteryWattsGraph.svelte";
    import LoadGraph from "./components/powermeter/LoadGraph.svelte";

    let outerWidth = 0
    let outerHeight = 0
    let stats = true;
    let voltageGraph = false;
    let solarGraph = false;
    let batteryGraph = false;
    let loadGraph = false;
</script>

<svelte:window bind:outerWidth bind:outerHeight/>
<PowerDataFetcher/>
<div style="display: flex; flex-flow: column;">
    {#if voltageGraph}
        <div style="display:flex; flex-flow: column;justify-content: flex-start;">
            <CurrentValues/>
            <div>
                <VoltageGraph chartWidth={(outerWidth - (outerWidth / 10)) } chartHeight={outerHeight * 0.65}/>
            </div>
        </div>
    {/if}

    {#if solarGraph}
        <div style="display:flex; flex-flow: column;justify-content: center;">
            <CurrentValues/>
            <SolarWattsGraph chartWidth={(outerWidth - (outerWidth / 10))} chartHeight={outerHeight * 0.65}/>
        </div>
    {/if}

    {#if stats}
        <div style="display:flex; flex-flow: column;justify-content: center;gap: 10px;">
            <CurrentValues/>
            <Statistics/>
        </div>
    {/if}

    {#if batteryGraph}
        <div style="display:flex; flex-flow: column;justify-content: center; height: 100%;">
            <CurrentValues/>
            <BatteryWattsGraph chartWidth={(outerWidth - (outerWidth / 10))} chartHeight={outerHeight * 0.65}/>
        </div>
    {/if}

    {#if loadGraph}
        <div style="display:flex; flex-flow: column;justify-content: center; height: 100%;">
            <CurrentValues/>
            <LoadGraph chartWidth={(outerWidth - (outerWidth / 10))} chartHeight={outerHeight * 0.65}/>
        </div>
    {/if}

    <div style="display:flex; flex-flow: column; justify-content: flex-end">
    <div style="display:flex; flex-flow:row;justify-content: space-between;">
        <button class="tabButton" on:click={()=> {stats=true; voltageGraph=false;solarGraph=false;batteryGraph=false;loadGraph=false;}}>
            Statistics
        </button>
        <button class="tabButton" on:click={()=> {stats=false; voltageGraph=true;solarGraph=false;batteryGraph=false;loadGraph=false;}}>
            Voltage
        </button>
        <button class="tabButton" on:click={()=> {stats=false; voltageGraph=false;solarGraph=true;batteryGraph=false;loadGraph=false;}}>
            Solar Watts
        </button>
        <button class="tabButton" on:click={()=> {stats=false; voltageGraph=false;solarGraph=false;batteryGraph=true;loadGraph=false;}}>
            Batt Watts
        </button>
        <button class="tabButton" on:click={()=> {stats=false; voltageGraph=false;solarGraph=false;batteryGraph=false;loadGraph=true;}}>
            Load
        </button>
    </div>
    </div>
</div>
