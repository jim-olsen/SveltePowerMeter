<script xmlns="http://www.w3.org/1999/html">
    import Fa from "svelte-fa";
    import {currentView} from "../../stores";
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
    <div style="display: flex; flex-flow: row wrap; justify-content: center; align-content: center; row-gap: 15px; gap: 15px;">
        <div class="card" style="display: flex; flex-flow: column; justify-content: center; align-items: center; flex: 1 0 25%;"
                on:click={()=> $currentView = 'dashboard'}>
            <Fa icon={faDashboard} style="font-size: 6vw; color: cadetblue;"/>
            <span class="largeText">Dashboard</span>
        </div>
        <div class="card" style="display: flex; flex-flow: column; justify-content: center; align-items: center; flex: 1 0 25%;"
                on:click={()=> $currentView = 'statistics'}>
            <Fa icon={faPlug} style="font-size: 6vw; color: cadetblue;"/>
            <span class="largeText">Power</span>
        </div>
        <div class="card" style="display: flex; flex-flow: column; justify-content: center; align-items: center; flex: 1 0 25%;"
                on:click={()=> $currentView = 'starlinkStatus'}>
            <Fa icon={faSatelliteDish} style="font-size: 6vw; color: cadetblue"/>
            <span class="largeText">Starlink</span>
        </div>
        <div class="card" style="display: flex; flex-flow: column; justify-content: center; align-items: center; flex: 1 0 25%;"
                on:click={()=> $currentView = 'shelley'}>
            <Fa icon={faLightbulb} style="font-size: 6vw; color: cadetblue"/>
            <span class="largeText">Devices</span>
        </div>
        <div class="card" style="display: flex; flex-flow: column; justify-content: center; align-items: center; flex: 1 0 25%;"
                on:click={()=> $currentView = 'weather'}>
            <Fa icon={faSnowflake} style="font-size: 6vw; color: cadetblue"/>
            <span class="largeText">Weather</span>
        </div>
        <div class="card" style="display: flex; flex-flow: column; justify-content: center;  align-items: center;flex: 1 0 25%;"
                on:click={()=> $currentView = 'alerts'}>
            <Fa icon={faExclamationTriangle} style="font-size: 6vw; color: cadetblue"/>
            <span class="largeText">Alerts</span>
        </div>
        <div class="card" style="display: flex; flex-flow: column; justify-content: center;  align-items: center;flex: 1 0 25%;"
             on:click={()=> $currentView = 'lightningDashboard'}>
            <Fa icon={faBoltLightning} style="font-size: 6vw; color: cadetblue"/>
            <span class="largeText">Lightning</span>
        </div>
        <div class="card" style="display: flex; flex-flow: column; justify-content: center;  align-items: center;flex: 1 0 25%;"
             on:click={()=> $currentView = 'adsb'}>
            <Fa icon={faPlane} style="font-size: 6vw; color: cadetblue"/>
            <span class="largeText">ADSB</span>
        </div>
    </div>
