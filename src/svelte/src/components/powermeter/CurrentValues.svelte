<script xmlns="http://www.w3.org/1999/html">
    import {onDestroy} from 'svelte'
    import {powerCurrentData, currentView} from "../../stores";

    let currentData = {};

    const unsubscribeCurrent = powerCurrentData.subscribe(data => {
        currentData = data;
    });

    onDestroy(unsubscribeCurrent);
</script>
<div style="display:flex; flex-flow:row; justify-content: space-between;" on:click={() => currentView.set('dashboard')}>
    <div style="display:flex; flex-flow:row; justify-content: flex-end; align-items: flex-end; flex: 2; gap: 10px;">
        <span class="normalText">{currentData?.battery_voltage ? (currentData?.battery_voltage)?.toFixed(1) : '---'}</span>
        <div style="display:flex; flex-flow:column; justify-content: stretch;">
            <span class="smallText">Batt</span>
            <span class="smallText">Volts</span>
        </div>
    </div>
    <div style="display:flex; flex-flow:row; justify-content: flex-end; align-items: flex-end; flex: 2; gap: 10px;">
        <span class="normalText">{currentData?.load_amps ? (currentData?.load_amps * currentData?.battery_voltage)?.toFixed(1) : '---'}</span>
        <div style="display:flex; flex-flow:column; justify-content: stretch;">
            <span class="smallText">Load</span>
            <span class="smallText">Watts</span>
        </div>
    </div>
    <div style="display:flex; flex-flow:row; justify-content: flex-end; align-items: flex-end; flex: 2; gap: 10px;">
        <span class="normalText">{currentData?.battery_load ? (currentData?.battery_load * currentData?.battery_voltage)?.toFixed(1) : '---'}</span>
        <div style="display:flex; flex-flow:column; justify-content: stretch;">
            <span class="smallText">Batt</span>
            <span class="smallText">Watts</span>
        </div>
    </div>
    <div style="display:flex; flex-flow:row; justify-content: flex-end; align-items: flex-end; flex: 2; gap: 10px;">
        <span class="normalText">{currentData?.solar_watts ? currentData?.solar_watts.toFixed(1) : '---'}</span>
        <div style="display:flex; flex-flow:column; justify-content: stretch;">
            <span class="smallText">Solar</span>
            <span class="smallText">Watts</span>
        </div>
    </div>
    <div style="display:flex; flex-flow:row; justify-content: flex-end; align-items: center; flex: 2; gap: 10px;">
        <span class="mediumSmallText">{currentData?.charge_state ? currentData?.charge_state : '---'}</span>
        <div style="display:flex; flex-flow:column; justify-content: stretch;">
            <span class="smallText">Charge</span>
            <span class="smallText">State</span>
        </div>
    </div>
</div>
