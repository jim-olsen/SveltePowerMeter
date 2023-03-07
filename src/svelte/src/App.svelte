<script>
    import StarlinkRawData from "./components/starlink/StarlinkRawData.svelte"
    import StarlinkObstructionMap from "./components/starlink/StarlinkObstructionMap.svelte";
    import StarlinkUploadDataRates from "./components/starlink/StarlinkUploadDataRates.svelte"
    import StarlinkDownloadDataRates from "./components/starlink/StarlinkDownloadDataRates.svelte"
    import StarlinkPingLatency from "./components/starlink/StarlinkPingLatency.svelte";
    import StarlinkPingDrop from "./components/starlink/StarlinkPingDrop.svelte"
    import StarlinkStatusIndicator from "./components/starlink/StarlinkStatusIndicator.svelte"
    import StarlinkOutagesChart from "./components/starlink/StarlinkOutagesChart.svelte"
    import StarlinkOutagesList from "./components/starlink/StarlinkOutageList.svelte"
    import StarlinkAlerts from "./components/starlink/StarlinkAlerts.svelte";
    import StarlinkOutageDurationChart from "./components/starlink/StarlinkOutageDurationChart.svelte";
    import StarlinkFirmwareVersion from "./components/starlink/StarlinkFirmwareVersion.svelte";
    import StarlinkUpTime from "./components/starlink/StarlinkUpTime.svelte";
    import StarlinkAntenna from "./components/starlink/StarlinkAntenna.svelte";
    import StarlinkControls from "./components/starlink/StarlinkControls.svelte";
    import ShellyDeviceList from "./components/shelly/ShellyDeviceList.svelte";
    import Statistics from "./components/powermeter/Statistics.svelte";
    import CurrentValues from "./components/powermeter/CurrentValues.svelte";
    import VoltageGraph from "./components/powermeter/VoltageGraph.svelte";
    import SolarWattsGraph from "./components/powermeter/SolarWattsGraph.svelte";
    import BatteryWattsGraph from "./components/powermeter/BatteryWattsGraph.svelte";
    import LoadGraph from "./components/powermeter/LoadGraph.svelte";
    import Fa from 'svelte-fa'
    import BlueIrisAlert from "./components/blueiris/BlueIrisAlert.svelte";
    import {
        faDashboard, faPlug, faWifiStrong, faHandPointer, faLightbulb, faSnowflake, faBarChart,
        faSun, faCarBattery, faBoltLightning, faPlugCircleBolt, faSatelliteDish, faTachographDigital,
        faGaugeHigh, faLinkSlash, faGamepad, faExclamationTriangle
    } from '@fortawesome/free-solid-svg-icons'

    let dashboard = true;
    let outages = false;
    let allComponents = false;
    let rawData = false;
    let dishControl = false;
    let testScreen = false;
    let innerWidth = 0;
    let outerWidth = 0
    let outerHeight = 0
    let stats = true;

    let currentView = 'powerMeter';
    let powerView = 'stats';
    let touchStarlinkView = 'status';
</script>

