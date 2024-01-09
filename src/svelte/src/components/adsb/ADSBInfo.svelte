<script xmlns="http://www.w3.org/1999/html">
    import {adsbData, blueIrisAlert, currentView} from "../../stores";

    let categories = {
        "A0": "No Info",
        "A1": "Light (<15.5k lbs)",
        "A2": "Small (15.5-75k lbs)",
        "A3": "Large (75-300k lbs)",
        "A4": "High Vortex",
        "A5": "Heavy (>300k lbs)",
        "A6": "High Performance",
        "A7": "Rotorcraft",
        "B0": "No Info",
        "B1": "Glider",
        "B2": "Balloon",
        "B3": "Parachute",
        "B4": "Ultralight",
        "B5": "Reserved",
        "B6": "UAV",
        "B7": "Space",
        "C0": "Land Unk",
        "C1": "Emergency Vehicle",
        "C2": "Service Vehicle",
        "C3": "Point Obstacle",
        "C4": "Cluster Obstacle",
        "C5": "Line Obstacle",
        "C6": "C6",
        "C7": "C7"
    }
</script>
<div style="display:flex; flex-flow:column; justify-content: center; align-items: center; width: 100%;"
         on:click={() => currentView.set('dashboard')}>
    <h2>Flight {$adsbData.hasOwnProperty("flight") ? $adsbData.flight : "Unknown"} is approaching, Distance {$adsbData.hasOwnProperty("r_dst") ? $adsbData.r_dst : "Unknown"} nm</h2>
    <div style="display:flex; flex-flow: row; align-items: center; justify-content: space-between; align-content: space-between; width: 100%;">
        <div><span class="smallText">Altitude: {$adsbData.hasOwnProperty("alt_baro") ? $adsbData.alt_baro : "Unknown"} ft</span></div>
        <div><span class="smallText">Speed: {$adsbData.hasOwnProperty("gs") ? $adsbData.gs : "Unknown"} kt</span></div>
        <div><span class="smallText">Squawk: {$adsbData.hasOwnProperty("squawk") ? $adsbData.squawk : "None"}</span></div>
        <div><span class="smallText">Category: {$adsbData.hasOwnProperty("category") ? categories[$adsbData.category] : "None"}</span></div>
        <div><span class="smallText">DBFlags: {$adsbData.hasOwnProperty("dbFlags") ? $adsbData.squawk : "None"}</span></div>
    </div>
    {#if $adsbData.hasOwnProperty("picture")}
        <img src="{'data:image/png;base64, ' + $adsbData.picture}" style="height: 80vh;"/>
    {:else}
        <h2>No Picture Available</h2>
    {/if}
</div>
