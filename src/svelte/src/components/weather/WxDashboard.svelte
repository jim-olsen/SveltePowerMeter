<script>
    import {currentView, weatherData} from "../../stores";
    import Fa from "svelte-fa";
    import {faArrowLeftLong} from "@fortawesome/free-solid-svg-icons";
    import WindDisplay from "./WindDisplay.svelte";
    import Thermometer from "./Thermometer.svelte";
    import OutdoorTemperatureGraph from "./OutdoorTemperatureGraph.svelte";
    import IndoorTemperatureGraph from "./IndoorTemperatureGraph.svelte";
    import PressureGraph from "./PressureGraph.svelte";
    import HumidityGraph from "./HumidityGraph.svelte";

    let wxHeight = 0, wxWidth = 0, headerHeight = 0;
    let display = 'dashboard';

</script>
<div style="display:flex; flex-flow: column; width: 100%; height: 100%;" bind:clientHeight={wxHeight} bind:clientWidth={wxWidth}>
{#if display === 'dashboard'}
    <div style="display:flex; flex-flow: row; justify-content: center; align-content: center; width: 100%; gap: 10px;"
        on:click|self={() => $currentView = 'dashboard'}>
        <div on:click={() => $currentView = 'dashboard'} class="card" style="flex: 1; height: {Math.min(wxHeight, wxWidth * 0.5)}px; aspect-ratio: 1 / 1;">
            <WindDisplay diameter={Math.min(wxHeight, wxWidth)}></WindDisplay>
        </div>
        <div on:click|self={() => $currentView = 'dashboard'} style="display:flex; flex-flow: column; justify-content: space-between; flex: 9; gap: 20px; height: 96%;">
            <div on:click|self={() => $currentView = 'dashboard'} class="card" style="display:flex; flex-flow: row; justify-content: space-evenly; align-items: stretch;">
                <div on:click={() => display = 'outtemp'}>
                    <Thermometer temperatureField="outTemp_F" temperatureMaxField="outTemp_F_max" temperatureMinField="outTemp_F_min" title="Outside" height="200"></Thermometer>
                </div>
                <div on:click={() => display = 'outtemp'}>
                    <Thermometer temperatureField="windchill_F" temperatureMinField="windchill_F_min" temperatureMaxField="windchill_F_max" title="Windchill" height="200"></Thermometer>
                </div>
                <div on:click={() => display = 'intemp'}>
                    <Thermometer temperatureField="inTemp_F" temperatureMinField="inTemp_F_min" temperatureMaxField="inTemp_F_max" title="Inside" height="200"></Thermometer>
                </div>
            </div>
            <div style="display:flex; flex-flow: row wrap; justify-content: flex-start; row-gap: 20px; column-gap: 10px;">
                <div on:click={() => display = 'pressure'} class="card" style="display:flex; flex-flow:column; justify-content: center; align-items: center; flex: 1">
                    <span class="mediumSmallText" style="white-space: nowrap;">Pressure</span>
                    <span class="mediumSmallText" style="white-space: nowrap;">{$weatherData?.barometer_inHg ? Number($weatherData?.barometer_inHg).toFixed(2) + " inHg" : "--- inHg"}</span>
                </div>
                <div on:click={() => display = 'humidity'} class="card" style="display:flex; flex-flow:column; justify-content: center; align-items: center; flex: 1">
                    <span class="mediumSmallText" style="white-space: nowrap;">Humidity</span>
                    <span class="mediumSmallText" style="white-space: nowrap;">{$weatherData?.outHumidity ? Number($weatherData?.outHumidity).toFixed(1) + " %" : "--- %"}</span>
                </div>
                <div on:click={() => $currentView = 'dashboard'} class="card" style="display:flex; flex-flow:column; justify-content: center; align-items: center; flex: 1">
                    <span class="mediumSmallText" style="white-space: nowrap;">Rain</span>
                    <span class="mediumSmallText" style="white-space: nowrap;">{$weatherData?.dayRain_in ? Number($weatherData?.dayRain_in).toFixed(1) + " in" : "--- in"}</span>
                </div>
                <div on:click={() => $currentView = 'dashboard'} class="card" style="display:flex; flex-flow:column; justify-content: center; align-items: center; flex: 1">
                    <span class="mediumSmallText" style="white-space: nowrap;">Rain Rate</span>
                    <span class="mediumSmallText" style="white-space: nowrap;">{$weatherData?.rainRate_inch_per_hour ? Number($weatherData?.rainRate_inch_per_hour).toFixed(1) + " in/Hr" : "--- in/Hr"}</span>
                </div>
                <div on:click={() => $currentView = 'dashboard'} class="card" style="display:flex; flex-flow:column; justify-content: center; align-items: center; flex: 1">
                    <span class="mediumSmallText" style="white-space: nowrap;">24Hr Rain</span>
                    <span class="mediumSmallText" style="white-space: nowrap;">{$weatherData?.rain24_in ? Number($weatherData?.rain24_in).toFixed(1) + " in" : "--- in"}</span>
                </div>
            </div>
        </div>
    </div>
{/if}
{#if display === 'outtemp'}
    <div on:click={() => display='dashboard'}>
        <OutdoorTemperatureGraph chartWidth={outerWidth - (outerWidth * 0.05)} chartHeight={outerHeight - (outerHeight * 0.03)} />
    </div>
{/if}
{#if display === 'intemp'}
    <div style="display:flex; flex-flow:column; align-items: stretch;">
        <div on:click={() => display='dashboard'} bind:clientHeight={headerHeight} >
            <Fa icon="{faArrowLeftLong}" style="font-size: 4vw; color: white;"/>
        </div>
        <IndoorTemperatureGraph chartWidth={wxWidth} chartHeight={wxHeight - headerHeight} />
    </div>
{/if}
{#if display === 'pressure'}
    <div style="display:flex; flex-flow:column; align-items: stretch;">
        <div on:click={() => display='dashboard'} bind:clientHeight={headerHeight} >
            <Fa icon="{faArrowLeftLong}" style="font-size: 4vw; color: white;"/>
        </div>
        <PressureGraph chartWidth={wxWidth} chartHeight={wxHeight - headerHeight} />
    </div>
{/if}
{#if display === 'humidity'}
    <div style="display:flex; flex-flow:column; align-items: stretch;">
        <div on:click={() => display='dashboard'} bind:clientHeight={headerHeight} >
            <Fa icon="{faArrowLeftLong}" style="font-size: 4vw; color: white;"/>
        </div>
        <HumidityGraph chartWidth={wxWidth} chartHeight={wxHeight - headerHeight} />
    </div>
{/if}
</div>