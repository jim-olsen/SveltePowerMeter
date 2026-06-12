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

    /*
     * autoScale: Svelte action that watches an element's width with a
     * ResizeObserver and sets CSS custom properties --mv (metric-value
     * font-size, px) and --ml (metric-label font-size, px) on the element.
     *
     * Sizing strategy mirrors the previous container-query approach but
     * works without `container-type` / `cqi` units (which can be flaky in
     * some Svelte build pipelines / older browsers):
     *   value font-size  ~= width / 3.4  (fits "9999.9" with tabular-nums +
     *                                      font-stretch 90% glyphs ~0.50em)
     *   label font-size  ~= value * 12/42  (preserve original ratio)
     * Each is clamped to a sensible min/max.
     */
    function autoScale(node) {
        const apply = (w) => {
            if (!w) return;
            const value = Math.max(28, Math.min(64, w / 3.4));
            const label = Math.max(9, Math.min(18, value * 12 / 42));
            node.style.setProperty('--mv', value.toFixed(2) + 'px');
            node.style.setProperty('--ml', label.toFixed(2) + 'px');
        };
        apply(node.clientWidth);
        const ro = new ResizeObserver(entries => {
            for (const entry of entries) {
                apply(entry.contentRect.width);
            }
        });
        ro.observe(node);
        return {
            destroy() { ro.disconnect(); }
        };
    }

    $: batteryPct = $powerCurrentData?.battery_percent;
    $: batteryLevel = batteryPct != null ? Math.max(0, Math.min(100, batteryPct)) : 0;
    $: batteryMin = $powerStatsData?.battery_min_percent != null ? Math.max(0, Math.min(100, $powerStatsData.battery_min_percent)) : 0;
    $: batteryMax = $powerStatsData?.battery_max_percent != null ? Math.max(0, Math.min(100, $powerStatsData.battery_max_percent)) : 0;
    
    $: batteryRangeWidth = Math.max(0, batteryMax - batteryMin);
    $: batteryColor = batteryPct == null
        ? '#8892A6'
        : batteryPct >= 66 ? '#7CFF9A'
        : batteryPct >= 33 ? '#FFE45E'
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
        <div class="tile-top-extra"></div>
        <div class="metric-grid three">
            <div class="metric" use:autoScale on:click|stopPropagation={go('solarWattsGraph')}>
                <div class="metric-icon"><Fa icon={faSolarPanel}/></div>
                <div class="metric-value">{fmt($powerCurrentData?.solar_watts, 0)}</div>
                <div class="metric-label">Solar W</div>
            </div>
            <div class="metric" use:autoScale on:click|stopPropagation={go('loadGraph')}>
                <div class="metric-icon"><Fa icon={faPlug}/></div>
                <div class="metric-value">{fmt($powerCurrentData?.load_watts, 0)}</div>
                <div class="metric-label">Load W</div>
            </div>
            <div class="metric" use:autoScale>
                <div class="metric-icon"><Fa icon={faChartLine}/></div>
                <div class="metric-value">{fmt($powerCurrentData?.day_solar_wh, 0)}</div>
                <div class="metric-label">Solar Wh</div>
            </div>
        </div>
        <div class="tile-bottom-extra"></div>
    </div>

    <!-- BATTERY TILE -->
    <div class="tile tile-battery" on:click={go('battery_dashboard')}>
        <div class="tile-header">
            <div class="tile-icon" style="color: {batteryColor};">
                <Fa icon={faCarBattery}/>
            </div>
            <div class="tile-title">Battery</div>
            <div class="tile-badge" style="color: {batteryColor}; font-size: 16px;">
                {fmt($powerStatsData?.battery_min_percent, 1, '%')} / {fmt($powerStatsData?.battery_max_percent, 1, '%')}
            </div>
        </div>
        <div class="tile-top-extra">
            <div class="battery-bar" on:click|stopPropagation={go('voltageGraph')}>
                <div class="battery-min-dot" style="left: {batteryMin}%;"></div>
                <div class="battery-max-dot" style="left: {batteryMax}%;"></div>
                <div class="battery-fill" 
                     style="width: {batteryLevel}%; 
                            background: linear-gradient(90deg, #FF5C5C 0%, #FFE45E 33%, #7CFF9A 66%, #7CFF9A 100%); 
                            background-size: {(100 / (batteryLevel || 0.1)) * 100}% 100%;
                            box-shadow: 0 0 12px {batteryColor}55;">
                </div>
            </div>
        </div>
        <div class="metric-grid three">
            <div class="metric" use:autoScale on:click|stopPropagation={go('battery_dashboard')}>
                <div class="metric-icon" style="color: {batteryColor};"><Fa icon={faCarBattery}/></div>
                <div class="metric-value">{fmt(batteryPct, 1, '%')}</div>
                <div class="metric-label">Battery</div>
            </div>
            <div class="metric" use:autoScale on:click|stopPropagation={go('batteryWattsGraph')}>
                <div class="metric-icon"><Fa icon={faBolt}/></div>
                <div class="metric-value">{fmt($powerStatsData?.day_batt_wh, 0)}</div>
                <div class="metric-label">Batt Wh</div>
            </div>
            <div class="metric" use:autoScale>
                <div class="metric-icon"><Fa icon={faPlug}/></div>
                <div class="metric-value">{fmt($powerStatsData?.day_load_wh, 0)}</div>
                <div class="metric-label">Load Wh</div>
            </div>
        </div>
        <div class="tile-bottom-extra"></div>
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
        <div class="tile-top-extra"></div>
        <div class="metric-grid three">
            <div class="metric" use:autoScale on:click|stopPropagation={go('outTempGraph')}>
                <div class="metric-icon"><Fa icon={faTemperatureHigh}/></div>
                <div class="metric-value">{fmt($weatherData?.outTemp_F, 1)}<span class="unit">°F</span></div>
                <div class="metric-label">Out Temp</div>
            </div>
            <div class="metric" use:autoScale on:click|stopPropagation={go('inTempGraph')}>
                <div class="metric-icon"><Fa icon={faTemperatureLow}/></div>
                <div class="metric-value">{fmt($weatherData?.inTemp_F, 1)}<span class="unit">°F</span></div>
                <div class="metric-label">In Temp</div>
            </div>
            <div class="metric" use:autoScale on:click|stopPropagation={go('windGraph')}>
                <div class="metric-icon"><Fa icon={faWind}/></div>
                <div class="metric-value">{fmt($weatherData?.wind_average)}</div>
                <div class="metric-label">Wind Avg</div>
            </div>
        </div>
        <div class="tile-bottom-extra"></div>
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
        <div class="tile-top-extra"></div>
        <div class="metric-grid three">
            <div class="metric" use:autoScale on:click|stopPropagation={go('starlinkSpeedGraphs')}>
                <div class="metric-icon"><Fa icon={faArrowDown}/></div>
                <div class="metric-value">{$starlinkStatus?.downlink_throughput_bps ? ($starlinkStatus.downlink_throughput_bps / 1e6).toFixed(1) : '---'}</div>
                <div class="metric-label">Down Mbps</div>
            </div>
            <div class="metric" use:autoScale on:click|stopPropagation={go('starlinkSpeedGraphs')}>
                <div class="metric-icon"><Fa icon={faArrowUp}/></div>
                <div class="metric-value">{$starlinkStatus?.uplink_throughput_bps ? ($starlinkStatus.uplink_throughput_bps / 1e6).toFixed(1) : '---'}</div>
                <div class="metric-label">Up Mbps</div>
            </div>
            <div class="metric" use:autoScale on:click|stopPropagation={go('starlinkPingGraphs')}>
                <div class="metric-icon"><Fa icon={faSignal}/></div>
                <div class="metric-value">{starlinkHistoryData?.average_ping_drop_rate != null ? (starlinkHistoryData.average_ping_drop_rate * 100).toFixed(1) + '%' : '---'}</div>
                <div class="metric-label">Avg Drop</div>
            </div>
        </div>
        <div class="tile-bottom-extra">
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
        overflow: hidden;
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
        height: 70px;
        margin-bottom: 6px;
    }

    .tile-icon {
        display: flex;
        align-items: center;
        justify-content: center;
        width: 60px;
        height: 60px;
        border-radius: 14px;
        background: rgba(255, 255, 255, 0.05);
        font-size: 34px;
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
        font-size: 22px;
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

    .tile-top-extra {
        height: 42px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }

    .tile-bottom-extra {
        height: 48px;
        display: flex;
        flex-direction: column;
        justify-content: center;
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

    /*
     * Dynamic font scaling for metric values.
     *
     * Goal: scale the value font-size to be as large as possible while still
     * fitting up to 4 digits + 1 decimal point + 1 fractional digit (e.g.
     * "9999.9" -> 6 glyphs) inside the metric column at any viewport.
     *
     * With tabular-nums + font-stretch:90%, each glyph occupies roughly
     * ~0.50em of horizontal space, so 6 glyphs ~= 3.0em. Allowing a small
     * inner padding margin, picking font-size ~= containerWidth / 3.4
     * (i.e. ~29.4cqi) gives the largest size that still fits "9999.9".
     *
     * The clamp() bounds preserve the previous visual range (42px base,
     * 56px on large screens) as min/max so very narrow or very wide
     * containers still look sensible.
     */
    .metric-value {
        font-size: var(--mv, 42px);
        font-weight: 700;
        color: #fca503;
        line-height: 1;
        text-align: center;
        letter-spacing: 0.5px;
        text-shadow: 0 1px 2px rgba(0, 0, 0, 0.5);
        font-variant-numeric: tabular-nums;
        font-stretch: 90%;
        /* Height tracks font-size so the row keeps its proportions. */
        height: 1em;
        display: flex;
        align-items: center;
        justify-content: center;
        white-space: nowrap;
    }

    .metric-value .unit {
        /* Unit glyphs (e.g. "°F") scale with the value, matching the
           original 22/42 ~= 52% ratio. */
        font-size: 0.52em;
        font-weight: 500;
        color: #e6eaf2;
        margin-left: 2px;
    }

    .metric-label {
        /* Label scales proportionally to the value to keep the original
           label/value size ratio (12/42 ~= 28.6%). */
        font-size: var(--ml, 12px);
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.6px;
        color: #b0b9c8;
    }

    .battery-bar {
        position: relative;
        height: 26px;
        background: linear-gradient(90deg, 
            rgba(255, 92, 92, 0.15) 0%, 
            rgba(255, 228, 94, 0.15) 33%, 
            rgba(124, 255, 154, 0.15) 66%, 
            rgba(124, 255, 154, 0.15) 100%
        );
        border-radius: 13px;
        overflow: hidden;
        margin: 0;
        border: 1px solid rgba(255, 255, 255, 0.06);
    }

    .battery-bar::after {
        content: "";
        position: absolute;
        inset: 0;
        background-image: repeating-linear-gradient(
            90deg,
            transparent,
            transparent calc(10% - 4px),
            rgba(0, 0, 0, 0.3) calc(10% - 4px),
            rgba(0, 0, 0, 0.3) 10%
        );
        pointer-events: none;
        z-index: 2;
    }

    .battery-fill {
        position: absolute;
        left: 0;
        top: 0;
        bottom: 0;
        border-radius: 13px;
        transition: width 0.4s ease, background-size 0.4s ease;
        z-index: 1;
    }

    .battery-min-dot,
    .battery-max-dot {
        position: absolute;
        top: 50%;
        width: 12px;
        height: 12px;
        background: #000000;
        border: 2px solid rgba(255, 255, 255, 0.4);
        border-radius: 50%;
        z-index: 3;
        transform: translate(-50%, -50%);
        transition: left 0.4s ease;
        box-shadow: 0 0 4px rgba(0, 0, 0, 0.5);
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
        /* .metric-value / .metric-label sizes are driven by the autoScale
           action (CSS vars --mv / --ml); no fixed overrides here. */
        .metric-label { letter-spacing: 0.4px; }
        .tile-title { font-size: 20px; }
        .tile-badge { font-size: 20px; padding: 5px 12px; }
        .tile-icon { width: 50px; height: 50px; font-size: 28px; border-radius: 12px; }
        .tile-header { height: 60px; }
        .tile-top-extra { height: 38px; }
        .tile-bottom-extra { height: 42px; }
        .metric-icon { font-size: 30px; }
        .metric { min-height: 92px; padding: 6px 3px; }
        .tile { padding: 6px 8px; border-radius: 12px; }
        .tile-header { margin-bottom: 4px; gap: 6px; }
        .dash { gap: 5px; padding: 1px; }
        .sub-chip { font-size: 12px; padding: 3px 8px; }
        .battery-bar { height: 24px; margin: 0; }
    }

    /* Very short screens — shrink chrome but keep numbers large & readable */
    @media (max-height: 700px) {
        .metric { min-height: 78px; padding: 5px 3px; }
        .metric-icon { font-size: 26px; }
        .tile { padding: 5px 8px; }
        .tile-header { margin-bottom: 3px; height: 52px; }
        .tile-top-extra { height: 32px; }
        .tile-bottom-extra { height: 36px; }
        .tile-icon { width: 44px; height: 44px; font-size: 26px; }
        .tile-title { font-size: 18px; }
        .battery-bar { height: 22px; margin: 0; }
        .dash { gap: 4px; padding: 1px; }
    }

    /* Very small screens — keep numbers as big as possible */
    @media (max-width: 380px) {
        .metric-icon { font-size: 24px; }
        .metric { min-height: 78px; }
    }
</style>
