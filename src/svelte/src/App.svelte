<script>
    import {onDestroy, onMount} from "svelte";
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

    import {blueIrisAlert, currentView, lightningData, adsbData} from "./stores";
    import MainDashboard from "./components/dahsboards/MainDashboard.svelte";
    import StarlinkStatus from "./components/starlink/StarlinkStatus.svelte";
    import WxDashboard from "./components/weather/WxDashboard.svelte";
    import MainNavigation from "./components/navigation/MainNavigation.svelte";
    import StarlinkOutageDurationChart from "./components/starlink/StarlinkOutageDurationChart.svelte";
    import OutdoorTemperatureGraph from "./components/weather/OutdoorTemperatureGraph.svelte";
    import IndoorTemperatureGraph from "./components/weather/IndoorTemperatureGraph.svelte";
    import WindGraph from "./components/weather/WindGraph.svelte";
    import BatteryDashboard from "./components/battery/BatteryDashboard.svelte";
    import BatteryDetails from "./components/battery/BatteryDetails.svelte";
    import BatteryBankVoltageGraph from "./components/battery/BatteryBankVoltageGraph.svelte";
    import BatteryCellVoltageGraph from "./components/battery/BatteryCellVoltageGraph.svelte";
    import BatteryBankCellPressureDiffGraph from "./components/battery/BatteryBankCellPressureDiffGraph.svelte";
    import BatteryBankTemperatureGraph from "./components/battery/BatteryBankTemperatureGraph.svelte";
    import LightningDashboard from "./components/lightning/LightningDashboard.svelte";
    import ADSBInfo from "./components/adsb/ADSBInfo.svelte";
    import StarlinkPower from "./components/starlink/StarlinkPower.svelte";

    let innerWidth = 0;
    let outerWidth = 0
    let outerHeight = 0
    let graphWidth, graphHeight;
    let graphViews = ['voltageGraph', 'loadGraph', 'solarWattsGraph', 'batteryWattsGraph', 'statistics', 'outTempGraph',
                        'inTempGraph', 'windGraph', 'batteryBankVoltageGraph', 'batteryCellPressureGraph', 'batteryBankTemperatureGraph'];
    let alertAllowedViews = ['dashboard', 'alerts', 'adsb', 'lightningDashboard'];
    let lastBlueIrisAlert = {};
    let lastADSBData = {};
    let lastLightningData = {};

    /**
     * Restore to the previous view only if the current view is the original calling view
     * @param callingView The popped up view that needs to be reset to the previous view
     * @param previousView The previous view to restore to before the popup happened.
     */
    function restoreView(callingView, previousView) {
        if ($currentView !== callingView) {
            setTimeout(restoreView, 500, callingView, previousView);
        } else {
            $currentView = previousView;
        }
    }

    /**
     * Cause the Blue iris alert to pop up and display the view of the new alert we have received
     */
    function displayBlueIrisAlert() {
        if ($currentView !== 'alerts') {
            let previousView = $currentView;
            $currentView = 'alerts';
            setTimeout(restoreView, 30000, 'alerts', previousView);
        }
    }

    /**
     * Display a new ADSB alert of incoming plane
     */
    function displayADSBData() {
        if ($currentView !== 'adsb') {
            let previousView = $currentView;
            $currentView = 'adsb';
            setTimeout(restoreView, 30000, 'adsb', previousView);
        }
    }

    /**
     * Cause the lightning alert screen to display the new lightning data we received
     */
    function displayLightningAlert() {
        if ($currentView !== 'lightningDashboard') {
            let previousView = $currentView;
            $currentView = 'lightningDashboard';
            setTimeout(restoreView, 30000, 'lightningDashboard', previousView);
        }
    }

    /**
     * Monitor for any new blue iris alerts that come in, and switch over to the alert screen if we receive a new one,
     * and return to the previous screen after 30 seconds.
     */
    const unsubscribeBlueIris = blueIrisAlert.subscribe(data => {
        if (!lastBlueIrisAlert.hasOwnProperty("id")) {
            lastBlueIrisAlert = data;
        } else if (data.hasOwnProperty("id") && lastBlueIrisAlert.id !== data.id) {
            lastBlueIrisAlert = data;
            if (alertAllowedViews.includes($currentView)) {
                displayBlueIrisAlert()
            }
        }
    });

    /**
     * Monitor for any new adsb flight data that come in, and switch over to the alert screen if we receive a new one,
     * and return to the previous screen after 30 seconds.
     */
    const unsubscribeADSBData = adsbData.subscribe(data => {
        if (!lastADSBData.hasOwnProperty("id")) {
            lastADSBData = data;
        } else if (data.hasOwnProperty("id") && lastADSBData.id !== data.id) {
            lastADSBData = data;
            if (alertAllowedViews.includes($currentView)) {
                displayADSBData();
            }
        }
    });

    /**
     * If we receive new lightning data and it is not due to not having any data, display the new data and update the
     * last value.
     */
    const unsubscribeLightningData = lightningData.subscribe(data => {
        if (lastLightningData.hasOwnProperty("last_strike_24hr") &&
            data.hasOwnProperty("last_strike_24hr") &&
            data?.last_strike_24hr?.hasOwnProperty("intensity") &&
            data?.last_strike_24hr?.intensity != lastLightningData?.last_strike_24hr?.intensity &&
            alertAllowedViews.includes($currentView)) {
                displayLightningAlert();
        }
        lastLightningData = data;
    });

    /**
     * If there is not any currently defined alerts on the server after a delay to let it try and get the latest one,
     * then set a dummy id so that we do receive the first real alert to come in.
     */
    onMount(() => {
        setTimeout(() => {
            if (!lastBlueIrisAlert.hasOwnProperty("id")) {
                lastBlueIrisAlert = {"id": "dummyid"};
            }
            if (!lastADSBData.hasOwnProperty("id")) {
                lastADSBData = {"id": "dummyid"};
            }
        }, 15000)
    })

    onDestroy(() => {
        unsubscribeBlueIris();
        unsubscribeLightningData();
        unsubscribeADSBData();
    });

    function onKeyDown(event) {
        if (!event.repeat) {
            switch(event.key) {
                case "f":
                    $currentView = "navigation";
                    break;
            }
        }
    }

    function onDoubleTap() {
        $currentView = "navigation";
    }

