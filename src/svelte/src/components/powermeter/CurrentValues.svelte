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
                <td>Load (W)</td>
                <td>Batt (V)</td>
                <td>Batt (W)</td>
                <td>Solar (W)</td>
                <td>Mode</td>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td>{(currentData?.load_amps * currentData?.battery_voltage)?.toFixed(2)}</td>
                <td>{currentData?.battery_voltage?.toFixed(2)}</td>
                <td>{(currentData?.battery_voltage * currentData?.battery_load)?.toFixed(2)}</td>
                <td>{currentData?.solar_watts?.toFixed(2)}</td>
                <td>{currentData?.charge_state}</td>
            </tr>
        </tbody>
    </table>
</div>