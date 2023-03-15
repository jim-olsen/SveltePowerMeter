<script>
import {weatherData} from "../../stores";
import {onDestroy} from "svelte";

let compass, arrow, text;
let wxData = {};
export let diameter = 500;

const unsubscribeWeather = weatherData.subscribe(data => {
    wxData = data;
    if (compass) {
        let transformation = 'rotate(' + (wxData?.windDir ? wxData?.windDir : "0") + 'deg)'
        compass.style.transform = transformation;
    }
    if (arrow) {
        if (!wxData?.windDir) {
            arrow.style.visibility = 'hidden';
        } else {
            arrow.style.visibility = 'visible';
        }
    }
    if (text) {
        let transformation = 'rotate(-' + (wxData?.windDir ? wxData?.windDir : "0") + 'deg)'
        text.style.transform = transformation;
    }
});

onDestroy(unsubscribeWeather);
</script>
<style>
    .compass {
        display: block;
        border-radius: 100%;
        box-shadow: 0 0 10px rgba(0, 0, 0, .85);
        position: relative;
    }

    .arrow {
        width: 100%;
        height: 100%;
        display: block;
        position: absolute;
        top: 0;
        content: "";
        width: 0;
        height: 0;
        border-left: 25px solid transparent;
        border-right: 25px solid transparent;
        border-bottom: 50px solid red;
        position: absolute;
        top: -26px;
        left: 50%;
        margin-left: -25px;
        z-index: 99;
    }


</style>
<div style = "display: flex; flex-flow: column; align-items: center; justify-content: center; width: 100%; height: 100%;">
    <div bind:this={compass} class="compass" style="width: 85%; height: 85%; display: flex; flex-flow: column; justify-content: center; align-items: center;">
        <div bind:this={text} style="display: flex; flex-flow: column; justify-content: center; align-items: center;">
            <span class="largerText">{wxData?.windDir ? Number(wxData?.windDir).toFixed(0) : '--'}</span>
            <span class="largerText">{wxData?.wind_average ? Number(wxData?.wind_average)?.toFixed(1) : '---'} MPH</span>
        </div>
        <div bind:this={arrow} class="arrow"></div>
    </div>
</div>
