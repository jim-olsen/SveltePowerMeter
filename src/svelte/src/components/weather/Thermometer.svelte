<script>
    import {weatherData, weatherDailyMinMax} from "../../stores.svelte.js";
    import {onDestroy} from "svelte";

    export let temperatureField = "outTemp_F";
    export let temperatureMinField = "outTemp_F_max";
    export let temperatureMaxField = "outTemp_F_min";
    export let title = temperatureField;
    export let minTemp = -20;
    export let maxTemp = 100;
    export let height = 140;

    let temperatureDiv, temperatureMinDiv, temperatureMaxDiv;
    let wxData = {};
    let temperature = 50;
    let minTemperature = minTemp;
    let maxTemperature = minTemp;
    const unsubscribeWeather = weatherData.subscribe(data => {
        wxData = data;
        temperature = wxData[temperatureField];
        if (temperatureDiv && temperature) {
            temperatureDiv.style.height = (temperature - minTemp) / (maxTemp - minTemp) * 100 + "%";
            temperatureDiv.dataset.value = Number(temperature).toFixed(2) + "°F";
        }
    });

    const unsubscribeWeatherMinMax = weatherDailyMinMax.subscribe(data => {
        minTemperature = data[temperatureMinField];
        maxTemperature = data[temperatureMaxField];
        if (temperatureDiv && minTemperature && maxTemperature) {
            temperatureMinDiv.style.height = (minTemperature - minTemp) / (maxTemp - minTemp) * 100 + "%";
            temperatureMaxDiv.style.height = (maxTemperature - minTemp) / (maxTemp - minTemp) * 100 + "%";
        }
    });

    onDestroy(()=> {
        unsubscribeWeather();
        unsubscribeWeatherMinMax();
    });
</script>

<div class="thermo-wrap">
    <span class="thermo-title">{title}</span>
    <div class="thermometer" style="height: {height}px; width: {Math.max(14, height / 8)}px;">
        <div class="temperatureMin" bind:this={temperatureMinDiv} style="height:0" data-value="---"></div>
        <div class="temperatureMax" bind:this={temperatureMaxDiv} style="height:0" data-value="---"></div>
        <div class="temperature" bind:this={temperatureDiv} style="height:0" data-value="---"></div>
        <div class="graduations"></div>
    </div>
    <span class="thermo-value">{temperature ? Number(temperature).toFixed(1) : "---"}<span class="thermo-unit">°F</span></span>
    <span class="thermo-range">{minTemperature ? Number(minTemperature).toFixed(0) : "---"}° / {maxTemperature ? Number(maxTemperature).toFixed(0) : "---"}°</span>
</div>

<style>
    .thermo-wrap {
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        gap: 6px;
        padding: 6px 4px;
    }

    .thermo-title {
        font-size: 12px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.6px;
        color: #b0b9c8;
    }

    .thermo-value {
        font-size: 42px;
        font-weight: 700;
        color: #fca503;
        line-height: 1;
        font-variant-numeric: tabular-nums;
        font-stretch: 90%;
        height: 42px;
        display: flex;
        align-items: center;
        justify-content: center;
    }

    .thermo-unit {
        font-size: 22px;
        font-weight: 500;
        color: #e6eaf2;
        margin-left: 1px;
    }

    @media (min-width: 1280px) and (min-height: 720px) {
        .thermo-value { font-size: 56px; height: 56px; }
        .thermo-unit { font-size: 30px; }
    }

    .thermo-range {
        font-size: 11px;
        font-weight: 600;
        color: #8892A6;
        font-variant-numeric: tabular-nums;
    }

    .thermometer {
        background: #38383f;
        position: relative;
        border: 6px solid #2a2a2e;
        border-radius: 14px;
        z-index: 1;
        margin-bottom: 15%;
    }

    .thermometer:before, .thermometer:after {
        position: absolute;
        content: "";
        border-radius: 50%;
    }

    .thermometer:before {
        width: 100%;
        height: 24px;
        bottom: 6px;
        background: #38383f;
        z-index: -1;
    }

    .thermometer:after {
        transform: translateX(-50%);
        width: 160%;
        height: 20%;
        background-color: #3dcadf;
        bottom: -15%;
        border: 6px solid #2a2a2e;
        z-index: -3;
        left: 50%;
    }

    .thermometer .graduations {
        height: 59%;
        top: 20%;
        width: 50%;
    }

    .thermometer .graduations, .thermometer .graduations:before {
        position: absolute;
        border-top: 2px solid rgba(0, 0, 0, 0.5);
        border-bottom: 2px solid rgba(0, 0, 0, 0.5);
    }

    .thermometer .graduations:before {
        content: "";
        height: 34%;
        width: 100%;
        top: 32%;
    }

    .thermometer .temperature {
        bottom: 0;
        background: linear-gradient(#f17a65, #3dcadf) no-repeat bottom;
        width: 100%;
        border-radius: 14px;
        background-size: 100% 240px;
        transition: all 0.2s ease-in-out;
    }

    .thermometer .temperatureMin {
        bottom: 0;
        background: rgba(0,0,0,0) no-repeat bottom;
        width: 100%;
        border-radius: 14px;
        background-size: 100% 240px;
        transition: all 0.2s ease-in-out;
    }

    .thermometer .temperatureMax {
        bottom: 0;
        background: rgba(0,0,0,0) no-repeat bottom;
        width: 100%;
        border-radius: 14px;
        background-size: 100% 240px;
        transition: all 0.2s ease-in-out;
    }

    .thermometer .temperature, .thermometer .temperature:before, .thermometer .temperature:after {
        position: absolute;
    }

    .thermometer .temperatureMin, .thermometer .temperatureMin:before, .thermometer .temperatureMin:after {
        position: absolute;
    }

    .thermometer .temperatureMax, .thermometer .temperatureMax:before, .thermometer .temperatureMax:after {
        position: absolute;
    }

    .thermometer .temperatureMin:after {
        content: "";
        border-top: 0.4545454545em solid transparent;
        border-bottom: 0.4545454545em solid transparent;
        border-right: 0.6666666667em solid rgba(100, 149, 237, 0.7);
        left: 100%;
        top: calc(-1em / 2.2 + 5px);
    }

    .thermometer .temperatureMax:after {
        content: "";
        border-top: 0.4545454545em solid transparent;
        border-bottom: 0.4545454545em solid transparent;
        border-right: 0.6666666667em solid rgba(255, 0, 0, 0.7);
        left: 100%;
        top: calc(-1em / 2.2 + 5px);
    }

    .thermometer .temperature:after {
        content: "";
        border-top: 0.4545454545em solid transparent;
        border-bottom: 0.4545454545em solid transparent;
        border-right: 0.6666666667em solid rgba(230, 234, 242, 0.85);
        left: 100%;
        top: calc(-1em / 2.2 + 5px);
    }
</style>



