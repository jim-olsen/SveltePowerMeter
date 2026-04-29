<script>
    import {onDestroy} from 'svelte';
    import Fa from "svelte-fa";
    import {
        faCarBattery,
        faSnowflake,
        faSatelliteDish,
        faSun,
        faCloudMoon,
        faBolt,
        faPlug,
        faSolarPanel,
        faTemperatureHigh,
        faTemperatureLow,
        faWind,
        faArrowDown,
        faArrowUp,
        faSignal,
        faChartLine,
        faFire
    } from "@fortawesome/free-solid-svg-icons";

    import {
        powerCurrentData,
        powerStatsData,
        weatherData,
        starlinkStatus,
        starlinkHistory,
        currentView
    } from "../../stores";

    let starlinkHistoryData = {};

    const unsubscribeStarlinkHistory = starlinkHistory.subscribe(data => {
        starlinkHistoryData = data || {};
    });

    onDestroy(() => {
        unsubscribeStarlinkHistory();
    });

    function isCharging() {
        return $powerCurrentData?.charge_state === 'ABSORB' || $powerCurrentData?.charge_state === 'MPPT';
    }

    function isFloating() {
        return $powerCurrentData?.charge_state === 'FLOAT';
    }

    function chargeColor() {
        if (isFloating()) return '#7CFF9A';
        if ($powerCurrentData?.charge_state === 'ABSORB') return '#FFE45E';
        if (isCharging()) return '#FFB020';
        return '#8892A6';
    }

    function sunClass() {
        if (isFloating()) return 'icon-pulser';
        if (isCharging()) return 'icon-spinner';
        return '';
    }

    function fmt(v, digits = 1, suffix = '') {
        if (v === undefined || v === null || isNaN(Number(v))) return '---';
        return Number(v).toFixed(digits) + suffix;
    }

    function go(view) {
        return () => $currentView = view;
    }

    $: batteryPct = $powerCurrentData?.battery_percent;
    $: batteryLevel = batteryPct != null ? Math.max(0, Math.min(100, batteryPct)) : 0;
    $: batteryColor = batteryPct == null
        ? '#8892A6'
        : batteryPct > 70 ? '#7CFF9A'
        : batteryPct > 40 ? '#FFE45E'
        : batteryPct > 20 ? '#FFB020'
        : '#FF5C5C';

    $: starlinkConnected = $starlinkStatus?.state === 'CONNECTED';
</script>

