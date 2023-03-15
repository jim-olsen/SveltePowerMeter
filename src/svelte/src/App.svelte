<script>
    import {onDestroy} from "svelte";
    import StarlinkUploadDataRates from "./components/starlink/StarlinkUploadDataRates.svelte"
    import StarlinkDownloadDataRates from "./components/starlink/StarlinkDownloadDataRates.svelte"
    import StarlinkPingLatency from "./components/starlink/StarlinkPingLatency.svelte";
    import StarlinkPingDrop from "./components/starlink/StarlinkPingDrop.svelte"
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
    import StarlinkStatus from "./components/starlink/StarlinkStatus.svelte";
    import WxDashboard from "./components/weather/WxDashboard.svelte";

    let innerWidth = 0;
    let outerWidth = 0
    let outerHeight = 0
    let stats = true;

    let powerView = 'stats';
    let touchStarlinkView = 'status';
    let lastBlueIrisAlert = { "id" : ""}

    /**
     * Cause the Blue iris alert to pop up and display the view of the new alert we have received
     */
    function displayBlueIrisAlert() {
        if ($currentView !== 'alerts') {
            let returnView = $currentView;
            currentView.set('alerts');
            setTimeout(() => {
                currentView.set(returnView)
            }, 30000);
        }
    }

    /**
     * Monitor for any new blue iris alerts that come in, and switch over to the alert screen if we receive a new one,
     * and return to the previous screen after 30 seconds.
     */
    const unsubscribeBlueIris = blueIrisAlert.subscribe(data => {
        if (!lastBlueIrisAlert.hasOwnProperty("id")) {
            lastBlueIrisAlert = data;
            displayBlueIrisAlert();
        } else if (data.hasOwnProperty("id") && lastBlueIrisAlert.id != "" && lastBlueIrisAlert.id !== data.id) {
            lastBlueIrisAlert = data;
            displayBlueIrisAlert();
        }
    });

    onDestroy(() => {
        unsubscribeBlueIris();
    });

    let graphWidth, graphHeight;
    let graphViews = ['voltageGraph', 'loadGraph', 'solarWattsGraph', 'batteryWattsGraph', 'statistics'];
</script>

<svelte:window bind:outerWidth bind:outerHeight bind:innerWidth/>
<div style="display:flex; flex-flow: row; align-content: center; gap: 20px; width: 100%; height:{outerHeight - (outerHeight * 0.05)}px;">
    {#if $currentView === 'dashboard'}
        <MainDashboard></MainDashboard>
    {:else if graphViews.includes($currentView)}
        <div style="display:flex; flex-flow: column;justify-content: space-between; width: 100%; gap: 10px">
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
        <StarlinkStatus />
    {/if}
    {#if $currentView === 'starlinkSpeedGraphs'}
        <div style="display:flex; flex-flow: column; justify-content: flex-start; width: 100%;" on:click={() => currentView.set('dashboard')}>
            <StarlinkUploadDataRates chartWidth={outerWidth - (outerWidth * 0.1)} chartHeight={(outerHeight / 2) - (outerHeight * 0.1)} />
            <StarlinkDownloadDataRates chartWidth={outerWidth - (outerWidth * 0.1)} chartHeight={(outerHeight / 2) - (outerHeight * 0.1)} />
        </div>
    {/if}
    {#if $currentView === 'starlinkPingGraphs'}
        <div style="display:flex; flex-flow: column; justify-content: flex-start; width: 100%;" on:click={() => currentView.set('dashboard')}>
            <StarlinkPingLatency chartWidth={outerWidth - (outerWidth * 0.15)} chartHeight={(outerHeight / 2) - (outerHeight * 0.15)} />
            <StarlinkPingDrop chartWidth={outerWidth - (outerWidth * 0.15)} chartHeight={(outerHeight / 2) - (outerHeight * 0.15)} />
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
    {#if $currentView === 'weather'}
        <WxDashboard />
    {/if}
</div>
