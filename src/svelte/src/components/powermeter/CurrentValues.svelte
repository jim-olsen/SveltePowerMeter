<script xmlns="http://www.w3.org/1999/html">
    import {onDestroy} from 'svelte'
    import {powerCurrentData} from "../../stores";

    let currentData = {};

    const unsubscribeCurrent = powerCurrentData.subscribe(data => {
        currentData = data;
    });

    onDestroy(unsubscribeCurrent);
</script>
<style>
    table td {
        border: 1px solid #fca503;
        text-align: center;
        font-size: 30px;
        color: #fca503;
        }
</style>
<div style="display:flex; flex-flow:column;justify-content: center;">
    <table style="width: 100%;">
        <thead>
            <tr>
                <td>Load</td>
                <td>Battery</td>
                <td>Battery</td>
                <td>Solar</td>
                <td>Mode</td>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td>{currentData?.load_amps ? (currentData?.load_amps * currentData?.battery_voltage)?.toFixed(1) : '---'} <small>w</small></td>
                <td>{currentData?.battery_voltage ? currentData?.battery_voltage?.toFixed(2) : '---'} <small>v</small></td>
                <td>{currentData?.battery_voltage ? (currentData?.battery_voltage * currentData?.battery_load)?.toFixed(1) : '---'} <small>w</small></td>
                <td>{currentData?.solar_watts ? currentData?.solar_watts.toFixed(1) : '---'} <small>w</small></td>
                <td>{currentData?.charge_state ? currentData?.charge_state : '---'}</td>
            </tr>
        </tbody>
    </table>
</div>