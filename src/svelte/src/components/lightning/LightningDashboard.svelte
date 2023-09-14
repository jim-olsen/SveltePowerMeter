<script xmlns="http://www.w3.org/1999/html">
    import {lightningData, currentView} from "../../stores";
    import {faBoltLightning} from "@fortawesome/free-solid-svg-icons";
    import Fa from "svelte-fa";
    import FaLayers from "svelte-fa/src/fa-layers.svelte";
    import FaLayersText from "svelte-fa/src/fa-layers-text.svelte";
</script>
<div style="display:flex; flex-flow:column; justify-content: space-evenly; align-items: center; width: 100%; gap: 5px;">
    <div style="display:flex; flex-flow:row; justify-content: space-evenly; align-items: center; width: 100%; gap: 5px;">
        <div style="display:flex; flex-flow: row; justify-content: center; align-items: center; flex: 1; color: yellow; font-size: 6vh;"
            on:click={() => $currentView = 'dashboard'}>
            <FaLayers size="10x" style="color: darkgoldenrod;">
                <Fa icon="{faBoltLightning}"/>
                <FaLayersText scale="{1.1}" style="color:greenyellow;font-weight: bolder;">{$lightningData?.last_strike_24hr?.distance}</FaLayersText>
            </FaLayers>
        </div>
        <div style="display:flex; flex-flow: column; justify-content: center; align-items: center">
            <div><span class="normalText">Last Strike</span></div>
            <div><span class="normalText">{new Date($lightningData?.last_strike_24hr?.record_time * 1000).toLocaleString()}</span></div>
            <div><span class="normalText">Distance {$lightningData?.last_strike_24hr?.distance} km</span></div>
            <div><span class="normalText">Intensity {$lightningData?.last_strike_24hr?.intensity.toFixed(2)}</span></div>
        </div>
    </div>
    <div style="display:flex; flex-flow: row; justify-content: space-evenly; align-items: center; width: 100%;">
        <div><span class="mediumSmallText">Closest Strike {$lightningData?.summary?.closest_strike} km</span></div>
        <div><span class="mediumSmallText">Strongest Strike {$lightningData?.summary?.strongest_strike?.toFixed(2)}</span></div>
    </div>
    <div style="display:flex; flex-flow: row; justify-content: space-evenly; align-items: center; width: 100%;">
        <div><span class="mediumSmallText">{$lightningData?.summary?.total_strikes} total strikes</span></div>
        <div><span class="mediumSmallText">{$lightningData?.summary?.total_disturbers} total disturbers</span></div>
        <div><span class="mediumSmallText">{$lightningData?.summary?.total_noise} total noise</span></div>
    </div>
</div>