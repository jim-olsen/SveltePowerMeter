<script>
    import {currentView, weatherData} from "../../stores";
    import WindDisplay from "./WindDisplay.svelte";
    import Thermometer from "./Thermometer.svelte";

    let wxHeight = 0;
    let wxWidth = 0;

</script>
<div style="display:flex; flex-flow: row; justify-content: center; align-content: center; width: 100%; gap: 10px;"
     on:click={() => $currentView = 'dashboard'} bind:clientHeight={wxHeight} bind:clientWidth={wxWidth}>
    <div class="card" style="flex: 1; height: {Math.min(wxHeight, wxWidth * 0.5)}px; aspect-ratio: 1 / 1;">
        <WindDisplay diameter={Math.min(wxHeight, wxWidth)}></WindDisplay>
    </div>
    <div style="display:flex; flex-flow: column; justify-content: space-between; flex: 9; gap: 20px; height: 96%;">
        <div class="card" style="display:flex; flex-flow: row; justify-content: space-evenly; align-items: stretch;">
            <Thermometer temperatureField="outTemp_F" title="Outside" height="200"></Thermometer>
            <Thermometer temperatureField="windchill_F" title="Windchill" height="200"></Thermometer>
            <Thermometer temperatureField="inTemp_F" title="Inside" height="200"></Thermometer>
        </div>
        <div style="display:flex; flex-flow: row wrap; justify-content: flex-start; row-gap: 20px; column-gap: 10px;">
            <div class="card" style="display:flex; flex-flow:column; justify-content: center; align-items: center; flex: 1">
                <span class="mediumSmallText" style="white-space: nowrap;">Pressure</span>
                <span class="mediumSmallText" style="white-space: nowrap;">{$weatherData?.barometer_inHg ? Number($weatherData?.barometer_inHg).toFixed(2) + " inHg" : "--- inHg"}</span>
            </div>
            <div class="card" style="display:flex; flex-flow:column; justify-content: center; align-items: center; flex: 1">
                <span class="mediumSmallText" style="white-space: nowrap;">Humidity</span>
                <span class="mediumSmallText" style="white-space: nowrap;">{$weatherData?.outHumidity ? Number($weatherData?.outHumidity).toFixed(1) + " %" : "--- %"}</span>
            </div>
            <div class="card" style="display:flex; flex-flow:column; justify-content: center; align-items: center; flex: 1">
                <span class="mediumSmallText" style="white-space: nowrap;">Rain</span>
                <span class="mediumSmallText" style="white-space: nowrap;">{$weatherData?.dayRain_in ? Number($weatherData?.dayRain_in).toFixed(1) + " in" : "--- in"}</span>
            </div>
            <div class="card" style="display:flex; flex-flow:column; justify-content: center; align-items: center; flex: 1">
                <span class="mediumSmallText" style="white-space: nowrap;">Rain Rate</span>
                <span class="mediumSmallText" style="white-space: nowrap;">{$weatherData?.rainRate_inch_per_hour ? Number($weatherData?.rainRate_inch_per_hour).toFixed(1) + " in/Hr" : "--- in/Hr"}</span>
            </div>
            <div class="card" style="display:flex; flex-flow:column; justify-content: center; align-items: center; flex: 1">
                <span class="mediumSmallText" style="white-space: nowrap;">24Hr Rain</span>
                <span class="mediumSmallText" style="white-space: nowrap;">{$weatherData?.rain24_in ? Number($weatherData?.rain24_in).toFixed(1) + " in" : "--- in"}</span>
            </div>
        </div>
    </div>
</div>