<svelte:window bind:outerWidth bind:outerHeight bind:innerWidth/>
<div style="display:flex; flex-flow: row; gap: 20px; width: 100%;">
    <div style="display: flex; flex-flow: column; justify-content: space-between; height:{outerHeight - 10}px;">
        <button class="tabButton"
                on:click={()=> {currentView = 'dashboard'}}>
            <Fa icon={faDashboard} size="2x"/>
        </button>
        <button class="tabButton"
                on:click={()=> {currentView = 'powerMeter'}}>
            <Fa icon={faPlug} size="2x"/>
        </button>
        <button class="tabButton"
                on:click={()=> {currentView = 'starlink'}}>
            <Fa icon={faSatelliteDish} size="2x"/>
        </button>
        <button class="tabButton"
                on:click={()=> {currentView = 'shelley'}}>
            <Fa icon={faLightbulb} size="2x"/>
        </button>
        <button class="tabButton"
                on:click={()=> {currentView = 'weather'}}>
            <Fa icon={faSnowflake} size="2x"/>
        </button>
        <button class="tabButton"
                on:click={()=> {currentView = 'alerts'}}>
            <Fa icon={faExclamationTriangle} size="2x"/>
        </button>
    </div>
    {#if currentView === 'powerMeter'}
        <div style="display: flex; flex-flow: column; flex-grow: 9; justify-content: space-between;">
            {#if powerView === 'volts'}
                <div style="display:flex; flex-flow: column;justify-content: space-between; height:100%;">
                    <CurrentValues/>
                    <div>
                        <VoltageGraph chartWidth={(outerWidth - (outerWidth / 6)) } chartHeight={outerHeight * 0.65}/>
                    </div>
                </div>
            {/if}

            {#if powerView === 'solar'}
                <div style="display:flex; flex-flow: column;justify-content: space-between; height:100%;">
                    <CurrentValues/>
                    <SolarWattsGraph chartWidth={(outerWidth - (outerWidth / 6))} chartHeight={outerHeight * 0.65}/>
                </div>
            {/if}

            {#if powerView === 'stats'}
                <div style="display:flex; flex-flow: column;justify-content: space-between; height:100%;">
                    <CurrentValues/>
                    <Statistics/>
                </div>
            {/if}

            {#if powerView === 'battery'}
                <div style="display:flex; flex-flow: column;justify-content: space-between; height: 100%;">
                    <CurrentValues/>
                    <BatteryWattsGraph chartWidth={(outerWidth - (outerWidth / 6))} chartHeight={outerHeight * 0.65}/>
                </div>
            {/if}

            {#if powerView === 'load'}
                <div style="display:flex; flex-flow: column;justify-content: space-between; height: 100%;">
                    <CurrentValues/>
                    <LoadGraph chartWidth={(outerWidth - (outerWidth / 6))} chartHeight={outerHeight * 0.65}/>
                </div>
            {/if}

            <div style="display:flex; flex-flow: column; justify-content: flex-end">
                <div style="display:flex; flex-flow:row;justify-content: space-between;">
                    <button class="tabButton"
                            on:click={()=> {powerView = 'stats'}}>
                        <Fa icon="{faBarChart}" size="2x"/>
                    </button>
                    <button class="tabButton"
                            on:click={()=> {powerView = 'volts'}}>
                        <Fa icon="{faCarBattery}" size="2x"/>
                    </button>
                    <button class="tabButton"
                            on:click={()=> {powerView = 'solar'}}>
                        <Fa icon="{faSun}" size="2x"/>
                    </button>
                    <button class="tabButton"
                            on:click={()=> {powerView = 'battery'}}>
                        <Fa icon="{faCarBattery}" size="2x"/>
                        <Fa icon="{faBoltLightning}" size="1x"/>
                    </button>
                    <button class="tabButton"
                            on:click={()=> {powerView = 'load'}}>
                        <Fa icon="{faPlugCircleBolt}" size="2x"/>
                    </button>
                </div>
            </div>
        </div>
    {/if}
    {#if currentView === 'starlink'}
        {#if outerWidth > 1500 && outerHeight > 900}
            <div style="display:flex; flex-flow:row; flex-grow: 9;">
                <button class="tabButton"
                        on:click={()=> {dashboard=true; outages=false;allComponents=false;rawData=false;dishControl=false;testScreen=false;}}>
                    Dashboard
                </button>
                <button class="tabButton"
                        on:click={()=> {dashboard=false; outages=true; allComponents=false;rawData=false;dishControl=false;testScreen=false;}}>
                    Outages
                </button>
                <button class="tabButton"
                        on:click={()=> {dashboard=false; outages=false; allComponents=false;rawData=false;dishControl=true;testScreen=false;}}>
                    Dish Control
                </button>
                <button class="tabButton"
                        on:click={()=> {dashboard=false; outages=false; allComponents=false;rawData=true;dishControl=false;testScreen=false;}}>
                    Raw Data
                </button>
            </div>
            {#if dashboard}
                <div style="display:flex; flex-flow:column; justify-content: center;">
                    <div style="display:flex; flex-flow: row; justify-content: space-evenly; flex-wrap: wrap;">
                        <StarlinkStatusIndicator/>
                        <div style="display:flex; flex-flow: row; justify-content: space-evenly; gap: 50px">
                            <div style="display:flex; justify-content: center; flex-flow: column; align-items: center">
                                <span><b>Alerts</b></span>
                                <hr style="width: 100%"/>
                                <StarlinkAlerts/>
                            </div>
                            <div style="display:flex; justify-content: flex-start; flex-flow: column; align-items: center; gap: 10px">
                                <span><b>Obstruction Map</b></span>
                                <StarlinkObstructionMap width=200 height=200/>
                            </div>
                        </div>
                    </div>
                    <div style="display:flex; flex-flow: row; justify-content: space-evenly; gap: 20px; flex-wrap: wrap;">
                        <div style="display:flex; flex-flow: column; justify-content: flex-start;">
                            <span><b>Upload Speed</b></span>
                            <hr style="width: 100%"/>
                            <StarlinkUploadDataRates chartWidth={Math.min(600, outerWidth - 100)} chartHeight=200/>
                        </div>
                        <div style="display:flex; flex-flow: column; justify-content: flex-start;">
                            <span><b>Download Speed</b></span>
                            <hr style="width: 100%"/>
                            <StarlinkDownloadDataRates chartWidth={Math.min(600, outerWidth - 100)} chartHeight=200/>
                        </div>
                    </div>
                    <div style="display:flex; flex-flow: row; justify-content: space-evenly; gap: 20px; flex-wrap: wrap;">
                        <div style="display:flex; flex-flow: column; justify-content: flex-start;">
                            <span><b>Ping Latency</b></span>
                            <hr style="width: 100%"/>
                            <StarlinkPingLatency chartWidth={Math.min(600, outerWidth - 100)} chartHeight=200/>
                        </div>
                        <div style="display:flex; flex-flow: column; justify-content: flex-start;">
                            <span><b>Ping Drop</b></span>
                            <hr style="width: 100%"/>
                            <StarlinkPingDrop chartWidth={Math.min(600, outerWidth - 100)} chartHeight=200/>
                        </div>
                    </div>
                    <div style="display:flex; flex-flow: row; justify-content: space-around; flex-wrap: wrap;">
                        <StarlinkFirmwareVersion/>
                        <StarlinkUpTime/>
                    </div>
                </div>
            {/if}

            {#if outages}
                <div style="display:flex; flex-flow: column; justify-content: flex-start">
                    <StarlinkOutagesList/>
                    <div style="display:flex; flex-flow:row; justify-content: space-around">
                        <StarlinkOutagesChart/>
                    </div>
                    <div style="display:flex; flex-flow:row; justify-content: space-around">
                        <StarlinkOutageDurationChart/>
                    </div>

                </div>
            {/if}

            {#if dishControl}
                <div style="display:flex; flex-flow: column; justify-content: space-evenly; gap: 20px;">
                    <span><b>Antenna Orientation</b></span>
                    <StarlinkAntenna/>
                    <span><b>Dishy Control</b></span>
                    <StarlinkControls/>
                </div>
            {/if}

            {#if rawData}
                <div style="display:flex; flex-flow: column; justify-content: flex-start">
                    <StarlinkRawData/>
                </div>
            {/if}
        {:else}
            <div style="display:flex; flex-flow: column; justify-content: space-between; flex-grow: 9;">
                {#if touchStarlinkView === 'status'}
                    <div style="display:flex; flex-flow: row; justify-content: space-evenly; flex-wrap: wrap;">
                        <StarlinkStatusIndicator/>
                        <div style="display:flex; flex-flow: row; justify-content: space-evenly; gap: 50px">
                            <div style="display:flex; justify-content: center; flex-flow: column; align-items: center">
                                <span><b>Alerts</b></span>
                                <hr style="width: 100%"/>
                                <StarlinkAlerts/>
                            </div>
                            <div style="display:flex; justify-content: flex-start; flex-flow: column; align-items: center; gap: 10px">
                                <span><b>Obstruction Map</b></span>
                                <StarlinkObstructionMap width=200 height=200/>
                            </div>
                        </div>
                    </div>
                    <div style="display:flex; flex-flow: row; justify-content: space-around; flex-wrap: wrap;">
                        <StarlinkFirmwareVersion/>
                        <StarlinkUpTime/>
                    </div>
                {/if}
                {#if touchStarlinkView === 'speed'}
                    <div style="display:flex; flex-flow: column; justify-content: flex-start;">
                        <span><b>Upload Speed</b></span>
                        <hr style="width: 100%"/>
                        <StarlinkUploadDataRates chartWidth={Math.min(600, outerWidth - 100)} chartHeight=160/>
                    </div>
                    <div style="display:flex; flex-flow: column; justify-content: flex-start;">
                        <span><b>Download Speed</b></span>
                        <hr style="width: 100%"/>
                        <StarlinkDownloadDataRates chartWidth={Math.min(600, outerWidth - 100)} chartHeight=160/>
                    </div>
                {/if}
                {#if touchStarlinkView === 'quality'}
                    <div style="display:flex; flex-flow: column; justify-content: flex-start;">
                        <span><b>Ping Latency</b></span>
                        <hr style="width: 100%"/>
                        <StarlinkPingLatency chartWidth={Math.min(600, outerWidth - 100)} chartHeight=160/>
                    </div>
                    <div style="display:flex; flex-flow: column; justify-content: flex-start;">
                        <span><b>Ping Drop</b></span>
                        <hr style="width: 100%"/>
                        <StarlinkPingDrop chartWidth={Math.min(600, outerWidth - 100)} chartHeight=160/>
                    </div>
                {/if}
                {#if touchStarlinkView === 'outages'}
                    <div style="display:flex; flex-flow: column; justify-content: flex-start">
                        <div style="display:flex; flex-flow:row; justify-content: space-around">
                            <StarlinkOutagesChart chartWidth={outerWidth - 20} chartHeight=200/>
                        </div>
                        <div style="display:flex; flex-flow:row; justify-content: space-around">
                            <StarlinkOutageDurationChart chartWidth={outerWidth - 20} chartHeight=200/>
                        </div>

                    </div>
                {/if}
                {#if touchStarlinkView === 'control'}
                    <div style="display:flex; flex-flow: column; justify-content: space-evenly; gap: 20px;">
                        <span><b>Antenna Orientation</b></span>
                        <StarlinkAntenna chartHeight="250"/>
                        <span><b>Dishy Control</b></span>
                        <StarlinkControls/>
                    </div>
                {/if}
                <div style="display:flex; flex-flow: column; justify-content: flex-end">
                    <div style="display:flex; flex-flow:row;justify-content: space-between;">
                        <button class="tabButton"
                                on:click={()=> {touchStarlinkView = 'status'}}>
                            <Fa icon="{faTachographDigital}" size="2x"/>
                        </button>
                        <button class="tabButton"
                                on:click={()=> {touchStarlinkView = 'speed'}}>
                            <Fa icon="{faGaugeHigh}" size="2x"/>
                        </button>
                        <button class="tabButton"
                                on:click={()=> {touchStarlinkView = 'quality'}}>
                            <Fa icon="{faWifiStrong}" size="2x"/>
                        </button>
                        <button class="tabButton"
                                on:click={()=> {touchStarlinkView = 'outages'}}>
                            <Fa icon="{faLinkSlash}" size="2x"/>
                        </button>
                        <button class="tabButton"
                                on:click={()=> {touchStarlinkView = 'control'}}>
                            <Fa icon="{faGamepad}" size="2x"/>
                        </button>
                    </div>
                </div>
            </div>
        {/if}
    {/if}
    {#if currentView === 'shelley'}
        <div style="display:flex; flex-flow: column; justify-content: space-between; height:100%; flex-grow: 9;">
            <ShellyDeviceList/>
        </div>
    {/if}
    {#if currentView === 'alerts'}
        <BlueIrisAlert />
    {/if}
</div>
