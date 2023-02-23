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
    let voltageGraph = false;
    let solarGraph = false;
    let batteryGraph = false;
    let loadGraph = false;
    let fullScreenStarlink = false;
    let fullScreenPowerMeter = true;
    let fullScreenMenu = false;
    let touchScreenStarlink = false;
    let shellyPowerDisplay = false;
    let touchStatus = true;
    let touchSpeed = false;
    let touchQuality = false;
    let touchOutages = false;
    let touchControl = false;
</script>

<svelte:window bind:outerWidth bind:outerHeight bind:innerWidth/>
{#if fullScreenMenu}
    <div style="display: flex; flex-flow: column;gap: 20px;">
        <button class="tabButton"
                on:click={()=> {fullScreenMenu=false;fullScreenPowerMeter=true;fullScreenStarlink=false;touchScreenStarlink=false;shellyPowerDisplay=false;}}>
            PowerMeter
        </button>
        <button class="tabButton"
                on:click={()=> {fullScreenMenu=false;fullScreenPowerMeter=false;fullScreenStarlink=true;touchScreenStarlink=false;shellyPowerDisplay=false;}}>
            Full Screen Starlink
        </button>
        <button class="tabButton"
                on:click={()=> {fullScreenMenu=false;fullScreenPowerMeter=false;fullScreenStarlink=false;touchScreenStarlink=true;shellyPowerDisplay=false;}}>
            Touch Screen Starlink
        </button>
        <button class="tabButton"
                on:click={()=> {fullScreenMenu=false;fullScreenPowerMeter=false;fullScreenStarlink=false;touchScreenStarlink=false;shellyPowerDisplay=true;}}>
            Shelly Devices
        </button>
    </div>
{/if}
{#if fullScreenPowerMeter}
    <div style="display: flex; flex-flow: column;">
        {#if voltageGraph}
            <div style="display:flex; flex-flow: column;justify-content: flex-start;">
                <CurrentValues/>
                <div>
                    <VoltageGraph chartWidth={(outerWidth - (outerWidth / 10)) } chartHeight={outerHeight * 0.65}/>
                </div>
            </div>
        {/if}

        {#if solarGraph}
            <div style="display:flex; flex-flow: column;justify-content: center;">
                <CurrentValues/>
                <SolarWattsGraph chartWidth={(outerWidth - (outerWidth / 10))} chartHeight={outerHeight * 0.65}/>
            </div>
        {/if}

        {#if stats}
            <div style="display:flex; flex-flow: column;justify-content: center;gap: 10px;">
                <CurrentValues/>
                <Statistics/>
            </div>
        {/if}

        {#if batteryGraph}
            <div style="display:flex; flex-flow: column;justify-content: center; height: 100%;">
                <CurrentValues/>
                <BatteryWattsGraph chartWidth={(outerWidth - (outerWidth / 10))} chartHeight={outerHeight * 0.65}/>
            </div>
        {/if}

        {#if loadGraph}
            <div style="display:flex; flex-flow: column;justify-content: center; height: 100%;">
                <CurrentValues/>
                <LoadGraph chartWidth={(outerWidth - (outerWidth / 10))} chartHeight={outerHeight * 0.65}/>
            </div>
        {/if}

        <div style="display:flex; flex-flow: column; justify-content: flex-end">
            <div style="display:flex; flex-flow:row;justify-content: space-between;">
                <button class="tabButton"
                        on:click={()=> {stats=true; voltageGraph=false;solarGraph=false;batteryGraph=false;loadGraph=false;}}>
                    Statistics
                </button>
                <button class="tabButton"
                        on:click={()=> {stats=false; voltageGraph=true;solarGraph=false;batteryGraph=false;loadGraph=false;}}>
                    Voltage
                </button>
                <button class="tabButton"
                        on:click={()=> {stats=false; voltageGraph=false;solarGraph=true;batteryGraph=false;loadGraph=false;}}>
                    Solar
                </button>
                <button class="tabButton"
                        on:click={()=> {stats=false; voltageGraph=false;solarGraph=false;batteryGraph=true;loadGraph=false;}}>
                    Battery
                </button>
                <button class="tabButton"
                        on:click={()=> {stats=false; voltageGraph=false;solarGraph=false;batteryGraph=false;loadGraph=true;}}>
                    Load
                </button>
                <button class="tabButton"
                        on:click={()=> {stats=true; voltageGraph=false;solarGraph=false;batteryGraph=false;loadGraph=false;fullScreenMenu=true;fullScreenPowerMeter=false;}}>
                    ...
                </button>
            </div>
        </div>
    </div>
{/if}
{#if fullScreenStarlink}
    <div style="display:flex; flex-flow:row">
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
        <button class="tabButton"
                on:click={()=> {dashboard=true; outages=false; allComponents=false;rawData=false;dishControl=false;testScreen=false;fullScreenMenu=true;fullScreenStarlink=false;}}>
            ...
        </button>

    </div>
    {#if dashboard}
        <div style="display:flex; flex-flow:column; justify-content: center;">
            <div style="display:flex; flex-flow: row; justify-content: space-evenly; flex-wrap: wrap;">
                <StarlinkStatusIndicator />
                <div style="display:flex; flex-flow: row; justify-content: space-evenly; gap: 50px">
                    <div style="display:flex; justify-content: center; flex-flow: column; align-items: center">
                        <span><b>Alerts</b></span>
                        <hr style="width: 100%" />
                        <StarlinkAlerts />
                    </div>
                    <div style="display:flex; justify-content: flex-start; flex-flow: column; align-items: center; gap: 10px">
                        <span><b>Obstruction Map</b></span>
                        <StarlinkObstructionMap width=200 height=200 />
                    </div>
                </div>
            </div>
            <div style="display:flex; flex-flow: row; justify-content: space-evenly; gap: 20px; flex-wrap: wrap;">
                <div style="display:flex; flex-flow: column; justify-content: flex-start;">
                    <span><b>Upload Speed</b></span>
                    <hr style="width: 100%"/>
                    <StarlinkUploadDataRates chartWidth={Math.min(600, outerWidth - 100)} chartHeight=200 />
                </div>
                <div style="display:flex; flex-flow: column; justify-content: flex-start;">
                    <span><b>Download Speed</b></span>
                    <hr style="width: 100%"/>
                    <StarlinkDownloadDataRates chartWidth={Math.min(600, outerWidth - 100)} chartHeight=200 />
                </div>
            </div>
            <div style="display:flex; flex-flow: row; justify-content: space-evenly; gap: 20px; flex-wrap: wrap;">
                <div style="display:flex; flex-flow: column; justify-content: flex-start;">
                    <span><b>Ping Latency</b></span>
                    <hr style="width: 100%" />
                    <StarlinkPingLatency chartWidth={Math.min(600, outerWidth - 100)} chartHeight=200 />
                </div>
                <div style="display:flex; flex-flow: column; justify-content: flex-start;">
                    <span><b>Ping Drop</b></span>
                    <hr style="width: 100%" />
                    <StarlinkPingDrop chartWidth={Math.min(600, outerWidth - 100)} chartHeight=200 />
                </div>
            </div>
            <div style="display:flex; flex-flow: row; justify-content: space-around; flex-wrap: wrap;">
                <StarlinkFirmwareVersion />
                <StarlinkUpTime />
            </div>
        </div>
    {/if}

    {#if outages}
        <div style="display:flex; flex-flow: column; justify-content: flex-start">
            <StarlinkOutagesList />
            <div style="display:flex; flex-flow:row; justify-content: space-around">
                <StarlinkOutagesChart />
            </div>
            <div style="display:flex; flex-flow:row; justify-content: space-around">
                <StarlinkOutageDurationChart />
            </div>

        </div>
    {/if}

    {#if dishControl}
        <div style="display:flex; flex-flow: column; justify-content: space-evenly; gap: 20px;">
            <span><b>Antenna Orientation</b></span>
            <StarlinkAntenna />
            <span><b>Dishy Control</b></span>
            <StarlinkControls />
        </div>
    {/if}

    {#if rawData}
        <div style="display:flex; flex-flow: column; justify-content: flex-start">
            <StarlinkRawData />
        </div>
    {/if}
{/if}
{#if touchScreenStarlink}
    <div style="display:flex; flex-flow: column; justify-content: space-evenly; flex-wrap: wrap;">
        {#if touchStatus}
            <div style="display:flex; flex-flow: row; justify-content: space-evenly; flex-wrap: wrap;">
                <StarlinkStatusIndicator />
                <div style="display:flex; flex-flow: row; justify-content: space-evenly; gap: 50px">
                    <div style="display:flex; justify-content: center; flex-flow: column; align-items: center">
                        <span><b>Alerts</b></span>
                        <hr style="width: 100%"/>
                        <StarlinkAlerts />
                    </div>
                    <div style="display:flex; justify-content: flex-start; flex-flow: column; align-items: center; gap: 10px">
                        <span><b>Obstruction Map</b></span>
                        <StarlinkObstructionMap width=200 height=200 />
                    </div>
                </div>
            </div>
            <div style="display:flex; flex-flow: row; justify-content: space-around; flex-wrap: wrap;">
                <StarlinkFirmwareVersion />
                <StarlinkUpTime />
            </div>
        {/if}
        {#if touchSpeed}
            <div style="display:flex; flex-flow: column; justify-content: flex-start;">
                <span><b>Upload Speed</b></span>
                <hr style="width: 100%"/>
                <StarlinkUploadDataRates chartWidth={Math.min(600, outerWidth - 100)} chartHeight=160 />
            </div>
            <div style="display:flex; flex-flow: column; justify-content: flex-start;">
                <span><b>Download Speed</b></span>
                <hr style="width: 100%"/>
                <StarlinkDownloadDataRates chartWidth={Math.min(600, outerWidth - 100)} chartHeight=160 />
            </div>
        {/if}
        {#if touchQuality}
            <div style="display:flex; flex-flow: column; justify-content: flex-start;">
                <span><b>Ping Latency</b></span>
                <hr style="width: 100%"/>
                <StarlinkPingLatency chartWidth={Math.min(600, outerWidth - 100)} chartHeight=160 />
            </div>
            <div style="display:flex; flex-flow: column; justify-content: flex-start;">
                <span><b>Ping Drop</b></span>
                <hr style="width: 100%"/>
                <StarlinkPingDrop chartWidth={Math.min(600, outerWidth - 100)} chartHeight=160 />
            </div>
        {/if}
        {#if touchOutages}
            <div style="display:flex; flex-flow: column; justify-content: flex-start">
                <div style="display:flex; flex-flow:row; justify-content: space-around">
                    <StarlinkOutagesChart chartWidth={outerWidth - 20} chartHeight=200 />
                </div>
                <div style="display:flex; flex-flow:row; justify-content: space-around">
                    <StarlinkOutageDurationChart chartWidth={outerWidth - 20} chartHeight=200 />
                </div>

            </div>
        {/if}
        {#if touchControl}
            <div style="display:flex; flex-flow: column; justify-content: space-evenly; gap: 20px;">
                <span><b>Antenna Orientation</b></span>
                <StarlinkAntenna chartHeight="250" />
                <span><b>Dishy Control</b></span>
                <StarlinkControls />
            </div>
        {/if}
        <div style="display:flex; flex-flow: column; justify-content: flex-end">
            <div style="display:flex; flex-flow:row;justify-content: space-between;">
                <button class="tabButton"
                        on:click={()=> {touchStatus=true;touchSpeed=false;touchQuality=false;touchOutages=false;touchControl=false;}}>
                    Status
                </button>
                <button class="tabButton"
                        on:click={()=> {touchStatus=false;touchSpeed=true;touchQuality=false;touchOutages=false;touchControl=false;}}>
                    Speed
                </button>
                <button class="tabButton"
                        on:click={()=> {touchStatus=false;touchSpeed=false;touchQuality=true;touchOutages=false;touchControl=false;}}>
                    Quality
                </button>
                <button class="tabButton"
                        on:click={()=> {touchStatus=false;touchSpeed=false;touchQuality=false;touchOutages=true;touchControl=false;}}>
                    Outages
                </button>
                <button class="tabButton"
                        on:click={()=> {touchStatus=false;touchSpeed=false;touchQuality=false;touchOutages=false;touchControl=true;}}>
                    Control
                </button>
                <button class="tabButton"
                        on:click={()=> {touchStatus=true;touchSpeed=false;touchQuality=false;touchOutages=false;touchControl=false;touchScreenStarlink=false;fullScreenMenu=true}}>
                    ...
                </button>
            </div>
        </div>
    </div>
{/if}
{#if shellyPowerDisplay}
    <div style="display:flex; flex-flow: column; justify-content: space-between; height:100%">
        <ShellyDeviceList/>
        <div style="display:flex; flex-flow: column; justify-content: flex-end;'">
            <div style="display:flex; flex-flow:row;justify-content: space-between;">
                <button class="tabButton"
                        on:click={()=> {shellyPowerDisplay=false;fullScreenMenu=true;}}>
                    ...
                </button>
            </div>
         </div>
    </div>
{/if}
