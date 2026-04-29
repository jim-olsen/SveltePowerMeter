<script xmlns="http://www.w3.org/1999/html">
    import {powerCurrentData, currentView} from "../../stores";

</script>
<div class="current-values-card card" on:click={() => currentView.set('dashboard')}>
    <div class="value-item">
        <span class="normalText">{$powerCurrentData?.battery_voltage ? ($powerCurrentData?.battery_voltage)?.toFixed(1) : '---'}</span>
        <div class="label-group">
            <span class="smallText">Batt</span>
            <span class="smallText">Volts</span>
        </div>
    </div>
    <div class="value-item">
        <span class="normalText">{$powerCurrentData?.load_watts ? $powerCurrentData?.load_watts?.toFixed(1) : '---'}</span>
        <div class="label-group">
            <span class="smallText">Load</span>
            <span class="smallText">Watts</span>
        </div>
    </div>
    <div class="value-item">
        <span class="normalText">{$powerCurrentData?.battery_load ? ($powerCurrentData?.battery_load * $powerCurrentData?.battery_voltage)?.toFixed(1) : '---'}</span>
        <div class="label-group">
            <span class="smallText">Batt</span>
            <span class="smallText">Watts</span>
        </div>
    </div>
    <div class="value-item">
        <span class="normalText">{$powerCurrentData?.solar_watts ? $powerCurrentData?.solar_watts.toFixed(1) : '---'}</span>
        <div class="label-group">
            <span class="smallText">Solar</span>
            <span class="smallText">Watts</span>
        </div>
    </div>
    <div class="value-item">
        <span class="mediumSmallText">{$powerCurrentData?.charge_state ? $powerCurrentData?.charge_state : '---'}</span>
        <div class="label-group">
            <span class="smallText">Charge</span>
            <span class="smallText">State</span>
        </div>
    </div>
</div>

<style>
    .current-values-card {
        display: flex;
        flex-flow: row;
        justify-content: space-between;
        padding: 4px 8px;
    }

    .value-item {
        display: flex;
        flex-flow: row;
        justify-content: flex-end;
        align-items: flex-end;
        flex: 1;
        gap: 6px;
        min-width: 0;
    }

    .label-group {
        display: flex;
        flex-flow: column;
        justify-content: stretch;
        line-height: 1;
    }

    .value-item .normalText {
        font-size: 4.5vw;
    }

    .value-item .mediumSmallText {
        font-size: 3.5vw;
    }

    .value-item .smallText {
        font-size: 1.6vw;
    }

    @media (max-width: 500px) {
        .value-item {
            gap: 4px;
        }
        .value-item .normalText {
            font-size: 7.5vw;
        }
        .value-item .mediumSmallText {
            font-size: 5vw;
        }
        .value-item .smallText {
            font-size: 2.8vw;
        }
    }
</style>
