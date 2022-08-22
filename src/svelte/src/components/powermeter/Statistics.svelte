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
                <td>{statsData?.day_load_wh ? statsData?.day_load_wh?.toFixed(1) : '---'} <small>wh</small></td>
                <td>Avg Use</td>
                <td>{statsData?.avg_load ? statsData?.avg_load?.toFixed(1) : '---'} <small>wh</small></td>
            </tr>
            <tr>
                <td>Today Solar</td>
                <td>{statsData?.day_solar_wh ? statsData?.day_solar_wh?.toFixed(1) : '---'} <small>wh</small></td>
                <td>Avg Solar</td>
                <td>{statsData?.avg_solar ? statsData?.avg_solar?.toFixed(1) : '---'} <small>wh</small></td>
            </tr>
        <tr>
            <td>Today Net</td>
            <td>{((statsData?.day_solar_wh ? statsData?.day_solar_wh : 0) - (statsData?.day_load_wh ? statsData?.day_load_wh : 0))?.toFixed(1)} <small>wh</small></td>
            <td>Avg Net</td>
            <td>{statsData?.avg_net ? statsData?.avg_net?.toFixed(1) : '---'} <small>wh</small></td>
        </tr>
        <tr>
            <td>Yesterday Net</td>
            <td>{statsData?.thirty_days_net ? statsData?.thirty_days_net?.[29]?.toFixed(1) : '---'} <small>wh</small></td>
            <td>Yesterday Use</td>
            <td>{statsData?.thirty_days_load ? statsData?.thirty_days_load?.[29]?.toFixed(1) : '---'} <small>wh</small></td>
        </tr>
        <tr>
            <td>Today Batt Use</td>
            <td>{statsData?.day_batt_wh ? statsData?.day_batt_wh?.toFixed(1) : '---'} <small>wh</small></td>
            <td>Yest Batt Use</td>
            <td>{statsData?.thirty_days_batt_wh?.[29] ? statsData?.thirty_days_batt_wh?.[29]?.toFixed(1) : '---'} <small>wh</small></td>
        </tr>
        <tr>
            <td>Five Day Net</td>
            <td>{(((statsData?.day_batt_wh ? statsData?.day_batt_wh : 0)
            + (statsData?.thirty_days_batt_wh?.[29] ? statsData?.thirty_days_batt_wh?.[29] : 0)
            + (statsData?.thirty_days_batt_wh?.[28] ? statsData?.thirty_days_batt_wh?.[28] : 0)
            + (statsData?.thirty_days_batt_wh?.[27] ? statsData?.thirty_days_batt_wh?.[27] : 0)
            + (statsData?.thirty_days_batt_wh?.[26] ? statsData?.thirty_days_batt_wh?.[26] : 0))
            * -1)?.toFixed(0)
            } <small>wh</small></td>
            <td>Ten Day Net</td>
            <td>{(((statsData?.day_batt_wh ? statsData?.day_batt_wh : 0)
            + (statsData?.thirty_days_batt_wh?.[29] ? statsData?.thirty_days_batt_wh?.[29] : 0)
            + (statsData?.thirty_days_batt_wh?.[28] ? statsData?.thirty_days_batt_wh?.[28] : 0)
            + (statsData?.thirty_days_batt_wh?.[27] ? statsData?.thirty_days_batt_wh?.[27] : 0)
            + (statsData?.thirty_days_batt_wh?.[26] ? statsData?.thirty_days_batt_wh?.[26] : 0)
            + (statsData?.thirty_days_batt_wh?.[25] ? statsData?.thirty_days_batt_wh?.[25] : 0)
            + (statsData?.thirty_days_batt_wh?.[24] ? statsData?.thirty_days_batt_wh?.[24] : 0)
            + (statsData?.thirty_days_batt_wh?.[23] ? statsData?.thirty_days_batt_wh?.[23] : 0)
            + (statsData?.thirty_days_batt_wh?.[22] ? statsData?.thirty_days_batt_wh?.[22] : 0)
            + (statsData?.thirty_days_batt_wh?.[21] ? statsData?.thirty_days_batt_wh?.[21] : 0))
            * -1)?.toFixed(0)
            } <small>wh</small></td>
        </tr>
        <tr>
            <td>Total Used</td>
            <td>{statsData?.total_load_wh ? statsData?.total_load_wh.toFixed(0) : '---'} <small>wh</small></td>
            <td>Total Solar</td>
            <td>{statsData?.total_solar_wh ? statsData?.total_solar_wh.toFixed(0) : '---'} <small>wh</small></td>
        </tr>
        </tbody>
    </table>
</div>