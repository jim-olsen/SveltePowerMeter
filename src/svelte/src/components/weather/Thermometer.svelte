<script>
    import {weatherData} from "../../stores";
    import {onDestroy} from "svelte";

    export let temperatureField = "outTemp_F";
    export let title = temperatureField;
    export let minTemp = -20;
    export let maxTemp = 100;

    let temperatureDiv;
    let wxData = {};
    let temperature = 50;
    const unsubscribeWeather = weatherData.subscribe(data => {
        wxData = data;
        temperature = wxData[temperatureField];
        if (temperatureDiv && temperature) {
            temperatureDiv.style.height = (temperature - minTemp) / (maxTemp - minTemp) * 100 + "%";
            temperatureDiv.dataset.value = Number(temperature).toFixed(2) + "°F";
        }
    });

    onDestroy(unsubscribeWeather);
</script>
<style>
    .thermometerWrapper {
        margin: auto;
        display: flex;
        flex-direction: column;
        align-items: center;
    }
    .thermometer {
        width: 25px;
        background: #38383f;
        height: 240px;
        position: relative;
        border: 9px solid #2a2a2e;
        border-radius: 20px;
        z-index: 1;
        margin-bottom: 50px;
    }
    .thermometer:before, .thermometer:after {
        position: absolute;
        content: "";
        border-radius: 50%;
    }
    .thermometer:before {
        width: 100%;
        height: 34px;
        bottom: 9px;
        background: #38383f;
        z-index: -1;
    }
    .thermometer:after {
        transform: translateX(-50%);
        width: 50px;
        height: 50px;
        background-color: #3dcadf;
        bottom: -41px;
        border: 9px solid #2a2a2e;
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
        border-radius: 20px;
        background-size: 100% 240px;
        transition: all 0.2s ease-in-out;
    }
    .thermometer .temperature, .thermometer .temperature:before, .thermometer .temperature:after {
        position: absolute;
    }
    .thermometer .temperature:before {
        content: attr(data-value);
        background: rgba(0, 0, 0, 0.7);
        color: white;
        z-index: 2;
        padding: 5px 10px;
        border-radius: 5px;
        font-size: 1em;
        line-height: 1;
        transform: translateY(50%);
        left: calc(100% + 1em / 1.5);
        top: calc(-1em + 5px - 5px * 2);
    }
    .thermometer .temperature:after {
        content: "";
        border-top: 0.4545454545em solid transparent;
        border-bottom: 0.4545454545em solid transparent;
        border-right: 0.6666666667em solid rgba(0, 0, 0, 0.7);
        left: 100%;
        top: calc(-1em / 2.2 + 5px);
    }
</style>
<div class="thermometerWrapper">
    <span class="mediumSmallText">{title}</span>
    <div class="thermometer">
        <div class="temperature" bind:this={temperatureDiv} style="height:0" data-value="---"></div>
        <div class="graduations"></div>
    </div>
</div>