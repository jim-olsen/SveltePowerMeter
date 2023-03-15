<script xmlns="http://www.w3.org/1999/html">
    import {onDestroy} from 'svelte'
    import Fa from "svelte-fa";
    import {faCarBattery, faSnowflake, faSatelliteDish, faSun, faCloudMoon} from "@fortawesome/free-solid-svg-icons";

    import {powerCurrentData, powerStatsData, weatherData, starlinkStatus, starlinkHistory, currentView} from "../../stores";

    let currentData = {};
    let statsData = {};
    let wxData = {};
    let starlinkData = {};
    let starlinkHistoryData = {};

    const unsubscribeCurrent = powerCurrentData.subscribe(data => {
        currentData = data;
    });

    const unsubscribeStats = powerStatsData.subscribe(data => {
        statsData = data;
    });

    const unsubscribeWeather = weatherData.subscribe(data => {
        wxData = data;
    });

    const unsubscribeStarlinkStatus = starlinkStatus.subscribe(data => {
        starlinkData = data;
    });

    const unsubscribeStarlinkHistory = starlinkHistory.subscribe(data => {
        starlinkHistoryData = data;
        let batteryIcon = document.getElementById("carBatteryIcon");
        if (batteryIcon) {
            batteryIcon.style.color = getChargeStateColor();
        }
        let sunIcon = document.getElementById("sunChargingIcon");
        if (sunIcon) {
            setChargeStateClass(sunIcon);
        }
    });

    onDestroy(() => {
        unsubscribeCurrent();
        unsubscribeStats();
        unsubscribeWeather();
        unsubscribeStarlinkStatus();
        unsubscribeStarlinkHistory();
    });

    function getChargeStateColor() {
        if (isFloating()) {
            return 'lightgreen';
        } else if (currentData.charge_state === 'ABSORB') {
            return 'yellow';
        } else {
            return 'orangered';
        }
    }

    function isCharging() {
        return currentData.charge_state === 'ABSORB' || currentData.charge_state === 'MPPT';
    }

    function isFloating() {
        return currentData.charge_state === 'FLOAT';
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
        {#if currentData && (isCharging() || isFloating())}
            <div style="display:flex; flex-flow: row; justify-content: center; align-items: center; flex: 1; color: yellow; font-size: 6vh;"
                     on:click={()=>currentView.set('statistics')}>
                <Fa id="sunChargingIcon" icon="{faSun}" style="font-size: 6vw;"/>
            </div>
        {:else}
            <div style="display:flex; flex-flow: row; justify-content: center; align-items: center; flex: 1; color: grey; font-size: 6vh;"
                 on:click={()=>currentView.set('statistics')}>
                <Fa id="moonNightIcon" icon="{faCloudMoon}"  style="font-size: 6vw;"/>
            </div>
        {/if}
        <div style="display:flex; flex-flow:row; justify-content: flex-end; align-items: flex-end; flex: 2; gap: 10px;"
                on:click={() => currentView.set('loadGraph')}>
            <span class="largeText">{currentData?.load_amps ? (currentData?.load_amps * currentData?.battery_voltage)?.toFixed(1) : '---'}</span>
            <div style="display:flex; flex-flow:column; justify-content: stretch;">
                <span class="smallText">Load</span>
                <span class="smallText">Watts</span>
            </div>
        </div>
        <div style="display:flex; flex-flow:row; justify-content: flex-end; align-items: flex-end; flex: 2; gap: 10px;"
                on:click={()=> {currentView.set('solarWattsGraph')}}>
            <span class="largeText">{currentData?.solar_watts ? currentData?.solar_watts.toFixed(1) : '---'}</span>
            <div style="display:flex; flex-flow:column; justify-content: stretch;">
                <span class="smallText">Solar</span>
                <span class="smallText">Watts</span>
            </div>
        </div>
        <div style="display:flex; flex-flow:row; justify-content: flex-end; align-items: flex-end; flex: 2; gap: 10px;">
            <span class="largeText">{statsData?.day_solar_wh ? statsData?.day_solar_wh.toFixed(1) : '---'}</span>
            <div style="display:flex; flex-flow:column; justify-content: stretch;">
                <span class="smallText">Solar</span>
                <span class="smallText">WH</span>
            </div>
        </div>
    </div>
    <div style="display:flex; flex-flow:row; justify-content: space-between; width: 100%;" class="card">
        <div style="display:flex; flex-flow: row; justify-content: center; align-items: center; flex: 1; font-size: 6vh;"
                on:click={()=> currentView.set('statistics')}>
            <Fa icon="{faCarBattery}" id="carBatteryIcon" style="font-size: 6vw; color: orangered;" />
        </div>
        <div style="display:flex; flex-flow:row; justify-content: flex-end; align-items: flex-end; flex: 2; gap: 10px;"
                on:click={()=>currentView.set('voltageGraph')}>
            <span class="largeText">{currentData?.battery_voltage ? (currentData?.battery_voltage)?.toFixed(2) : '---'}</span>
            <div style="display:flex; flex-flow:column; justify-content: stretch;">
                <span class="smallText">Batt</span>
                <span class="smallText">Volts</span>
            </div>
        </div>
        <div style="display:flex; flex-flow:row; justify-content: flex-end; align-items: flex-end; flex: 2; gap: 10px;"
                on:click={() => currentView.set('batteryWattsGraph')}>
            <span class="largeText">{statsData?.day_batt_wh ? statsData?.day_batt_wh?.toFixed(1) : '---'}</span>
            <div style="display:flex; flex-flow:column; justify-content: stretch;">
                <span class="smallText">Batt</span>
                <span class="smallText">WH</span>
            </div>
        </div>
        <div style="display:flex; flex-flow:row; justify-content: flex-end; align-items: flex-end; flex: 2; gap: 10px;">
            <span class="largeText">{statsData?.day_load_wh ? statsData?.day_load_wh?.toFixed(1) : '---'}</span>
            <div style="display:flex; flex-flow:column; justify-content: stretch;">
                <span class="smallText">Load</span>
                <span class="smallText">WH</span>
            </div>
        </div>
    </div>
    <div style="display:flex; flex-flow:row; justify-content: space-between; width: 100%;" class="card">
        <div style="display:flex; flex-flow: row; justify-content: center; align-items: center; flex: 1; color: slateblue; font-size: 6vh;"
             on:click={()=> currentView.set('weather')}>
            <Fa icon="{faSnowflake}" style="font-size: 6vw;"/>
        </div>
        <div style="display:flex; flex-flow:row; justify-content: flex-end; align-items: flex-end; flex: 2; gap: 10px;">
            <span class="largeText">{wxData?.outTemp_F ? Number(wxData?.outTemp_F)?.toFixed(1) + ' F' : '---'}</span>
            <div style="display:flex; flex-flow:column; justify-content: stretch;">
                <span class="smallText">Out</span>
                <span class="smallText">Temp</span>
            </div>
        </div>
        <div style="display:flex; flex-flow:row; justify-content: flex-end; align-items: flex-end; flex: 2; gap: 10px;">
            <span class="largeText">{wxData?.inTemp_F ? Number(wxData?.inTemp_F)?.toFixed(1) + ' F' : '---'}</span>
            <div style="display:flex; flex-flow:column; justify-content: stretch;">
                <span class="smallText">In</span>
                <span class="smallText">Temp</span>
            </div>
        </div>
        <div style="display:flex; flex-flow:row; justify-content: flex-end; align-items: flex-end; flex: 2; gap: 10px;">
            <span class="largeText">{wxData?.wind_average ? Number(wxData?.wind_average)?.toFixed(1) : '---'}</span>
            <div style="display:flex; flex-flow:column; justify-content: stretch;">
                <span class="smallText">Wind</span>
                <span class="smallText">Avg</span>
            </div>
        </div>
    </div>
    <div style="display:flex; flex-flow:row; justify-content: space-between; width: 100%;" class="card">
        <div style="display:flex; flex-flow: row; justify-content: center; align-items: center; flex: 1; color: slategray; font-size: 6vh;">
            <Fa icon="{faSatelliteDish}" style="font-size: 6vw;"/>
        </div>
        <div style="display:flex; flex-flow: column; flex: 2;">
            <div style="display:flex; flex-flow:row; justify-content: flex-end; align-items: flex-end;" on:click={()=>currentView.set('starlinkStatus')}>
                <span class="normalText" style="color: {starlinkData.state === 'CONNECTED' ? 'greenyellow' : 'orangered'};">{starlinkData.state ? starlinkData.state : 'UNKNOWN'}</span>
            </div>
            <div style="display:flex; flex-flow:row; justify-content: flex-end; align-items: flex-end;">
                <span class="normalText">Heater <span style="color: {starlinkData?.alerts?.is_heating ? 'red' : 'greenyellow'};">{starlinkData?.alerts?.is_heating ? 'On' : 'Off'}</span></span>
            </div>
        </div>
        <div style="display:flex; flex-flow: column; flex: 2;" on:click={()=>currentView.set('starlinkSpeedGraphs')}>
            <div style="display:flex; flex-flow:row; justify-content: flex-end; align-items: flex-end; gap: 10px;">
                <span class="normalText" >{starlinkData?.downlink_throughput_bps ? (starlinkData?.downlink_throughput_bps / 1000000)?.toFixed(2) : '---'}</span>
                <div style="display:flex; flex-flow:column; justify-content: stretch;">
                    <span class="smallText">Down</span>
                    <span class="smallText">Mbps</span>
                </div>
            </div>
            <div style="display:flex; flex-flow:row; justify-content: flex-end; align-items: flex-end; gap: 10px;">
                <span class="normalText">{starlinkData?.uplink_throughput_bps ? (starlinkData?.uplink_throughput_bps/ 1000000)?.toFixed(2) : '---'}</span>
                <div style="display:flex; flex-flow:column; justify-content: stretch;">
                    <span class="smallText">Up</span>
                    <span class="smallText">Mbps</span>
                </div>
            </div>
        </div>
        <div style="display:flex; flex-flow: column; flex: 2;" on:click={()=>currentView.set('starlinkPingGraphs')}>
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