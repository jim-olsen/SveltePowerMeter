<script>
    import {batteryCurrentData} from "../../stores.svelte.js";
    import {currentView} from "../../states.svelte.js";
    import Fa from "svelte-fa";
    import {
        faCarBattery,
        faBolt,
        faThermometerHalf,
        faChartBar,
        faArrowLeft,
        faSync
    } from "@fortawesome/free-solid-svg-icons";

    let battery_overall_percent = 0;

    function getOverallAveragePercent() {
        let percentTotal = 0;
        $batteryCurrentData.forEach(battery => percentTotal += battery.capacity_percent);
        battery_overall_percent = $batteryCurrentData.length > 0
            ? percentTotal / $batteryCurrentData.length
            : 0;
    }

    $: $batteryCurrentData, getOverallAveragePercent();

    function batteryColor(pct) {
        if (pct >= 66) return '#7CFF9A';
        if (pct >= 33) return '#FFE45E';
        return '#FF5C5C';
    }

    function statusColor(battery) {
        if (battery.protection_status && battery.protection_status.indexOf('Cell Block Over-Vol') > -1) return '#FF5C5C';
        if (battery.control_status === 'Charging') return '#FFE45E';
        if (battery.control_status === 'Discharging') return '#5EC6FF';
        return '#7CFF9A';
    }

    function statusLabel(battery) {
        if (battery.protection_status && battery.protection_status.indexOf('Cell Block Over-Vol') > -1) return 'PRO';
        if (battery.control_status === 'Charging') return 'CHG';
        if (battery.control_status === 'Discharging') return 'DIS';
        return 'IDL';
    }

    function fmt(v, digits = 2, suffix = '') {
        if (v === undefined || v === null || isNaN(Number(v))) return '---';
        return Number(v).toFixed(digits) + suffix;
    }

    function go(view) {
        return () => currentView.value = view;
    }
</script>