<div class="dash">
    <!-- SOLAR / LOAD TILE -->
    <div class="tile tile-solar" on:click={go('statistics')}>
        <div class="tile-header">
            <div class="tile-icon" style="color: {chargeColor()};">
                {#if isCharging() || isFloating()}
                    <span class={sunClass()}><Fa icon={faSun}/></span>
                {:else}
                    <Fa icon={faCloudMoon}/>
                {/if}
            </div>
            <div class="tile-title">Solar</div>
            <div class="tile-badge" style="color: {chargeColor()};">
                {$powerCurrentData?.charge_state ?? '---'}
            </div>
        </div>
        <div class="metric-grid three">
            <div class="metric" on:click|stopPropagation={go('solarWattsGraph')}>
                <div class="metric-icon"><Fa icon={faSolarPanel}/></div>
                <div class="metric-value">{fmt($powerCurrentData?.solar_watts)}</div>
                <div class="metric-label">Solar W</div>
            </div>
            <div class="metric" on:click|stopPropagation={go('loadGraph')}>
                <div class="metric-icon"><Fa icon={faPlug}/></div>
                <div class="metric-value">{fmt($powerCurrentData?.load_watts)}</div>
                <div class="metric-label">Load W</div>
            </div>
            <div class="metric">
                <div class="metric-icon"><Fa icon={faChartLine}/></div>
                <div class="metric-value">{fmt($powerStatsData?.day_solar_wh)}</div>
                <div class="metric-label">Solar Wh</div>
            </div>
        </div>
    </div>

    <!-- BATTERY TILE -->
    <div class="tile tile-battery" on:click={go('battery_dashboard')}>
        <div class="tile-header">
            <div class="tile-icon" style="color: {batteryColor};">
                <Fa icon={faCarBattery}/>
            </div>
            <div class="tile-title">Battery</div>
            <div class="tile-badge" style="color: {batteryColor};">
                {batteryPct != null ? batteryPct.toFixed(1) + '%' : '---'}
            </div>
        </div>
        <div class="battery-bar" on:click|stopPropagation={go('voltageGraph')}>
            <div class="battery-fill" style="width: {batteryLevel}%; background: linear-gradient(90deg, {batteryColor}, {batteryColor}cc);"></div>
            <div class="battery-bar-labels">
                <span>Min {fmt($powerStatsData?.battery_min_percent, 2, '%')}</span>
                <span>Max {fmt($powerStatsData?.battery_max_percent, 2, '%')}</span>
            </div>
        </div>
        <div class="metric-grid two">
            <div class="metric" on:click|stopPropagation={go('batteryWattsGraph')}>
                <div class="metric-icon"><Fa icon={faBolt}/></div>
                <div class="metric-value">{fmt($powerStatsData?.day_batt_wh)}</div>
                <div class="metric-label">Batt Wh</div>
            </div>
            <div class="metric">
                <div class="metric-icon"><Fa icon={faPlug}/></div>
                <div class="metric-value">{fmt($powerStatsData?.day_load_wh)}</div>
                <div class="metric-label">Load Wh</div>
            </div>
        </div>
    </div>

    <!-- WEATHER TILE -->
    <div class="tile tile-weather" on:click={go('weather')}>
        <div class="tile-header">
            <div class="tile-icon weather-icon">
                <Fa icon={faSnowflake}/>
            </div>
            <div class="tile-title">Weather</div>
            <div class="tile-badge">
                {$weatherData?.outTemp_F ? Number($weatherData.outTemp_F).toFixed(0) + '°F' : '---'}
            </div>
        </div>
        <div class="metric-grid three">
            <div class="metric" on:click|stopPropagation={go('outTempGraph')}>
                <div class="metric-icon"><Fa icon={faTemperatureHigh}/></div>
                <div class="metric-value">{fmt($weatherData?.outTemp_F, 1)}<span class="unit">°F</span></div>
                <div class="metric-label">Out Temp</div>
            </div>
            <div class="metric" on:click|stopPropagation={go('inTempGraph')}>
                <div class="metric-icon"><Fa icon={faTemperatureLow}/></div>
                <div class="metric-value">{fmt($weatherData?.inTemp_F, 1)}<span class="unit">°F</span></div>
                <div class="metric-label">In Temp</div>
            </div>
            <div class="metric" on:click|stopPropagation={go('windGraph')}>
                <div class="metric-icon"><Fa icon={faWind}/></div>
                <div class="metric-value">{fmt($weatherData?.wind_average)}</div>
                <div class="metric-label">Wind Avg</div>
            </div>
        </div>
    </div>

    <!-- STARLINK TILE -->
    <div class="tile tile-starlink" on:click={go('starlinkStatus')}>
        <div class="tile-header">
            <div class="tile-icon starlink-icon">
                <Fa icon={faSatelliteDish}/>
            </div>
            <div class="tile-title">Starlink</div>
            <div class="tile-badge" class:connected={starlinkConnected} class:disconnected={!starlinkConnected}>
                <span class="status-dot" style="background: {starlinkConnected ? '#7CFF9A' : '#FF5C5C'};"></span>
                {$starlinkStatus?.state ?? 'UNKNOWN'}
            </div>
        </div>
        <div class="metric-grid three">
            <div class="metric" on:click|stopPropagation={go('starlinkSpeedGraphs')}>
                <div class="metric-icon"><Fa icon={faArrowDown}/></div>
                <div class="metric-value">{$starlinkStatus?.downlink_throughput_bps ? ($starlinkStatus.downlink_throughput_bps / 1e6).toFixed(1) : '---'}</div>
                <div class="metric-label">Down Mbps</div>
            </div>
            <div class="metric" on:click|stopPropagation={go('starlinkSpeedGraphs')}>
                <div class="metric-icon"><Fa icon={faArrowUp}/></div>
                <div class="metric-value">{$starlinkStatus?.uplink_throughput_bps ? ($starlinkStatus.uplink_throughput_bps / 1e6).toFixed(1) : '---'}</div>
                <div class="metric-label">Up Mbps</div>
            </div>
            <div class="metric" on:click|stopPropagation={go('starlinkPingGraphs')}>
                <div class="metric-icon"><Fa icon={faSignal}/></div>
                <div class="metric-value">{starlinkHistoryData?.average_ping_drop_rate != null ? (starlinkHistoryData.average_ping_drop_rate * 100).toFixed(1) + '%' : '---'}</div>
                <div class="metric-label">Avg Drop</div>
            </div>
        </div>
        <div class="sub-row" on:click|stopPropagation={go('starlinkPowerGraphs')}>
            <span class="sub-chip">
                <Fa icon={faFire} style="color: {$starlinkStatus?.alerts?.is_heating ? '#FF5C5C' : '#7CFF9A'};"/>
                Heater {$starlinkStatus?.alerts?.is_heating ? 'On' : 'Off'}
            </span>
            <span class="sub-chip">
                <Fa icon={faBolt}/>
                {fmt($starlinkStatus?.power_in, 1, ' W')}
            </span>
            <span class="sub-chip">
                Max Drop {starlinkHistoryData?.maximum_ping_drop_rate != null ? (starlinkHistoryData.maximum_ping_drop_rate * 100).toFixed(1) + '%' : '---'}
            </span>
        </div>
    </div>
</div>

<style>
    .dash {
        display: grid;
        grid-template-columns: 1fr;
        gap: 6px;
        width: 100%;
        height: 100%;
        box-sizing: border-box;
        padding: 2px;
        color: #e6eaf2;
        font-family: inherit;
        grid-auto-rows: 1fr;
    }

    @media (min-width: 720px) {
        .dash {
            grid-template-columns: 1fr 1fr;
        }
    }

    .tile {
        position: relative;
        border-radius: 14px;
        padding: 8px 10px 8px;
        background: linear-gradient(145deg, rgba(34, 40, 56, 0.85), rgba(20, 24, 36, 0.85));
        border: 1px solid rgba(255, 255, 255, 0.06);
        box-shadow: 0 6px 18px rgba(0, 0, 0, 0.45), inset 0 1px 0 rgba(255, 255, 255, 0.04);
        backdrop-filter: blur(6px);
        -webkit-backdrop-filter: blur(6px);
        transition: transform 0.15s ease, box-shadow 0.15s ease;
        overflow: hidden;
        display: flex;
        flex-direction: column;
        -webkit-tap-highlight-color: transparent;
        touch-action: manipulation;
    }

    .tile::before {
        content: "";
        position: absolute;
        inset: 0;
        border-radius: inherit;
        pointer-events: none;
        opacity: 0.18;
        background: radial-gradient(circle at top right, var(--accent, #fca503), transparent 60%);
    }

    .tile:active {
        transform: scale(0.985);
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.5);
    }

    .tile-solar    { --accent: #fca503; }
    .tile-battery  { --accent: #7CFF9A; }
    .tile-weather  { --accent: #5EC6FF; }
    .tile-starlink { --accent: #B78CFF; }

    .tile-header {
        display: flex;
        align-items: center;
        gap: 8px;
        margin-bottom: 6px;
    }

    .tile-icon {
        display: flex;
        align-items: center;
        justify-content: center;
        width: 68px;
        height: 68px;
        border-radius: 14px;
        background: rgba(255, 255, 255, 0.05);
        font-size: 40px;
        flex: 0 0 auto;
        color: var(--accent);
    }

    .weather-icon { color: #5EC6FF; }
    .starlink-icon { color: #B78CFF; }

    .tile-title {
        font-size: 26px;
        font-weight: 700;
        letter-spacing: 0.5px;
        color: #e6eaf2;
        flex: 1;
        text-transform: uppercase;
    }

    .tile-badge {
        font-size: 26px;
        font-weight: 700;
        padding: 6px 14px;
        border-radius: 999px;
        background: rgba(255, 255, 255, 0.06);
        color: #e6eaf2;
        display: inline-flex;
        align-items: center;
        gap: 6px;
        white-space: nowrap;
        font-variant-numeric: tabular-nums;
    }

    .status-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        display: inline-block;
        box-shadow: 0 0 8px currentColor;
    }

    .metric-grid {
        display: grid;
        gap: 6px;
        flex: 1 1 auto;
    }
    .metric-grid.two   { grid-template-columns: 1fr 1fr; }
    .metric-grid.three { grid-template-columns: 1fr 1fr 1fr; }

    .metric {
        background: rgba(255, 255, 255, 0.035);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 10px;
        padding: 10px 4px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        gap: 4px;
        min-height: 110px;
        cursor: pointer;
        transition: background 0.15s ease, transform 0.15s ease;
    }

    .metric:active {
        background: rgba(255, 255, 255, 0.08);
        transform: scale(0.97);
    }

    .metric-icon {
        font-size: 36px;
        color: var(--accent);
        opacity: 0.85;
        margin-bottom: 2px;
    }

    .metric-value {
        font-size: 64px;
        font-weight: 400;
        color: #fca503;
        line-height: 1;
        text-align: center;
        letter-spacing: 0.5px;
        text-shadow: 0 1px 2px rgba(0, 0, 0, 0.5);
        font-variant-numeric: tabular-nums;
        font-stretch: 90%;
    }

    .metric-value .unit {
        font-size: 34px;
        font-weight: 400;
        color: #e6eaf2;
        margin-left: 2px;
    }

    .metric-label {
        font-size: 14px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.6px;
        color: #b0b9c8;
    }

    .battery-bar {
        position: relative;
        height: 26px;
        background: rgba(255, 255, 255, 0.06);
        border-radius: 13px;
        overflow: hidden;
        margin: 2px 0 6px;
        border: 1px solid rgba(255, 255, 255, 0.06);
    }

    .battery-fill {
        position: absolute;
        left: 0;
        top: 0;
        bottom: 0;
        border-radius: 13px;
        transition: width 0.4s ease;
        box-shadow: 0 0 12px rgba(124, 255, 154, 0.35);
    }

    .battery-bar-labels {
        position: absolute;
        inset: 0;
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0 14px;
        font-size: 14px;
        color: #0b0f18;
        font-weight: 700;
        mix-blend-mode: screen;
        text-shadow: 0 0 2px rgba(0,0,0,0.4);
        font-variant-numeric: tabular-nums;
    }

    .sub-row {
        display: flex;
        flex-wrap: wrap;
        gap: 4px;
        margin-top: 6px;
    }

    .sub-chip {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        font-size: 16px;
        font-weight: 600;
        padding: 5px 12px;
        border-radius: 999px;
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.06);
        color: #cbd2df;
    }

    /* Phone-size tuning — keep numbers BIG for at-a-distance readability */
    @media (max-width: 500px) {
        .metric-value { font-size: 54px; }
        .metric-value .unit { font-size: 28px; }
        .metric-label { font-size: 12px; letter-spacing: 0.4px; }
        .tile-title { font-size: 20px; }
        .tile-badge { font-size: 22px; padding: 5px 12px; }
        .tile-icon { width: 56px; height: 56px; font-size: 32px; border-radius: 12px; }
        .metric-icon { font-size: 30px; }
        .metric { min-height: 92px; padding: 6px 3px; }
        .tile { padding: 6px 8px; border-radius: 12px; }
        .tile-header { margin-bottom: 4px; gap: 6px; }
        .dash { gap: 5px; padding: 1px; }
        .sub-chip { font-size: 12px; padding: 3px 8px; }
        .battery-bar { height: 24px; margin: 2px 0 5px; }
        .battery-bar-labels { font-size: 13px; padding: 0 10px; }
    }

    /* Very short screens — shrink chrome but keep numbers large & readable */
    @media (max-height: 700px) {
        .metric { min-height: 78px; padding: 5px 3px; }
        .metric-value { font-size: 48px; }
        .metric-value .unit { font-size: 26px; }
        .metric-label { font-size: 12px; }
        .metric-icon { font-size: 26px; }
        .tile { padding: 5px 8px; }
        .tile-header { margin-bottom: 3px; }
        .tile-icon { width: 52px; height: 52px; font-size: 30px; }
        .tile-title { font-size: 18px; }
        .battery-bar { height: 22px; margin: 1px 0 4px; }
        .dash { gap: 4px; padding: 1px; }
    }

    /* Very small screens — keep numbers as big as possible */
    @media (max-width: 380px) {
        .metric-value { font-size: 44px; }
        .metric-value .unit { font-size: 24px; }
        .metric-icon { font-size: 24px; }
        .metric { min-height: 78px; }
    }
</style>
