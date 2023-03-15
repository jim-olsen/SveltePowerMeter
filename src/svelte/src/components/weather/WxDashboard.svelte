<script>
    import {currentView, weatherData} from "../../stores";
    import {onDestroy} from "svelte";
    import WindDisplay from "./WindDisplay.svelte";
    import Thermometer from "./Thermometer.svelte";

    let wxData = {};
    let wxHeight = 0;
    let wxWidth = 0;

    const unsubscribeWeather = weatherData.subscribe(data => {
        wxData = data;
    });

    onDestroy(unsubscribeWeather);
</script>
<div style="display:flex; flex-flow: row; justify-content: center; align-content: center; width: 100%; gap: 10px;"
     on:click={() => currentView.set('dashboard')} bind:clientHeight={wxHeight} bind:clientWidth={wxWidth}>
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
                <span class="mediumSmallText" style="white-space: nowrap;">{wxData?.barometer_inHg ? Number(wxData?.barometer_inHg).toFixed(2) + " inHg" : "--- inHg"}</span>
            </div>
            <div class="card" style="display:flex; flex-flow:column; justify-content: center; align-items: center; flex: 1">
                <span class="mediumSmallText" style="white-space: nowrap;">Humidity</span>
                <span class="mediumSmallText" style="white-space: nowrap;">{wxData?.outHumidity ? Number(wxData?.outHumidity).toFixed(1) + " %" : "--- %"}</span>
            </div>
            <div class="card" style="display:flex; flex-flow:column; justify-content: center; align-items: center; flex: 1">
                <span class="mediumSmallText" style="white-space: nowrap;">Rain</span>
                <span class="mediumSmallText" style="white-space: nowrap;">{wxData?.dayRain_in ? Number(wxData?.dayRain_in).toFixed(1) + " in" : "--- in"}</span>
            </div>
            <div class="card" style="display:flex; flex-flow:column; justify-content: center; align-items: center; flex: 1">
                <span class="mediumSmallText" style="white-space: nowrap;">Rain Rate</span>
                <span class="mediumSmallText" style="white-space: nowrap;">{wxData?.rainRate_inch_per_hour ? Number(wxData?.rainRate_inch_per_hour).toFixed(1) + " in/Hr" : "--- in/Hr"}</span>
            </div>
            <div class="card" style="display:flex; flex-flow:column; justify-content: center; align-items: center; flex: 1">
                <span class="mediumSmallText" style="white-space: nowrap;">24Hr Rain</span>
                <span class="mediumSmallText" style="white-space: nowrap;">{wxData?.rain24_in ? Number(wxData?.rain24_in).toFixed(1) + " in" : "--- in"}</span>
            </div>
        </div>
    </div>
</div>