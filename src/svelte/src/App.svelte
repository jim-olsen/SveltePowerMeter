<script>
    import {onDestroy} from "svelte";
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
    import BlueIrisAlert from "./components/blueiris/BlueIrisAlert.svelte";

    import {blueIrisAlert, currentView} from "./stores";
    import MainDashboard from "./components/dahsboards/MainDashboard.svelte";

    let innerWidth = 0;
    let outerWidth = 0
    let outerHeight = 0
    let stats = true;

    let powerView = 'stats';
    let touchStarlinkView = 'status';
    let lastBlueIrisAlert = {}

    /**
     * Monitor for any new blue iris alerts that come in, and switch over to the alert screen if we receive a new one,
     * and return to the previous screen after 30 seconds.
     */
    const unsubscribeBlueIris = blueIrisAlert.subscribe(data => {
        if (!lastBlueIrisAlert.hasOwnProperty("id")) {
            lastBlueIrisAlert = data;
        } else if (data.hasOwnProperty("id") && lastBlueIrisAlert.id !== data.id) {
            lastBlueIrisAlert = data;
            if ($currentView !== 'alerts') {
                let returnView = $currentView;
                currentView.set('alerts');
                setTimeout(() => {
                    currentView.set(returnView)
                }, 30000);
            }
        }
    });

    onDestroy(() => {
        unsubscribeBlueIris();
    });

    let graphWidth, graphHeight, obstructionMapWidth;
    let graphViews = ['voltageGraph', 'loadGraph', 'solarWattsGraph', 'batteryWattsGraph', 'statistics'];
</script>

<svelte:window bind:outerWidth bind:outerHeight bind:innerWidth/>
<div style="display:flex; flex-flow: row; gap: 20px; width: 100%; height:{outerHeight - (outerHeight * 0.05)}px;">
    {#if $currentView === 'dashboard'}
        <MainDashboard></MainDashboard>
    {:else if graphViews.includes($currentView)}
        <div style="display:flex; flex-flow: column;justify-content: space-between; width: 100%;">
            <CurrentValues/>
            <div bind:clientWidth={graphWidth} bind:clientHeight={graphHeight} style="height: 100%; width:100%;">
                {#if $currentView === 'voltageGraph'}
                    <VoltageGraph chartWidth={graphWidth - (outerWidth * 0.05)} chartHeight={graphHeight - (outerHeight * 0.03)} />
                {/if}
                {#if $currentView === 'loadGraph'}
                    <LoadGraph chartWidth={graphWidth - (outerWidth * 0.05)} chartHeight={graphHeight - (outerHeight * 0.03)} />
                {/if}
                {#if $currentView === 'solarWattsGraph'}
                    <SolarWattsGraph chartWidth={graphWidth - (outerWidth * 0.05)} chartHeight={graphHeight - (outerHeight * 0.03)} />
                {/if}
                {#if $currentView === 'batteryWattsGraph'}
                    <BatteryWattsGraph chartWidth={graphWidth - (outerWidth * 0.05)} chartHeight={graphHeight - (outerHeight * 0.03)} />
                {/if}
                {#if $currentView === 'statistics'}
                    <Statistics />
                {/if}
            </div>
        </div>
    {/if}
    {#if $currentView === 'starlinkStatus'}
        <div style="display:flex; flex-flow: column; justify-content: space-between; width: 100%;" on:click={() => currentView.set('dashboard')}>
            <div style="display:flex; flex-flow: row; justify-content: space-evenly; align-items: center; flex: 9;">
                <div style="display:flex; flex-flow: column; justify-content: space-between; gap: 20px">
                    <StarlinkStatusIndicator/>
                    <div style="display:flex; justify-content: center; flex-flow: column; align-items: center;gap: 10px">
                        <span class="smallText"><b>Alerts</b></span>
                        <StarlinkAlerts/>
                    </div>
                </div>
                <div style="display:flex; justify-content: flex-start; flex-flow: column; align-items: center; gap: 10px"
                        bind:clientWidth={obstructionMapWidth}>
                    <span class="smallText"><b>Obstruction Map</b></span>
                    <StarlinkObstructionMap width={obstructionMapWidth} height={obstructionMapWidth}/>
                </div>
            </div>
            <div style="display:flex; flex-flow: row; justify-content: space-around; flex-wrap: wrap; flex: 1;">
                <StarlinkFirmwareVersion/>
                <StarlinkUpTime/>
            </div>
        </div>
    {/if}
    {#if $currentView === 'starlinkSpeedGraphs'}
        <div style="display:flex; flex-flow: column; justify-content: flex-start; width: 100%;" on:click={() => currentView.set('dashboard')}>
            <StarlinkUploadDataRates chartWidth={outerWidth - (outerWidth * 0.1)} chartHeight={(outerHeight / 2) - (outerHeight * 0.1)} />
            <StarlinkDownloadDataRates chartWidth={outerWidth - (outerWidth * 0.1)} chartHeight={(outerHeight / 2) - (outerHeight * 0.1)} />
        </div>
    {/if}
    {#if $currentView === 'starlinkPingGraphs'}
        <div style="display:flex; flex-flow: column; justify-content: flex-start; width: 100%;" on:click={() => currentView.set('dashboard')}>
            <StarlinkPingLatency chartWidth={outerWidth - (outerWidth * 0.1)} chartHeight={(outerHeight / 2) - (outerHeight * 0.1)} />
            <StarlinkPingDrop chartWidth={outerWidth - (outerWidth * 0.1)} chartHeight={(outerHeight / 2) - (outerHeight * 0.1)} />
        </div>
    {/if}
    {#if $currentView === 'shelley'}
        <div style="display:flex; flex-flow: column; justify-content: space-between; height:100%; flex-grow: 9;">
            <ShellyDeviceList/>
        </div>
    {/if}
    {#if $currentView === 'alerts'}
        <BlueIrisAlert />
    {/if}
</div>
