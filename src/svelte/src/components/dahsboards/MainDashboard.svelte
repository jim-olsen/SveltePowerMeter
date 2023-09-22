<script xmlns="http://www.w3.org/1999/html">
    import {onDestroy} from 'svelte'
    import Fa from "svelte-fa";
    import {faCarBattery, faSnowflake, faSatelliteDish, faSun, faCloudMoon} from "@fortawesome/free-solid-svg-icons";

    import {powerCurrentData, powerStatsData, weatherData, starlinkStatus, starlinkHistory, currentView} from "../../stores";

    let starlinkHistoryData = {};
    let batteryIcon, sunIcon;

    const unsubscribeStarlinkHistory = starlinkHistory.subscribe(data => {
        starlinkHistoryData = data;
        if (batteryIcon) {
            batteryIcon.style.color = getChargeStateColor();
        }
        if (sunIcon) {
            setChargeStateClass(sunIcon);
        }
    });

    onDestroy(() => {
        unsubscribeStarlinkHistory();
    });

    function getChargeStateColor() {
        if (isFloating()) {
            return 'lightgreen';
        } else if ($powerCurrentData.charge_state === 'ABSORB') {
            return 'yellow';
        } else {
            return 'orangered';
        }
    }

    function isCharging() {
        return $powerCurrentData.charge_state === 'ABSORB' || $powerCurrentData.charge_state === 'MPPT';
    }

    function isFloating() {
        return $powerCurrentData.charge_state === 'FLOAT';
    }

    function setChargeStateClass(element) {
        if (isFloating()) {
            element.classList.remove('icon-spinner');
            element.classList.add('icon-pulser')
        } else if (isCharging()) {
            element.classList.remove('icon-pulser');
            element.classList.add('icon-spinner');
        } else {
            element.classList.remove('icon-pulser');
            element.classList.remove('icon-spinner');
        }
    }

