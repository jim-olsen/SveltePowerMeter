<script>
    import { powerStatsData, currentView } from "../../stores";

    // Helper for formatting
    const format = (val, dec = 1) => (val !== undefined && val !== null) ? val.toFixed(dec) : '---';
</script>

<div class="stats-container" role="button" tabindex="0" on:click={() => $currentView = 'dashboard'} on:keydown={(event) => (event.key === 'Enter' || event.key === ' ') && ($currentView = 'dashboard')}>
    <!-- Row 1: Load / Usage Stats -->
    <div class="stats-grid">
        <div class="card stat-item">
            <span class="smallText">Today Use</span>
            <span class="normalText">{format($powerStatsData?.day_load_wh)} <span class="unit">Wh</span></span>
        </div>
        <div class="card stat-item">
            <span class="smallText">Avg Use</span>
            <span class="normalText">{format($powerStatsData?.avg_load)} <span class="unit">Wh</span></span>
        </div>
        <div class="card stat-item">
            <span class="smallText">Batt Use</span>
            <span class="normalText">{format($powerStatsData?.day_batt_wh)} <span class="unit">Wh</span></span>
        </div>
        <div class="card stat-item">
            <span class="smallText">Yest Batt</span>
            <span class="normalText">{format($powerStatsData?.yesterday_batt_wh)} <span class="unit">Wh</span></span>
        </div>
    </div>

    <!-- Row 2: Solar & Net Stats -->
    <div class="stats-grid">
        <div class="card stat-item solar">
            <span class="smallText">Today Solar</span>
            <span class="normalText">{format($powerStatsData?.day_solar_wh)} <span class="unit">Wh</span></span>
        </div>
        <div class="card stat-item solar">
            <span class="smallText">Avg Solar</span>
            <span class="normalText">{format($powerStatsData?.avg_solar)} <span class="unit">Wh</span></span>
        </div>
        <div class="card stat-item net">
            <span class="smallText">Today Net</span>
            <span class="normalText">{format(($powerStatsData?.day_solar_wh || 0) - ($powerStatsData?.day_load_wh || 0))} <span class="unit">Wh</span></span>
        </div>
        <div class="card stat-item net">
            <span class="smallText">Avg Net</span>
            <span class="normalText">{format($powerStatsData?.avg_net)} <span class="unit">Wh</span></span>
        </div>
    </div>

    <!-- Row 3: History Net Stats -->
    <div class="stats-grid">
        <div class="card stat-item">
            <span class="smallText">Yest Use</span>
            <span class="normalText">{format($powerStatsData?.yesterday_load_wh)} <span class="unit">Wh</span></span>
        </div>
        <div class="card stat-item">
            <span class="smallText">Yest Net</span>
            <span class="normalText">{format($powerStatsData?.yesterday_net_wh)} <span class="unit">Wh</span></span>
        </div>
        <div class="card stat-item">
            <span class="smallText">5 Day Net</span>
            <span class="normalText">{format($powerStatsData?.five_day_net, 0)} <span class="unit">Wh</span></span>
        </div>
        <div class="card stat-item">
            <span class="smallText">10 Day Net</span>
            <span class="normalText">{format($powerStatsData?.ten_day_net, 0)} <span class="unit">Wh</span></span>
        </div>
    </div>

    <!-- Row 4: Battery Min/Max History -->
    <div class="stats-grid">
        <div class="card stat-item batt">
            <span class="smallText">Batt Today</span>
            <span class="normalText">
                {format($powerStatsData?.battery_min_percent, 0)}<span class="sep">/</span>{format($powerStatsData?.battery_max_percent, 0)}<span class="unit">%</span>
            </span>
        </div>
        <div class="card stat-item batt">
            <span class="smallText">Batt Yest</span>
            <span class="normalText">
                {format($powerStatsData?.battery_min_percent_one_day_ago, 0)}<span class="sep">/</span>{format($powerStatsData?.battery_max_percent_one_day_ago, 0)}<span class="unit">%</span>
            </span>
        </div>
        <div class="card stat-item batt">
            <span class="smallText">Batt -2 Days</span>
            <span class="normalText">
                {format($powerStatsData?.battery_min_percent_two_days_ago, 0)}<span class="sep">/</span>{format($powerStatsData?.battery_max_percent_two_days_ago, 0)}<span class="unit">%</span>
            </span>
        </div>
        <div class="card stat-item batt">
            <span class="smallText">Batt -3 Days</span>
            <span class="normalText">
                {format($powerStatsData?.battery_min_percent_three_days_ago, 0)}<span class="sep">/</span>{format($powerStatsData?.battery_max_percent_three_days_ago, 0)}<span class="unit">%</span>
            </span>
        </div>
    </div>
</div>

<style>
    .stats-container {
        display: flex;
        flex-direction: column;
        gap: 8px;
        width: 100%;
        height: 100%;
        padding: 4px;
        box-sizing: border-box;
        cursor: pointer;
    }

    .stats-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 8px;
        flex: 1;
    }

    .stat-item {
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        text-align: center;
        padding: 8px 4px;
        min-width: 0; /* allows shrinking */
    }

    .stat-item .normalText {
        font-size: 4.5vw;
    }

    .stat-item .smallText {
        margin-bottom: 2px;
        font-size: 1.8vw; /* Slightly larger than global default for readability */
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        width: 100%;
    }

    .unit {
        font-size: 0.7em;
        opacity: 0.7;
        margin-left: 2px;
        font-weight: 500;
        text-transform: none;
    }

    .sep {
        opacity: 0.4;
        margin: 0 1px;
    }

    /* Accent colors for different types of data */
    .solar .normalText {
        color: var(--ok);
    }

    .net .normalText {
        color: var(--accent-cool);
    }

    .batt .normalText {
        color: var(--warn);
    }

    @media (max-width: 500px) {
        .stats-grid {
            gap: 4px;
        }
        .stat-item .normalText {
            font-size: 7.5vw;
        }
        .stat-item .smallText {
            font-size: 3.2vw;
        }
        .stats-container {
            gap: 4px;
            padding: 2px;
        }
    }
</style>