</script>

<svelte:window bind:outerWidth bind:outerHeight bind:innerWidth on:keydown={onKeyDown}/>
<div style="display:flex; flex-flow: row; align-content: center; gap: 20px; width: 100%; height:{outerHeight - (outerHeight * 0.05)}px;"
        on:dblclick={onDoubleTap}>
    {#if $currentView === 'dashboard'}
        <MainDashboard></MainDashboard>
    {:else if graphViews.includes($currentView)}
        <div style="display:flex; flex-flow: column;justify-content: space-between; width: 100%; gap: 10px">
            <CurrentValues/>
            <div bind:clientWidth={graphWidth} bind:clientHeight={graphHeight} style="height: 100%; width:100%;">
                {#if $currentView === 'voltageGraph'}
                    <VoltageGraph chartWidth={graphWidth} chartHeight={graphHeight - (outerHeight * 0.03)} />
                {/if}
                {#if $currentView === 'loadGraph'}
                    <LoadGraph chartWidth={graphWidth} chartHeight={graphHeight - (outerHeight * 0.03)} />
                {/if}
                {#if $currentView === 'solarWattsGraph'}
                    <SolarWattsGraph chartWidth={graphWidth} chartHeight={graphHeight - (outerHeight * 0.03)} />
                {/if}
                {#if $currentView === 'batteryWattsGraph'}
                    <BatteryWattsGraph chartWidth={graphWidth} chartHeight={graphHeight - (outerHeight * 0.03)} />
                {/if}
                {#if $currentView === 'statistics'}
                    <Statistics />
                {/if}
                {#if $currentView === 'outTempGraph'}
                    <OutdoorTemperatureGraph chartWidth={graphWidth} chartHeight={graphHeight - (outerHeight * 0.03)} />
                {/if}
                {#if $currentView === 'inTempGraph'}
                    <IndoorTemperatureGraph chartWidth={graphWidth} chartHeight={graphHeight - (outerHeight * 0.03)} />
                {/if}
                {#if $currentView === 'windGraph'}
                    <WindGraph chartWidth={graphWidth} chartHeight={graphHeight - (outerHeight * 0.03)} />
                {/if}
                {#if $currentView === 'batteryBankVoltageGraph'}
                    <BatteryBankVoltageGraph chartWidth={graphWidth} chartHeight={graphHeight - (outerHeight * 0.03)} />
                {/if}
                {#if $currentView === 'batteryCellPressureGraph'}
                    <BatteryBankCellPressureDiffGraph chartWidth={graphWidth} chartHeight={graphHeight - (outerHeight * 0.03)} />
                {/if}
                {#if $currentView === 'batteryBankTemperatureGraph'}
                    <BatteryBankTemperatureGraph chartWidth={graphWidth} chartHeight={graphHeight - (outerHeight * 0.03)} />
                {/if}
            </div>
        </div>
    {/if}
    {#if $currentView === 'starlinkStatus'}
        <StarlinkStatus />
    {/if}
    {#if $currentView === 'starlinkOutages'}
        <div style="display:flex; flex-flow: column; justify-content: flex-start; width: 100%;" on:click={() => $currentView = 'dashboard'}>
            <StarlinkOutageDurationChart chartWidth={outerWidth - (outerWidth * 0.1)} chartHeight={outerHeight - (outerHeight * 0.1)}/>
        </div>
    {/if}
    {#if $currentView === 'starlinkSpeedGraphs'}
        <div style="display:flex; flex-flow: column; justify-content: flex-start; width: 100%;" on:click={() => $currentView = 'dashboard'}>
            <StarlinkUploadDataRates chartWidth={outerWidth - (outerWidth * 0.1)} chartHeight={(outerHeight / 2) - (outerHeight * 0.1)} />
            <StarlinkDownloadDataRates chartWidth={outerWidth - (outerWidth * 0.1)} chartHeight={(outerHeight / 2) - (outerHeight * 0.1)} />
        </div>
    {/if}
    {#if $currentView === 'starlinkPingGraphs'}
        <div style="display:flex; flex-flow: column; justify-content: flex-start; width: 100%;" on:click={() => $currentView = 'dashboard'}>
            <StarlinkPingLatency chartWidth={outerWidth - (outerWidth * 0.15)} chartHeight={(outerHeight / 2) - (outerHeight * 0.15)} />
            <StarlinkPingDrop chartWidth={outerWidth - (outerWidth * 0.15)} chartHeight={(outerHeight / 2) - (outerHeight * 0.15)} />
        </div>
    {/if}
    {#if $currentView === 'starlinkPowerGraphs'}
        <div style="display:flex; flex-flow: column; justify-content: flex-start; width: 100%;" on:click={() => $currentView = 'dashboard'}>
            <StarlinkPower chartWidth={outerWidth - (outerWidth * 0.15)} chartHeight={(outerHeight) - (outerHeight * 0.15)} />
        </div>
    {/if}
    {#if $currentView === 'shelley'}
        <div style="display:flex; flex-flow: column; justify-content: space-between; height:100%; flex-grow: 9;"
             on:click={() => $currentView = 'dashboard'}>
            <ShellyDeviceList/>
        </div>
    {/if}
    {#if $currentView === 'alerts'}
        <BlueIrisAlert />
    {/if}
    {#if $currentView === 'adsb'}
        <ADSBInfo />
    {/if}
    {#if $currentView === 'weather'}
        <WxDashboard />
    {/if}
    {#if $currentView === 'navigation'}
        <MainNavigation />
    {/if}
    {#if $currentView === 'battery_dashboard'}
        <BatteryDashboard />
    {/if}
    {#if $currentView.startsWith('battery_details_')}
        <BatteryDetails />
    {/if}
    {#if $currentView.startsWith('battery_cell_graph_')}
        <BatteryCellVoltageGraph />
    {/if}
    {#if $currentView === 'lightningDashboard'}
        <LightningDashboard />
    {/if}
</div>