</script>
<div style="display:flex; flex-flow:column; justify-content: space-evenly; align-items: flex-start; width: 100%; gap: 5px;">
    <div style="display:flex; flex-flow:row; justify-content: space-between; width: 100%;" class="card">
        {#if $powerCurrentData && (isCharging() || isFloating())}
            <div bind:this={sunIcon} style="display:flex; flex-flow: row; justify-content: center; align-items: center; flex: 1; color: yellow; font-size: 6vh;"
                     on:click={()=>$currentView = 'statistics'}>
                <Fa icon="{faSun}" style="font-size: 6vw;"/>
            </div>
        {:else}
            <div style="display:flex; flex-flow: row; justify-content: center; align-items: center; flex: 1; color: grey; font-size: 6vh;"
                 on:click={()=> $currentView = 'statistics'}>
                <Fa id="moonNightIcon" icon="{faCloudMoon}"  style="font-size: 6vw;"/>
            </div>
        {/if}
        <div style="display:flex; flex-flow:row; justify-content: flex-end; align-items: flex-end; flex: 2; gap: 10px;"
                on:click={() => $currentView = 'loadGraph'}>
            <span class="largeText">{$powerCurrentData?.load_amps ? ($powerCurrentData?.load_amps * $powerCurrentData?.battery_voltage)?.toFixed(1) : '---'}</span>
            <div style="display:flex; flex-flow:column; justify-content: stretch;">
                <span class="smallText">Load</span>
                <span class="smallText">Watts</span>
            </div>
        </div>
        <div style="display:flex; flex-flow:row; justify-content: flex-end; align-items: flex-end; flex: 2; gap: 10px;"
                on:click={()=> $currentView = 'solarWattsGraph'}>
            <span class="largeText">{$powerCurrentData?.solar_watts ? $powerCurrentData?.solar_watts.toFixed(1) : '---'}</span>
            <div style="display:flex; flex-flow:column; justify-content: stretch;">
                <span class="smallText">Solar</span>
                <span class="smallText">Watts</span>
            </div>
        </div>
        <div style="display:flex; flex-flow:row; justify-content: flex-end; align-items: flex-end; flex: 2; gap: 10px;">
            <span class="largeText">{$powerStatsData?.day_solar_wh ? $powerStatsData?.day_solar_wh.toFixed(1) : '---'}</span>
            <div style="display:flex; flex-flow:column; justify-content: stretch;">
                <span class="smallText">Solar</span>
                <span class="smallText">WH</span>
            </div>
        </div>
    </div>
    <div style="display:flex; flex-flow:row; justify-content: space-between; width: 100%;" class="card">
        <div bind:this={batteryIcon} style="display:flex; flex-flow: row; justify-content: center; align-items: center; flex: 1; font-size: 6vh;"
                on:click={()=> $currentView = 'battery_dashboard'}>
            <Fa icon="{faCarBattery}" style="font-size: 6vw;" />
        </div>
        <div style="display:flex; flex-flow:row; justify-content: flex-end; align-items: flex-end; flex: 2; gap: 10px;"
                on:click={()=> $currentView = 'voltageGraph'}>
            <span class="largeText">{$powerCurrentData?.battery_percent ? ($powerCurrentData?.battery_percent)?.toFixed(2) : '---'}</span>
            <div style="display:flex; flex-flow:column; justify-content: stretch;">
                <span class="smallText">{$powerStatsData?.battery_min_percent ? ($powerStatsData?.battery_min_percent)?.toFixed(2) : '---'}%</span>
                <span class="smallText">{$powerStatsData?.battery_max_percent ? ($powerStatsData?.battery_max_percent)?.toFixed(2) : '---'}%</span>
                <span class="smallText">Batt&nbsp%</span>
            </div>
        </div>
        <div style="display:flex; flex-flow:row; justify-content: flex-end; align-items: flex-end; flex: 2; gap: 10px;"
                on:click={() => $currentView = 'batteryWattsGraph'}>
            <span class="largeText">{$powerStatsData?.day_batt_wh ? $powerStatsData?.day_batt_wh?.toFixed(1) : '---'}</span>
            <div style="display:flex; flex-flow:column; justify-content: stretch;">
                <span class="smallText">Batt</span>
                <span class="smallText">WH</span>
            </div>
        </div>
        <div style="display:flex; flex-flow:row; justify-content: flex-end; align-items: flex-end; flex: 2; gap: 10px;">
            <span class="largeText">{$powerStatsData?.day_load_wh ? $powerStatsData?.day_load_wh?.toFixed(1) : '---'}</span>
            <div style="display:flex; flex-flow:column; justify-content: stretch;">
                <span class="smallText">Load</span>
                <span class="smallText">WH</span>
            </div>
        </div>
    </div>
    <div style="display:flex; flex-flow:row; justify-content: space-between; width: 100%;" class="card">
        <div style="display:flex; flex-flow: row; justify-content: center; align-items: center; flex: 1; color: slateblue; font-size: 6vh;"
             on:click={()=> $currentView = 'weather'}>
            <Fa icon="{faSnowflake}" style="font-size: 6vw;"/>
        </div>
        <div  on:click={()=> $currentView = 'outTempGraph'} style="display:flex; flex-flow:row; justify-content: flex-end; align-items: flex-end; flex: 2; gap: 10px;">
            <span class="largeText">{$weatherData?.outTemp_F ? Number($weatherData?.outTemp_F)?.toFixed(1) + ' F' : '---'}</span>
            <div style="display:flex; flex-flow:column; justify-content: stretch;">
                <span class="smallText">Out</span>
                <span class="smallText">Temp</span>
            </div>
        </div>
        <div on:click={()=> $currentView = 'inTempGraph'} style="display:flex; flex-flow:row; justify-content: flex-end; align-items: flex-end; flex: 2; gap: 10px;">
            <span class="largeText">{$weatherData?.inTemp_F ? Number($weatherData?.inTemp_F)?.toFixed(1) + ' F' : '---'}</span>
            <div style="display:flex; flex-flow:column; justify-content: stretch;">
                <span class="smallText">In</span>
                <span class="smallText">Temp</span>
            </div>
        </div>
        <div on:click={()=> $currentView = 'windGraph'} style="display:flex; flex-flow:row; justify-content: flex-end; align-items: flex-end; flex: 2; gap: 10px;">
            <span class="largeText">{$weatherData?.wind_average ? Number($weatherData?.wind_average)?.toFixed(1) : '---'}</span>
            <div style="display:flex; flex-flow:column; justify-content: stretch;">
                <span class="smallText">Wind</span>
                <span class="smallText">Avg</span>
            </div>
        </div>
    </div>
    <div style="display:flex; flex-flow:row; justify-content: space-between; width: 100%;" class="card">
        <div on:click={()=> $currentView = 'starlinkStatus'} style="display:flex; flex-flow: row; justify-content: center; align-items: center; flex: 1; color: slategray; font-size: 6vh;">
            <Fa icon="{faSatelliteDish}" style="font-size: 6vw;"/>
        </div>
        <div style="display:flex; flex-flow: column; flex: 2;">
            <div style="display:flex; flex-flow:row; justify-content: flex-end; align-items: flex-end;" on:click={()=> $currentView = 'starlinkOutages'}>
                <span class="normalText" style="color: {$starlinkStatus?.state === 'CONNECTED' ? 'greenyellow' : 'orangered'};">{$starlinkStatus?.state ? $starlinkStatus.state : 'UNKNOWN'}</span>
            </div>
            <div style="display:flex; flex-flow:row; justify-content: flex-end; align-items: flex-end;">
                <span class="normalText">Heater <span style="color: {$starlinkStatus?.alerts?.is_heating ? 'red' : 'greenyellow'};">{$starlinkStatus?.alerts?.is_heating ? 'On' : 'Off'}</span></span>
            </div>
        </div>
        <div style="display:flex; flex-flow: column; flex: 2;" on:click={()=> $currentView = 'starlinkSpeedGraphs'}>
            <div style="display:flex; flex-flow:row; justify-content: flex-end; align-items: flex-end; gap: 10px;">
                <span class="normalText" >{$starlinkStatus?.downlink_throughput_bps ? ($starlinkStatus?.downlink_throughput_bps / 1000000)?.toFixed(2) : '---'}</span>
                <div style="display:flex; flex-flow:column; justify-content: stretch;">
                    <span class="smallText">Down</span>
                    <span class="smallText">Mbps</span>
                </div>
            </div>
            <div style="display:flex; flex-flow:row; justify-content: flex-end; align-items: flex-end; gap: 10px;">
                <span class="normalText">{$starlinkStatus?.uplink_throughput_bps ? ($starlinkStatus?.uplink_throughput_bps/ 1000000)?.toFixed(2) : '---'}</span>
                <div style="display:flex; flex-flow:column; justify-content: stretch;">
                    <span class="smallText">Up</span>
                    <span class="smallText">Mbps</span>
                </div>
            </div>
        </div>
        <div style="display:flex; flex-flow: column; flex: 2;" on:click={()=> $currentView = 'starlinkPingGraphs'}>
            <div style="display:flex; flex-flow:row; justify-content: flex-end; align-items: flex-end; gap: 10px;">
                <span class="normalText">{starlinkHistoryData?.maximum_ping_drop_rate ? (starlinkHistoryData?.maximum_ping_drop_rate * 100)?.toFixed(2) + '%' : '---'}</span>
                <div style="display:flex; flex-flow:column; justify-content: stretch;">
                    <span class="smallText">Max</span>
                    <span class="smallText">Drop</span>
                </div>
            </div>
            <div style="display:flex; flex-flow:row; justify-content: flex-end; align-items: flex-end; gap: 10px;">
                <span class="normalText">{starlinkHistoryData?.average_ping_drop_rate ? (starlinkHistoryData?.average_ping_drop_rate * 100)?.toFixed(2) + '%' : '---'}</span>
                <div style="display:flex; flex-flow:column; justify-content: stretch;">
                    <span class="smallText">Avg</span>
                    <span class="smallText">Drop</span>
                </div>
            </div>
        </div>
    </div>
</div>