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

    import {blueIrisAlert, lightningData, adsbData, newBirdAlert} from "./stores.svelte.js";
    import {currentView} from "./states.svelte.js";
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
    import BirdDashboard from "./components/bird/BirdDashboard.svelte";
    import BirdHistory from "./components/bird/BirdHistory.svelte";
    import BirdDetails from "./components/bird/BirdDetails.svelte";

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
    let lastNewBirdAlert = {};

    /**
     * Restore to the previous view only if the current view is the original calling view
     * @param callingView The popped up view that needs to be reset to the previous view
     * @param previousView The previous view to restore to before the popup happened.
     */
    function restoreView(callingView, previousView) {
        if (currentView.value !== callingView) {
            setTimeout(restoreView, 500, callingView, previousView);
        } else {
            currentView.value = previousView;
        }
    }

    /**
     * Cause the Blue iris alert to pop up and display the view of the new alert we have received
     */
    function displayBlueIrisAlert() {
        if (currentView.value !== 'alerts') {
            let previousView = currentView.value;
            currentView.value = 'alerts';
            setTimeout(restoreView, 30000, 'alerts', previousView);
        }
    }

    /**
     * Display a new ADSB alert of incoming plane
     */
    function displayADSBData() {
        if (currentView.value !== 'adsb') {
            let previousView = currentView.value;
            currentView.value = 'adsb';
            setTimeout(restoreView, 30000, 'adsb', previousView);
        }
    }

    /**
     * Cause the lightning alert screen to display the new lightning data we received
     */
    function displayLightningAlert() {
        if (currentView.value !== 'lightningDashboard') {
            let previousView = currentView.value;
            currentView.value = 'lightningDashboard';
            setTimeout(restoreView, 30000, 'lightningDashboard', previousView);
        }
    }

    /**
     * Cause the bird details screen to display the newly detected bird species
     */
    function displayNewBirdAlert(scientificName) {
        let birdView = 'bird_details_' + scientificName;
        if (currentView.value !== birdView) {
            let previousView = currentView.value;
            currentView.value = birdView;
            setTimeout(restoreView, 30000, birdView, previousView);
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
            if (alertAllowedViews.includes(currentView.value)) {
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
            if (alertAllowedViews.includes(currentView.value)) {
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
            alertAllowedViews.includes(currentView.value)) {
                displayLightningAlert();
        }
        lastLightningData = data;
    });

    /**
     * Monitor for any newly detected bird species that come in, and switch over to the bird details screen if we
     * receive a new one, and return to the previous screen after 30 seconds.
     */
    const unsubscribeNewBirdAlert = newBirdAlert.subscribe(data => {
        if (!lastNewBirdAlert.hasOwnProperty("id")) {
            lastNewBirdAlert = data;
        } else if (data.hasOwnProperty("id") && lastNewBirdAlert.id !== data.id) {
            lastNewBirdAlert = data;
            if (alertAllowedViews.includes(currentView.value) && data.scientific_name) {
                displayNewBirdAlert(data.scientific_name);
            }
        }
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
            if (!lastNewBirdAlert.hasOwnProperty("id")) {
                lastNewBirdAlert = {"id": "dummyid"};
            }
        }, 15000)
    })

    onDestroy(() => {
        unsubscribeBlueIris();
        unsubscribeLightningData();
        unsubscribeADSBData();
        unsubscribeNewBirdAlert();
    });

    function onKeyDown(event) {
        if (!event.repeat) {
            switch(event.key) {
                case "f":
                    currentView.value = "navigation";
                    break;
            }
        }
    }

    function onDoubleTap() {
        currentView.value = "navigation";
    }

</script>

