<script>
    import Fa from "svelte-fa";
    import {currentView} from "../../states.svelte.js";
    import {
        faDashboard,
        faPlug,
        faSatelliteDish,
        faLightbulb,
        faSnowflake,
        faExclamationTriangle,
        faBoltLightning,
        faPlane
    } from "@fortawesome/free-solid-svg-icons";
</script>
    <div style="display: flex; flex-flow: row wrap; justify-content: center; align-content: center; row-gap: 6px; gap: 6px; width: 100%; box-sizing: border-box; padding: 2px;">
        <div class="card" style="display: flex; flex-flow: column; justify-content: center; align-items: center; flex: 1 0 25%;"
                on:click={()=> currentView.value = 'dashboard'}>
            <Fa icon={faDashboard} style="font-size: 6vw; color: cadetblue;"/>
            <span class="largeText">Dashboard</span>
        </div>
        <div class="card" style="display: flex; flex-flow: column; justify-content: center; align-items: center; flex: 1 0 25%;"
                on:click={()=> currentView.value = 'statistics'}>
            <Fa icon={faPlug} style="font-size: 6vw; color: cadetblue;"/>
            <span class="largeText">Power</span>
        </div>
        <div class="card" style="display: flex; flex-flow: column; justify-content: center; align-items: center; flex: 1 0 25%;"
                on:click={()=> currentView.value = 'starlinkStatus'}>
            <Fa icon={faSatelliteDish} style="font-size: 6vw; color: cadetblue"/>
            <span class="largeText">Starlink</span>
        </div>
        <div class="card" style="display: flex; flex-flow: column; justify-content: center; align-items: center; flex: 1 0 25%;"
                on:click={()=> currentView.value = 'shelley'}>
            <Fa icon={faLightbulb} style="font-size: 6vw; color: cadetblue"/>
            <span class="largeText">Devices</span>
        </div>
        <div class="card" style="display: flex; flex-flow: column; justify-content: center; align-items: center; flex: 1 0 25%;"
                on:click={()=> currentView.value = 'weather'}>
            <Fa icon={faSnowflake} style="font-size: 6vw; color: cadetblue"/>
            <span class="largeText">Weather</span>
        </div>
        <div class="card" style="display: flex; flex-flow: column; justify-content: center;  align-items: center;flex: 1 0 25%;"
                on:click={()=> currentView.value = 'alerts'}>
            <Fa icon={faExclamationTriangle} style="font-size: 6vw; color: cadetblue"/>
            <span class="largeText">Alerts</span>
        </div>
        <div class="card" style="display: flex; flex-flow: column; justify-content: center;  align-items: center;flex: 1 0 25%;"
             on:click={()=> currentView.value = 'lightningDashboard'}>
            <Fa icon={faBoltLightning} style="font-size: 6vw; color: cadetblue"/>
            <span class="largeText">Lightning</span>
        </div>
        <div class="card" style="display: flex; flex-flow: column; justify-content: center;  align-items: center;flex: 1 0 25%;"
             on:click={()=> currentView.value = 'adsb'}>
            <Fa icon={faPlane} style="font-size: 6vw; color: cadetblue"/>
            <span class="largeText">ADSB</span>
        </div>
    </div>



