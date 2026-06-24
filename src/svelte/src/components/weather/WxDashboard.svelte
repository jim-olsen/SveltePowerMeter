<script>
    import {weatherData} from "../../stores.svelte.js";
    import {currentView} from "../../states.svelte.js";
    import Fa from "svelte-fa";
    import {faArrowLeftLong, faWind, faTemperatureHigh, faTemperatureLow, faDroplet, faCloudRain, faGauge} from "@fortawesome/free-solid-svg-icons";
    import WindDisplay from "./WindDisplay.svelte";
    import Thermometer from "./Thermometer.svelte";
    import OutdoorTemperatureGraph from "./OutdoorTemperatureGraph.svelte";
    import IndoorTemperatureGraph from "./IndoorTemperatureGraph.svelte";
    import PressureGraph from "./PressureGraph.svelte";
    import HumidityGraph from "./HumidityGraph.svelte";

    let wxHeight = 0, wxWidth = 0, headerHeight = 0;
    let display = 'dashboard';

    function fmt(v, digits = 1, suffix = '') {
        if (v === undefined || v === null || isNaN(Number(v))) return '---';
        return Number(v).toFixed(digits) + suffix;
    }
</script>

<div class="wx-root" bind:clientHeight={wxHeight} bind:clientWidth={wxWidth}>
{#if display === 'dashboard'}
    <div class="wx-dash">
        <!-- WIND TILE -->
        <div class="tile tile-wind" role="button" tabindex="0" on:click={() => currentView.value = 'dashboard'} on:keydown={(event) => (event.key === 'Enter' || event.key === ' ') && (currentView.value = 'dashboard')}>
            <div class="tile-header">
                <div class="tile-icon"><Fa icon={faWind}/></div>
                <div class="tile-title">Wind</div>
                <div class="tile-badge">
                    {$weatherData?.wind_average ? Number($weatherData.wind_average).toFixed(1) + ' MPH' : '---'}
                </div>
            </div>
            <div class="wind-rose-container">
                <WindDisplay size={Math.min(wxWidth * 0.42, wxHeight * 0.38, 260)}/>
            </div>
            <div class="wind-extras">
                <span class="sub-chip">Gust {fmt($weatherData?.windGust, 1, ' MPH')}</span>
                <span class="sub-chip">Max {fmt($weatherData?.windGust_max, 1, ' MPH')}</span>
            </div>
        </div>

        <!-- TEMPERATURE TILE -->
        <div class="tile tile-temp" on:click={() => display = 'outtemp'}>
            <div class="tile-header">
                <div class="tile-icon"><Fa icon={faTemperatureHigh}/></div>
                <div class="tile-title">Temperature</div>
                <div class="tile-badge">
                    {$weatherData?.outTemp_F ? Number($weatherData.outTemp_F).toFixed(0) + '°F' : '---'}
                </div>
            </div>
            <div class="thermo-row">
                <div on:click|stopPropagation={() => display = 'outtemp'}>
                    <Thermometer temperatureField="outTemp_F" temperatureMaxField="outTemp_F_max" temperatureMinField="outTemp_F_min" title="Outside" height="120"/>
                </div>
                <div on:click|stopPropagation={() => display = 'outtemp'}>
                    <Thermometer temperatureField="windchill_F" temperatureMinField="windchill_F_min" temperatureMaxField="windchill_F_max" title="Windchill" height="120"/>
                </div>
                <div on:click|stopPropagation={() => display = 'intemp'}>
                    <Thermometer temperatureField="inTemp_F" temperatureMinField="inTemp_F_min" temperatureMaxField="inTemp_F_max" title="Inside" height="120"/>
                </div>
            </div>
        </div>

        <!-- CONDITIONS TILE -->
        <div class="tile tile-conditions">
            <div class="tile-header">
                <div class="tile-icon"><Fa icon={faGauge}/></div>
                <div class="tile-title">Conditions</div>
            </div>
            <div class="metric-grid">
                <div class="metric" on:click={() => display = 'pressure'}>
                    <div class="metric-icon"><Fa icon={faGauge}/></div>
                    <div class="metric-value">{fmt($weatherData?.barometer_inHg, 2)}<span class="unit">inHg</span></div>
                    <div class="metric-label">Pressure</div>
                </div>
                <div class="metric" on:click={() => display = 'humidity'}>
                    <div class="metric-icon"><Fa icon={faDroplet}/></div>
                    <div class="metric-value">{fmt($weatherData?.outHumidity, 1)}<span class="unit">%</span></div>
                    <div class="metric-label">Humidity</div>
                </div>
            </div>
        </div>

        <!-- RAIN TILE -->
        <div class="tile tile-rain">
            <div class="tile-header">
                <div class="tile-icon"><Fa icon={faCloudRain}/></div>
                <div class="tile-title">Rain</div>
            </div>
            <div class="metric-grid three">
                <div class="metric">
                    <div class="metric-value">{fmt($weatherData?.dayRain_in, 2)}<span class="unit">in</span></div>
                    <div class="metric-label">Today</div>
                </div>
                <div class="metric">
                    <div class="metric-value">{fmt($weatherData?.rainRate_inch_per_hour, 1)}<span class="unit">in/hr</span></div>
                    <div class="metric-label">Rate</div>
                </div>
                <div class="metric">
                    <div class="metric-value">{fmt($weatherData?.rain24_in, 2)}<span class="unit">in</span></div>
                    <div class="metric-label">24 Hr</div>
                </div>
            </div>
        </div>
    </div>
{/if}
{#if display === 'outtemp'}
    <div class="detail-view">
        <div on:click={() => display='dashboard'} bind:clientHeight={headerHeight} class="detail-header">
            <div class="back-btn"><Fa icon={faArrowLeftLong}/></div>
            <span class="detail-title">Outdoor Temperature</span>
        </div>
        <OutdoorTemperatureGraph chartWidth={wxWidth} chartHeight={wxHeight - headerHeight} />
    </div>
{/if}
{#if display === 'intemp'}
    <div class="detail-view">
        <div on:click={() => display='dashboard'} bind:clientHeight={headerHeight} class="detail-header">
            <div class="back-btn"><Fa icon={faArrowLeftLong}/></div>
            <span class="detail-title">Indoor Temperature</span>
        </div>
        <IndoorTemperatureGraph chartWidth={wxWidth} chartHeight={wxHeight - headerHeight} />
    </div>
{/if}
{#if display === 'pressure'}
    <div class="detail-view">
        <div on:click={() => display='dashboard'} bind:clientHeight={headerHeight} class="detail-header">
            <div class="back-btn"><Fa icon={faArrowLeftLong}/></div>
            <span class="detail-title">Barometric Pressure</span>
        </div>
        <PressureGraph chartWidth={wxWidth} chartHeight={wxHeight - headerHeight} />
    </div>
{/if}
{#if display === 'humidity'}
    <div class="detail-view">
        <div on:click={() => display='dashboard'} bind:clientHeight={headerHeight} class="detail-header">
            <div class="back-btn"><Fa icon={faArrowLeftLong}/></div>
            <span class="detail-title">Outdoor Humidity</span>
        </div>
        <HumidityGraph chartWidth={wxWidth} chartHeight={wxHeight - headerHeight} />
    </div>
{/if}
</div>

<style>
    .wx-root {
        display: flex;
        flex-direction: column;
        width: 100%;
        height: 100%;
        color: #e6eaf2;
        font-family: inherit;
        overflow: hidden;
    }

    .wx-dash {
        display: grid;
        grid-template-columns: 1fr;
        gap: 6px;
        width: 100%;
        height: 100%;
        box-sizing: border-box;
        padding: 2px;
        grid-auto-rows: 1fr;
        overflow: hidden;
    }

    @media (min-width: 600px) {
        .wx-dash {
            grid-template-columns: 1fr 1fr;
        }
    }

    /* Tile base — matches MainDashboard */
    .tile {
        position: relative;
        border-radius: 14px;
        padding: 8px 10px;
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
        background: radial-gradient(circle at top right, var(--accent, #5EC6FF), transparent 60%);
    }

    .tile:active {
        transform: scale(0.985);
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.5);
    }

    .tile-wind       { --accent: #5EC6FF; }
    .tile-temp       { --accent: #FF8C5C; }
    .tile-conditions { --accent: #B78CFF; }
    .tile-rain       { --accent: #5EC6FF; }

    .tile-header {
        display: flex;
        align-items: center;
        gap: 8px;
        min-height: 44px;
        margin-bottom: 4px;
    }

    .tile-icon {
        display: flex;
        align-items: center;
        justify-content: center;
        width: 40px;
        height: 40px;
        border-radius: 10px;
        background: rgba(255, 255, 255, 0.05);
        font-size: 22px;
        flex: 0 0 auto;
        color: var(--accent);
    }

    .tile-title {
        font-size: 20px;
        font-weight: 700;
        letter-spacing: 0.5px;
        color: #e6eaf2;
        flex: 1;
        text-transform: uppercase;
    }

    .tile-badge {
        font-size: 18px;
        font-weight: 700;
        padding: 4px 10px;
        border-radius: 999px;
        background: rgba(255, 255, 255, 0.06);
        color: #e6eaf2;
        display: inline-flex;
        align-items: center;
        gap: 6px;
        white-space: nowrap;
        font-variant-numeric: tabular-nums;
    }

    /* Wind rose area */
    .wind-rose-container {
        flex: 1 1 auto;
        display: flex;
        align-items: center;
        justify-content: center;
        min-height: 0;
    }

    .wind-extras {
        display: flex;
        flex-wrap: wrap;
        gap: 4px;
        justify-content: center;
        padding-top: 4px;
    }

    .sub-chip {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        font-size: 13px;
        font-weight: 600;
        padding: 4px 10px;
        border-radius: 999px;
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.06);
        color: #cbd2df;
    }

    /* Thermometer row */
    .thermo-row {
        flex: 1 1 auto;
        display: flex;
        justify-content: space-evenly;
        align-items: center;
        min-height: 0;
        gap: 4px;
    }

    /* Metric grid — matches MainDashboard */
    .metric-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 6px;
        flex: 1 1 auto;
    }

    .metric-grid.three {
        grid-template-columns: 1fr 1fr 1fr;
    }

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
        min-height: 80px;
        cursor: pointer;
        transition: background 0.15s ease, transform 0.15s ease;
    }

    .metric:active {
        background: rgba(255, 255, 255, 0.08);
        transform: scale(0.97);
    }

    .metric-icon {
        font-size: 24px;
        color: var(--accent);
        opacity: 0.85;
        margin-bottom: 2px;
    }

    .metric-value {
        font-size: 42px;
        font-weight: 700;
        color: #fca503;
        line-height: 1;
        text-align: center;
        letter-spacing: 0.5px;
        text-shadow: 0 1px 2px rgba(0, 0, 0, 0.5);
        font-variant-numeric: tabular-nums;
        font-stretch: 90%;
        height: 42px;
        display: flex;
        align-items: center;
        justify-content: center;
    }

    .metric-value .unit {
        font-size: 22px;
        font-weight: 500;
        color: #e6eaf2;
        margin-left: 2px;
    }

    .metric-label {
        font-size: 12px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.6px;
        color: #b0b9c8;
    }

    @media (min-width: 1280px) and (min-height: 720px) {
        .metric-value { font-size: 56px; height: 56px; }
        .metric-value .unit { font-size: 30px; }
        .metric-label { font-size: 14px; }
    }

    /* Detail / graph views */
    .detail-view {
        display: flex;
        flex-direction: column;
        align-items: stretch;
        width: 100%;
        height: 100%;
    }

    .detail-header {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 10px 12px;
        cursor: pointer;
        -webkit-tap-highlight-color: transparent;
        touch-action: manipulation;
    }

    .back-btn {
        display: flex;
        align-items: center;
        justify-content: center;
        width: 44px;
        height: 44px;
        border-radius: 12px;
        background: rgba(255, 255, 255, 0.05);
        font-size: 22px;
        color: #e6eaf2;
    }

    .back-btn:active {
        background: rgba(255, 255, 255, 0.12);
    }

    .detail-title {
        font-size: 20px;
        font-weight: 700;
        color: #e6eaf2;
        letter-spacing: 0.5px;
    }

    /* Responsive adjustments */
    @media (max-width: 500px) {
        .tile { padding: 6px 8px; border-radius: 12px; }
        .tile-header { min-height: 38px; gap: 6px; }
        .tile-icon { width: 34px; height: 34px; font-size: 18px; border-radius: 8px; }
        .tile-title { font-size: 16px; }
        .tile-badge { font-size: 15px; padding: 3px 8px; }
        .metric-value { font-size: 48px; height: 48px; }
        .metric-value .unit { font-size: 24px; }
        .metric-label { font-size: 12px; letter-spacing: 0.4px; }
        .metric { min-height: 92px; padding: 6px 3px; }
        .metric-icon { font-size: 30px; }
        .wx-dash { gap: 4px; padding: 1px; }
        .sub-chip { font-size: 11px; padding: 3px 7px; }
    }

    @media (max-height: 700px) {
        .metric { min-height: 78px; padding: 5px 3px; }
        .metric-value { font-size: 42px; height: 42px; }
        .metric-value .unit { font-size: 22px; }
        .metric-label { font-size: 12px; }
        .metric-icon { font-size: 26px; }
        .tile { padding: 5px 8px; }
        .tile-header { min-height: 34px; margin-bottom: 2px; }
        .tile-icon { width: 30px; height: 30px; font-size: 16px; }
        .tile-title { font-size: 15px; }
        .wx-dash { gap: 4px; padding: 1px; }
    }
</style>