<svelte:window bind:outerWidth bind:outerHeight bind:innerWidth on:keydown={onKeyDown}/>
<div role="application" style="display:flex; flex-flow: row; align-content: center; gap: 4px; width: 100%; height:{outerHeight}px; overflow: hidden;"
        on:dblclick={onDoubleTap}>
    {#if currentView.value === 'dashboard'}
        <MainDashboard></MainDashboard>
    {:else if graphViews.includes(currentView.value)}
        <div style="display:flex; flex-flow: column;justify-content: space-between; width: 100%; gap: 4px">
            <CurrentValues/>
            <div bind:clientWidth={graphWidth} bind:clientHeight={graphHeight} style="height: 100%; width:100%;">
                {#if currentView.value === 'voltageGraph'}
                    <VoltageGraph chartWidth={graphWidth} chartHeight={graphHeight - (outerHeight * 0.03)} />
                {/if}
                {#if currentView.value === 'loadGraph'}
                    <LoadGraph chartWidth={graphWidth} chartHeight={graphHeight - (outerHeight * 0.03)} />
                {/if}
                {#if currentView.value === 'solarWattsGraph'}
                    <SolarWattsGraph chartWidth={graphWidth} chartHeight={graphHeight - (outerHeight * 0.03)} />
                {/if}
                {#if currentView.value === 'batteryWattsGraph'}
                    <BatteryWattsGraph chartWidth={graphWidth} chartHeight={graphHeight - (outerHeight * 0.03)} />
                {/if}
                {#if currentView.value === 'statistics'}
                    <Statistics />
                {/if}
                {#if currentView.value === 'outTempGraph'}
                    <OutdoorTemperatureGraph chartWidth={graphWidth} chartHeight={graphHeight - (outerHeight * 0.03)} />
                {/if}
                {#if currentView.value === 'inTempGraph'}
                    <IndoorTemperatureGraph chartWidth={graphWidth} chartHeight={graphHeight - (outerHeight * 0.03)} />
                {/if}
                {#if currentView.value === 'windGraph'}
                    <WindGraph chartWidth={graphWidth} chartHeight={graphHeight - (outerHeight * 0.03)} />
                {/if}
                {#if currentView.value === 'batteryBankVoltageGraph'}
                    <BatteryBankVoltageGraph chartWidth={graphWidth} chartHeight={graphHeight - (outerHeight * 0.03)} />
                {/if}
                {#if currentView.value === 'batteryCellPressureGraph'}
                    <BatteryBankCellPressureDiffGraph chartWidth={graphWidth} chartHeight={graphHeight - (outerHeight * 0.03)} />
                {/if}
                {#if currentView.value === 'batteryBankTemperatureGraph'}
                    <BatteryBankTemperatureGraph chartWidth={graphWidth} chartHeight={graphHeight - (outerHeight * 0.03)} />
                {/if}
            </div>
        </div>
    {/if}
    {#if currentView.value === 'starlinkStatus'}
        <StarlinkStatus />
    {/if}
    {#if currentView.value === 'starlinkOutages'}
        <div role="button" tabindex="0" style="display:flex; flex-flow: column; justify-content: flex-start; width: 100%;" on:click={() => currentView.value = 'dashboard'} on:keydown={(event) => (event.key === 'Enter' || event.key === ' ') && (currentView.value = 'dashboard')}>
            <StarlinkOutageDurationChart chartWidth={outerWidth - (outerWidth * 0.1)} chartHeight={outerHeight - (outerHeight * 0.1)}/>
        </div>
    {/if}
    {#if currentView.value === 'starlinkSpeedGraphs'}
        <div role="button" tabindex="0" style="display:flex; flex-flow: column; justify-content: flex-start; width: 100%;" on:click={() => currentView.value = 'dashboard'} on:keydown={(event) => (event.key === 'Enter' || event.key === ' ') && (currentView.value = 'dashboard')}>
            <StarlinkUploadDataRates chartWidth={outerWidth - (outerWidth * 0.1)} chartHeight={(outerHeight / 2) - (outerHeight * 0.1)} />
            <StarlinkDownloadDataRates chartWidth={outerWidth - (outerWidth * 0.1)} chartHeight={(outerHeight / 2) - (outerHeight * 0.1)} />
        </div>
    {/if}
    {#if currentView.value === 'starlinkPingGraphs'}
        <div role="button" tabindex="0" style="display:flex; flex-flow: column; justify-content: flex-start; width: 100%;" on:click={() => currentView.value = 'dashboard'} on:keydown={(event) => (event.key === 'Enter' || event.key === ' ') && (currentView.value = 'dashboard')}>
            <StarlinkPingLatency chartWidth={outerWidth - (outerWidth * 0.15)} chartHeight={(outerHeight / 2) - (outerHeight * 0.15)} />
            <StarlinkPingDrop chartWidth={outerWidth - (outerWidth * 0.15)} chartHeight={(outerHeight / 2) - (outerHeight * 0.15)} />
        </div>
    {/if}
    {#if currentView.value === 'starlinkPowerGraphs'}
        <div role="button" tabindex="0" style="display:flex; flex-flow: column; justify-content: flex-start; width: 100%;" on:click={() => currentView.value = 'dashboard'} on:keydown={(event) => (event.key === 'Enter' || event.key === ' ') && (currentView.value = 'dashboard')}>
            <StarlinkPower chartWidth={outerWidth - (outerWidth * 0.15)} chartHeight={(outerHeight) - (outerHeight * 0.15)} />
        </div>
    {/if}
    {#if currentView.value === 'shelley'}
        <div role="button" tabindex="0" style="display:flex; flex-flow: column; justify-content: space-between; height:100%; flex-grow: 9;"
             on:click={() => currentView.value = 'dashboard'} on:keydown={(event) => (event.key === 'Enter' || event.key === ' ') && (currentView.value = 'dashboard')}>
            <ShellyDeviceList/>
        </div>
    {/if}
    {#if currentView.value === 'alerts'}
        <BlueIrisAlert />
    {/if}
    {#if currentView.value === 'adsb'}
        <ADSBInfo />
    {/if}
    {#if currentView.value === 'weather'}
        <WxDashboard />
    {/if}
    {#if currentView.value === 'navigation'}
        <MainNavigation />
    {/if}
    {#if currentView.value === 'battery_dashboard'}
        <BatteryDashboard />
    {/if}
    {#if currentView.value.startsWith('battery_details_')}
        <BatteryDetails />
    {/if}
    {#if currentView.value.startsWith('battery_cell_graph_')}
        <BatteryCellVoltageGraph />
    {/if}
    {#if currentView.value === 'lightningDashboard'}
        <LightningDashboard />
    {/if}
    {#if currentView.value === 'birdDashboard'}
        <BirdDashboard />
    {/if}
    {#if currentView.value === 'birdHistory'}
        <BirdHistory />
    {/if}
    {#if currentView.value.startsWith('bird_details_')}
        <BirdDetails />
    {/if}
</div>