<div class="battery-dash">
    <!-- Header -->
    <div class="dash-header" role="button" tabindex="0" on:click={go('dashboard')} on:keydown={(event) => (event.key === 'Enter' || event.key === ' ') && go('dashboard')()}>
        <div class="back-btn"><Fa icon={faArrowLeft}/></div>
        <div class="header-icon" style="color: {batteryColor(battery_overall_percent)};">
            <Fa icon={faCarBattery}/>
        </div>
        <div class="header-title">Battery Bank</div>
        <div class="header-pct" style="color: {batteryColor(battery_overall_percent)};">
            {fmt(battery_overall_percent, 1)}%
        </div>
    </div>

    <!-- Battery Grid -->
    <div class="card-grid">
        {#each $batteryCurrentData as battery}
            <div class="card" role="button" tabindex="0" on:click={go('battery_details_' + battery.name)} on:keydown={(event) => (event.key === 'Enter' || event.key === ' ') && go('battery_details_' + battery.name)()}>
                <div class="card-body">
                    <!-- Row 1: Name + Status -->
                    <div class="card-row-top">
                        <span class="card-name">{battery.name}</span>
                        <span class="card-status" style="color: {statusColor(battery)};">{statusLabel(battery)}</span>
                    </div>

                    <!-- Row 2: Big percentage + capacity bar -->
                    <div class="card-row-main" role="button" tabindex="0" on:click|stopPropagation={go('batteryBankVoltageGraph')} on:keydown|stopPropagation={(event) => (event.key === 'Enter' || event.key === ' ') && go('batteryBankVoltageGraph')()}>
                        <span class="big-pct" style="color: {batteryColor(battery.capacity_percent)};">{battery.capacity_percent}<small>%</small></span>
                        <div class="cap-bar-wrap">
                            <div class="cap-bar">
                                <div class="cap-fill"
                                     style="width: {Math.max(0, Math.min(100, battery.capacity_percent))}%;
                                            background: linear-gradient(90deg, #FF5C5C 0%, #FFE45E 33%, #7CFF9A 66%, #7CFF9A 100%);
                                            background-size: {(100 / (Math.max(1, battery.capacity_percent) / 100)) }% 100%;
                                            box-shadow: 0 0 6px {batteryColor(battery.capacity_percent)}55;">
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Row 3: Key metrics -->
                    <div class="card-row-metrics">
                        <span class="metric" role="button" tabindex="0" on:click|stopPropagation={go('batteryBankVoltageGraph')} on:keydown|stopPropagation={(event) => (event.key === 'Enter' || event.key === ' ') && go('batteryBankVoltageGraph')()}>
                            <Fa icon={faBolt} style="color:#FFE45E;font-size:10px;"/>
                            <b>{fmt(battery.voltage, 1)}</b><small>V</small>
                        </span>
                        <span class="metric" role="button" tabindex="0" on:click|stopPropagation={go('batteryCellPressureGraph')} on:keydown|stopPropagation={(event) => (event.key === 'Enter' || event.key === ' ') && go('batteryCellPressureGraph')()}>
                            <Fa icon={faChartBar} style="color:#5EC6FF;font-size:10px;"/>
                            <b>{fmt(battery.current, 1)}</b><small>A</small>
                        </span>
                        <span class="metric" role="button" tabindex="0" on:click|stopPropagation={go('batteryBankTemperatureGraph')} on:keydown|stopPropagation={(event) => (event.key === 'Enter' || event.key === ' ') && go('batteryBankTemperatureGraph')()}>
                            <Fa icon={faThermometerHalf} style="color:#FF5C5C;font-size:10px;"/>
                            <b>{#if battery.battery_temps_f && battery.battery_temps_f.length > 0}{fmt(battery.battery_temps_f[0], 0)}{:else}---{/if}</b><small>°F</small>
                        </span>
                        <span class="metric">
                            <Fa icon={faSync} style="color:#7CFF9A;font-size:10px;"/>
                            <b>{fmt(battery.cycles, 0)}</b>
                        </span>
                    </div>
                </div>
            </div>
        {/each}
    </div>
</div>

<style>
    .battery-dash {
        display: flex;
        flex-direction: column;
        width: 100%;
        height: 100%;
        box-sizing: border-box;
        padding: 3px;
        gap: 3px;
        color: #e6eaf2;
        font-family: inherit;
        overflow: hidden;
    }

    /* ── Header ── */
    .dash-header {
        display: flex;
        align-items: center;
        gap: 14px;
        padding: 10px 16px;
        border-radius: 10px;
        background: linear-gradient(145deg, rgba(34, 40, 56, 0.85), rgba(20, 24, 36, 0.85));
        border: 1px solid rgba(255, 255, 255, 0.06);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.4), inset 0 1px 0 rgba(255, 255, 255, 0.04);
        cursor: pointer;
        -webkit-tap-highlight-color: transparent;
        touch-action: manipulation;
        transition: transform 0.15s ease;
        flex-shrink: 0;
    }
    .dash-header:active { transform: scale(0.985); }

    .back-btn { font-size: 26px; color: #8892A6; }
    .header-icon { font-size: 34px; display: flex; align-items: center; }
    .header-title { font-size: 26px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px; flex: 1; }
    .header-pct { font-size: 36px; font-weight: 700; font-variant-numeric: tabular-nums; white-space: nowrap; }

    /* ── Card grid — 2 cols ── */
    .card-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 3px;
        flex: 1;
        min-height: 0;
    }

    .card {
        border-radius: 10px;
        background: linear-gradient(145deg, rgba(34, 40, 56, 0.85), rgba(20, 24, 36, 0.85));
        border: 1px solid rgba(255, 255, 255, 0.06);
        box-shadow: 0 3px 10px rgba(0, 0, 0, 0.35), inset 0 1px 0 rgba(255, 255, 255, 0.04);
        cursor: pointer;
        -webkit-tap-highlight-color: transparent;
        touch-action: manipulation;
        transition: transform 0.15s ease;
        display: flex;
        flex-direction: row;
        overflow: hidden;
    }
    .card:active { transform: scale(0.985); }

    .card-body {
        flex: 1;
        display: flex;
        flex-direction: column;
        justify-content: center;
        padding: 5px 8px;
        gap: 2px;
        min-width: 0;
    }

    /* ── Row: Name + Status ── */
    .card-row-top {
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    .card-name {
        font-size: 28px;
        font-weight: 700;
        letter-spacing: 0.3px;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    .card-status {
        font-size: 22px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.3px;
    }

    /* ── Row: Big percent + bar ── */
    .card-row-main {
        display: flex;
        align-items: center;
        gap: 6px;
        cursor: pointer;
    }
    .big-pct {
        font-size: 28px;
        font-weight: 800;
        font-variant-numeric: tabular-nums;
        line-height: 1;
        white-space: nowrap;
        text-shadow: 0 1px 3px rgba(0, 0, 0, 0.5);
    }
    .big-pct small {
        font-size: 16px;
        font-weight: 600;
        opacity: 0.7;
    }
    .cap-bar-wrap {
        flex: 1;
        min-width: 0;
        display: flex;
        align-items: center;
    }
    .cap-bar {
        position: relative;
        width: 100%;
        height: 10px;
        background: linear-gradient(90deg,
            rgba(255, 92, 92, 0.15) 0%,
            rgba(255, 228, 94, 0.15) 33%,
            rgba(124, 255, 154, 0.15) 66%,
            rgba(124, 255, 154, 0.15) 100%
        );
        border-radius: 5px;
        overflow: hidden;
        border: 1px solid rgba(255, 255, 255, 0.06);
    }
    .cap-fill {
        position: absolute;
        left: 0; top: 0; bottom: 0;
        border-radius: 5px;
        transition: width 0.4s ease;
    }

    /* ── Row: Metrics ── */
    .card-row-metrics {
        display: flex;
        gap: 3px;
        justify-content: space-between;
    }
    .metric {
        display: inline-flex;
        align-items: center;
        gap: 1px;
        font-size: 10px;
        cursor: pointer;
        padding: 1px 2px;
        border-radius: 3px;
        transition: background 0.15s ease;
    }
    .metric:active { background: rgba(255, 255, 255, 0.08); }
    .metric b {
        color: #fca503;
        font-variant-numeric: tabular-nums;
        font-size: 16px;
    }
    .metric small {
        color: #8892A6;
        font-size: 10px;
        margin-left: 1px;
    }

    /* ── Responsive: small width ── */
    @media (max-width: 400px) {
        .big-pct { font-size: 24px; }
        .big-pct small { font-size: 14px; }
        .card-name { font-size: 12px; }
        .metric b { font-size: 20px; }
        .metric { font-size: 14px; }
        .header-title { font-size: 14px; }
        .header-pct { font-size: 18px; }
    }

    /* ── Responsive: short screens ── */
    @media (max-height: 600px) {
        .card-body { padding: 3px 6px; gap: 1px; }
        .big-pct { font-size: 22px; }
        .big-pct small { font-size: 12px; }
        .cap-bar { height: 8px; }
        .dash-header { padding: 4px 8px; }
        .card-grid { gap: 2px; }
        .card-name { font-size: 12px; }
        .metric b { font-size: 20px; }
    }
</style>



