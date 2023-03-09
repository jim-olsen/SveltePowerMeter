<script xmlns="http://www.w3.org/1999/html">
    import {currentView} from "../../stores";
    import {faDashboard, faPlug, faSatelliteDish, faLightbulb, faSnowflake, faExclamationTriangle} from "@fortawesome/free-solid-svg-icons";
</script>
    <div style="display: flex; flex-flow: column; justify-content: space-between;">
    <button class="tabButton"
            on:click={()=> {currentView.set('dashboard')}}>
        <Fa icon={faDashboard} size="2x"/>
    </button>
    <button class="tabButton"
            on:click={()=> {currentView.set('powerMeter')}}>
        <Fa icon={faPlug} size="2x"/>
    </button>
    <button class="tabButton"
            on:click={()=> {currentView.set('starlink')}}>
        <Fa icon={faSatelliteDish} size="2x"/>
    </button>
    <button class="tabButton"
            on:click={()=> {currentView.set('shelley')}}>
        <Fa icon={faLightbulb} size="2x"/>
    </button>
    <button class="tabButton"
            on:click={()=> {currentView.set('weather')}}>
        <Fa icon={faSnowflake} size="2x"/>
    </button>
    <button class="tabButton"
            on:click={()=> {currentView.set('alerts')}}>
        <Fa icon={faExclamationTriangle} size="2x"/>
    </button>
</div>
