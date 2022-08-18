<script xmlns="http://www.w3.org/1999/html">
    import {onDestroy} from 'svelte'
    import {powerStatsData} from "../../stores";

    let statsData = {};

    const unsubscribeStats = powerStatsData.subscribe(data => {
        statsData = data;
    });

    onDestroy(unsubscribeStats);
</script>
<style>
    table td {
        border: 1px solid #fca503;
        text-align: center;
        font-size: 30px;
        color: #fca503;
        }
</style>
<div style="display:flex; flex-flow:column">
    <table>
        <tbody>
            <tr>
                <td>Today Usage</td>
                <td>{statsData?.day_load_wh ? statsData?.day_load_wh?.toFixed(2) : '---'} WH</td>
                <td>Avg Use</td>
                <td>{statsData?.avg_load ? statsData?.avg_load?.toFixed(2) : '---'} WH</td>
            </tr>
            <tr>
                <td>Today Solar</td>
                <td>{statsData?.day_solar_wh ? statsData?.day_solar_wh?.toFixed(2) : '---'} WH</td>
                <td>Avg Solar</td>
                <td>{statsData?.avg_solar ? statsData?.avg_solar?.toFixed(2) : '---'} WH</td>
            </tr>
        <tr>
            <td>Today Net</td>
            <td>{((statsData?.day_solar_wh ? statsData?.day_solar_wh : 0) - (statsData?.day_load_wh ? statsData?.day_load_wh : 0))?.toFixed(2)} WH</td>
            <td>Avg Net</td>
            <td>{statsData?.avg_net ? statsData?.avg_net?.toFixed(2) : '---'} WH</td>
        </tr>
        <tr>
            <td>Yesterday Net</td>
            <td>{statsData?.thirty_days_net ? statsData?.thirty_days_net?.[29]?.toFixed(2) : '---'} WH</td>
            <td>Yesterday Use</td>
            <td>{statsData?.thirty_days_load ? statsData?.thirty_days_load?.[29]?.toFixed(2) : '---'} WH</td>
        </tr>
        <tr>
            <td>Today Batt Use</td>
            <td>{statsData?.day_batt_wh ? statsData?.day_batt_wh?.toFixed(2) : '---'} WH</td>
            <td>Five Day Net</td>
            <td>{((statsData?.day_batt_wh ? statsData?.day_batt_wh : 0
                    + statsData?.thirty_days_batt_wh?.[29] ? statsData?.thirty_days_batt_wh?.[29] : 0
                    + statsData?.thirty_days_batt_wh?.[28] ? statsData?.thirty_days_batt_wh?.[28] : 0
                    + statsData?.thirty_days_batt_wh?.[27] ? statsData?.thirty_days_batt_wh?.[27] : 0
                    + statsData?.thirty_days_batt_wh?.[26] ? statsData?.thirty_days_batt_wh?.[26] : 0) * -1)?.toFixed(2)
                    } WH</td>
        </tr>
        </tbody>
    </table>
</div>