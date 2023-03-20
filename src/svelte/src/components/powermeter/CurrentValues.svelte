<script xmlns="http://www.w3.org/1999/html">
    import {powerCurrentData, currentView} from "../../stores";

</script>
<div style="display:flex; flex-flow:row; justify-content: space-between;" class="card" on:click={() => currentView.set('dashboard')}>
    <div style="display:flex; flex-flow:row; justify-content: flex-end; align-items: flex-end; flex: 2; gap: 10px;">
        <span class="normalText">{$powerCurrentData?.battery_voltage ? ($powerCurrentData?.battery_voltage)?.toFixed(1) : '---'}</span>
        <div style="display:flex; flex-flow:column; justify-content: stretch;">
            <span class="smallText">Batt</span>
            <span class="smallText">Volts</span>
        </div>
    </div>
    <div style="display:flex; flex-flow:row; justify-content: flex-end; align-items: flex-end; flex: 2; gap: 10px;">
        <span class="normalText">{$powerCurrentData?.load_amps ? ($powerCurrentData?.load_amps * $powerCurrentData?.battery_voltage)?.toFixed(1) : '---'}</span>
        <div style="display:flex; flex-flow:column; justify-content: stretch;">
            <span class="smallText">Load</span>
            <span class="smallText">Watts</span>
        </div>
    </div>
    <div style="display:flex; flex-flow:row; justify-content: flex-end; align-items: flex-end; flex: 2; gap: 10px;">
        <span class="normalText">{$powerCurrentData?.battery_load ? ($powerCurrentData?.battery_load * $powerCurrentData?.battery_voltage)?.toFixed(1) : '---'}</span>
        <div style="display:flex; flex-flow:column; justify-content: stretch;">
            <span class="smallText">Batt</span>
            <span class="smallText">Watts</span>
        </div>
    </div>
    <div style="display:flex; flex-flow:row; justify-content: flex-end; align-items: flex-end; flex: 2; gap: 10px;">
        <span class="normalText">{$powerCurrentData?.solar_watts ? $powerCurrentData?.solar_watts.toFixed(1) : '---'}</span>
        <div style="display:flex; flex-flow:column; justify-content: stretch;">
            <span class="smallText">Solar</span>
            <span class="smallText">Watts</span>
        </div>
    </div>
    <div style="display:flex; flex-flow:row; justify-content: flex-end; align-items: center; flex: 2; gap: 10px;">
        <span class="mediumSmallText">{$powerCurrentData?.charge_state ? $powerCurrentData?.charge_state : '---'}</span>
        <div style="display:flex; flex-flow:column; justify-content: stretch;">
            <span class="smallText">Charge</span>
            <span class="smallText">State</span>
        </div>
    </div>
</div>
