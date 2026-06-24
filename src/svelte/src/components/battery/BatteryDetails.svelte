<script>
    import {batteryCurrentData} from "../../stores.svelte.js";
    import {currentView} from "../../states.svelte.js";
    import {onMount} from "svelte";
    import Fa from "svelte-fa";
    import {faCarBattery, faThermometerHalf, faShieldAlt, faSync, faCheckCircle} from "@fortawesome/free-solid-svg-icons";
    import Cell from "./Cell.svelte";

    let battery_name = currentView.value.replace('battery_details_', '')
    let battery = {};
    let cells = [];
    let temps = [];
    let status = "Unknown";
    let cycles = 0;
    let protection_status = [];

    onMount(async () => {
        $batteryCurrentData.forEach(batt => { if (batt.name === battery_name) {
            battery = batt;
            cells = battery.cell_block_voltages;
            temps = battery.battery_temps_f;
            status = battery.control_status;
            cycles = battery.cycles;
            protection_status = battery.protection_status;
        }});
    });

    function statusColor(s) {
        if (s === 'Charging') return '#7CFF9A';
        if (s === 'Discharging') return '#FFE45E';
        return '#8892A6';
    }
</script>

<div class="details" on:click={() => currentView.value = 'battery_dashboard'}>
    <!-- HEADER -->
    <div class="tile-header">
        <div class="tile-icon">
            <Fa icon={faCarBattery}/>
        </div>
        <div class="tile-title">{battery_name}</div>
        <div class="tile-badge" style="color: {statusColor(status)};">
            {status}
        </div>
    </div>

    <!-- CELLS -->
    <div class="section-label">Cell Voltages</div>
    <div class="cells-grid">
        {#each cells as cell_voltage, index}
            <div class="cell-item">
                <Cell voltageIndex={index} battery_name={battery_name} />
                <span class="cell-voltage">{cell_voltage}</span>
            </div>
        {/each}
    </div>

    <!-- TEMPS & STATUS ROW -->
    <div class="metric-grid">
        {#each temps as temp, i}
            <div class="metric">
                <div class="metric-icon"><Fa icon={faThermometerHalf}/></div>
                <div class="metric-value">{temp.toFixed(1)}<span class="unit">°F</span></div>
                <div class="metric-label">Temp {i + 1}</div>
            </div>
        {/each}
        <div class="metric">
            <div class="metric-icon"><Fa icon={faSync}/></div>
            <div class="metric-value">{cycles}</div>
            <div class="metric-label">Cycles</div>
        </div>
    </div>

    <!-- PROTECTION STATUS -->
    <div class="protection-row">
        {#each protection_status as ps}
            <span class="sub-chip warn">
                <Fa icon={faShieldAlt}/>
                {ps}
            </span>
        {:else}
            <span class="sub-chip ok">
                <Fa icon={faCheckCircle}/>
                No Protection Issues
            </span>
        {/each}
    </div>
</div>

<style>
    .details {
        display: flex;
        flex-direction: column;
        width: 100%;
        height: 100%;
        box-sizing: border-box;
        padding: 6px 8px;
        color: #e6eaf2;
        font-family: inherit;
        overflow: hidden;
        gap: 6px;
        --accent: #7CFF9A;
    }

    .tile-header {
        display: flex;
        align-items: center;
        gap: 8px;
        height: 56px;
        flex: 0 0 auto;
    }

    .tile-icon {
        display: flex;
        align-items: center;
        justify-content: center;
        width: 48px;
        height: 48px;
        border-radius: 12px;
        background: rgba(255, 255, 255, 0.05);
        font-size: 26px;
        flex: 0 0 auto;
        color: var(--accent);
    }

    .tile-title {
        font-size: 22px;
        font-weight: 700;
        letter-spacing: 0.5px;
        color: #e6eaf2;
        flex: 1;
        text-transform: uppercase;
    }

    .tile-badge {
        font-size: 18px;
        font-weight: 700;
        padding: 5px 12px;
        border-radius: 999px;
        background: rgba(255, 255, 255, 0.06);
        color: #e6eaf2;
        display: inline-flex;
        align-items: center;
        gap: 6px;
        white-space: nowrap;
    }

    .section-label {
        font-size: 14px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        color: #b0b9c8;
        flex: 0 0 auto;
    }

    .cells-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 6px;
        flex: 1 1 auto;
        background: rgba(255, 255, 255, 0.035);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 10px;
        padding: 8px;
        overflow: hidden;
    }

    .cell-item {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 4px;
        min-width: 0;
        padding: 0 8px;
    }

    .cell-voltage {
        font-size: 18px;
        font-weight: 700;
        color: #fca503;
        font-variant-numeric: tabular-nums;
        white-space: nowrap;
    }

    .metric-grid {
        display: flex;
        gap: 6px;
        flex: 1 1 auto;
    }

    .metric {
        flex: 1;
        background: rgba(255, 255, 255, 0.035);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 10px;
        padding: 8px 4px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        gap: 4px;
    }

    .metric-icon {
        font-size: 32px;
        color: var(--accent);
        opacity: 0.85;
    }

    .metric-value {
        font-size: 36px;
        font-weight: 700;
        color: #fca503;
        line-height: 1;
        text-align: center;
        letter-spacing: 0.5px;
        text-shadow: 0 1px 2px rgba(0, 0, 0, 0.5);
        font-variant-numeric: tabular-nums;
    }

    .metric-value .unit {
        font-size: 20px;
        font-weight: 500;
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

    .protection-row {
        display: flex;
        flex-wrap: wrap;
        gap: 4px;
        flex: 0 0 auto;
    }

    .sub-chip {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        font-size: 20px;
        font-weight: 600;
        padding: 6px 14px;
        border-radius: 999px;
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.06);
        color: #cbd2df;
    }

    .sub-chip.ok {
        color: #7CFF9A;
    }

    .sub-chip.warn {
        color: #FF5C5C;
    }

    @media (max-width: 380px) {
        .metric-value { font-size: 24px; }
        .metric-icon { font-size: 20px; }
        .tile-title { font-size: 18px; }
        .tile-badge { font-size: 14px; }
        .cell-voltage { font-size: 12px; }
    }
</style>



