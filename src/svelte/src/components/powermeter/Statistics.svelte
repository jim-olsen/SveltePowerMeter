<script xmlns="http://www.w3.org/1999/html">
    import {powerStatsData, currentView} from "../../stores";
</script>
<div style="display: flex; flex-flow: column; justify-content: space-between; align-items: flex-start; width:100%; height: 100%;"
        on:click={() => $currentView = 'dashboard'}>
    <div style="display:flex; flex-flow:row; justify-content: space-between; width: 100%;">
        <div style="display:flex; flex-flow:row; justify-content: flex-end; align-items: flex-end; flex: 2; gap: 10px;">
        </div>
        <div style="display:flex; flex-flow:row; justify-content: flex-end; align-items: flex-end; flex: 2; gap: 10px;">
        </div>
        <div style="display:flex; flex-flow:row; justify-content: flex-end; align-items: flex-end; flex: 2; gap: 10px;">
        </div>
        <div style="display:flex; flex-flow:row; justify-content: flex-end; align-items: flex-end; flex: 2; gap: 10px;">
        </div>
    </div>
    <div style="display:flex; flex-flow:row; justify-content: space-between; width: 100%;" class="card" >
        <div style="display:flex; flex-flow:row; justify-content: flex-end; align-items: flex-end; flex: 2; gap: 10px;">
            <span class="normalText">{$powerStatsData?.day_load_wh ? $powerStatsData?.day_load_wh?.toFixed(1) : '---'}</span>
            <div style="display:flex; flex-flow:column; justify-content: stretch;">
                <span class="smallText">Today</span>
                <span class="smallText">Use Wh</span>
            </div>
        </div>
        <div style="display:flex; flex-flow:row; justify-content: flex-end; align-items: flex-end; flex: 2; gap: 10px;">
            <span class="normalText">{$powerStatsData?.avg_load ? $powerStatsData?.avg_load?.toFixed(1) : '---'}</span>
            <div style="display:flex; flex-flow:column; justify-content: stretch;">
                <span class="smallText">Avg</span>
                <span class="smallText">Use Wh</span>
            </div>
        </div>
        <div style="display:flex; flex-flow:row; justify-content: flex-end; align-items: flex-end; flex: 2; gap: 10px;">
            <span class="normalText">{$powerStatsData?.day_batt_wh ? $powerStatsData?.day_batt_wh?.toFixed(1) : '---'}</span>
            <div style="display:flex; flex-flow:column; justify-content: stretch;">
                <span class="smallText">Batt</span>
                <span class="smallText">Use Wh</span>
            </div>
        </div>
        <div style="display:flex; flex-flow:row; justify-content: flex-end; align-items: flex-end; flex: 2; gap: 10px;">
            <span class="normalText">{$powerStatsData?.yesterday_batt_wh ? $powerStatsData?.yesterday_batt_wh?.toFixed(1) : '---'}</span>
            <div style="display:flex; flex-flow:column; justify-content: stretch;">
                <span class="smallText">Yest Batt</span>
                <span class="smallText">Use Wh</span>
            </div>
        </div>
    </div>
    <div style="display:flex; flex-flow:row; justify-content: space-between; width: 100%;" class="card">
        <div style="display:flex; flex-flow:row; justify-content: flex-end; align-items: flex-end; flex: 2; gap: 10px;">
            <span class="normalText">{$powerStatsData?.day_solar_wh ? $powerStatsData?.day_solar_wh?.toFixed(1) : '---'}</span>
            <div style="display:flex; flex-flow:column; justify-content: stretch;">
                <span class="smallText">Today</span>
                <span class="smallText">Solar Wh</span>
            </div>
        </div>
        <div style="display:flex; flex-flow:row; justify-content: flex-end; align-items: flex-end; flex: 2; gap: 10px;">
            <span class="normalText">{$powerStatsData?.avg_solar ? $powerStatsData?.avg_solar?.toFixed(1) : '---'}</span>
            <div style="display:flex; flex-flow:column; justify-content: stretch;">
                <span class="smallText">Avg</span>
                <span class="smallText">Solar Wh</span>
            </div>
        </div>
        <div style="display:flex; flex-flow:row; justify-content: flex-end; align-items: flex-end; flex: 2; gap: 10px;">
            <span class="normalText">{(($powerStatsData?.day_solar_wh ? $powerStatsData?.day_solar_wh : 0) - ($powerStatsData?.day_load_wh ? $powerStatsData?.day_load_wh : 0))?.toFixed(1)}</span>
            <div style="display:flex; flex-flow:column; justify-content: stretch;">
                <span class="smallText">Today</span>
                <span class="smallText">Net Wh</span>
            </div>
        </div>
        <div style="display:flex; flex-flow:row; justify-content: flex-end; align-items: flex-end; flex: 2; gap: 10px;">
            <span class="normalText">{$powerStatsData?.avg_net ? $powerStatsData?.avg_net?.toFixed(1) : '---'}</span>
            <div style="display:flex; flex-flow:column; justify-content: stretch;">
                <span class="smallText">Avg</span>
                <span class="smallText">Net Wh</span>
            </div>
        </div>
    </div>
    <div style="display:flex; flex-flow:row; justify-content: space-between; width: 100%;" class="card">
        <div style="display:flex; flex-flow:row; justify-content: flex-end; align-items: flex-end; flex: 2; gap: 10px;">
            <span class="normalText">{$powerStatsData?.yesterday_load_wh ? $powerStatsData?.yesterday_load_wh?.toFixed(1) : '---'}</span>
            <div style="display:flex; flex-flow:column; justify-content: stretch;">
                <span class="smallText">Yest</span>
                <span class="smallText">Use Wh</span>
            </div>
        </div>
        <div style="display:flex; flex-flow:row; justify-content: flex-end; align-items: flex-end; flex: 2; gap: 10px;">
            <span class="normalText">{$powerStatsData?.yesterday_net_wh ? $powerStatsData?.yesterday_net_wh?.toFixed(1) : '---'}</span>
            <div style="display:flex; flex-flow:column; justify-content: stretch;">
                <span class="smallText">Yest</span>
                <span class="smallText">Net Wh</span>
            </div>
        </div>
        <div style="display:flex; flex-flow:row; justify-content: flex-end; align-items: flex-end; flex: 2; gap: 10px;">
            <span class="normalText">{($powerStatsData?.five_day_net ? $powerStatsData?.five_day_net : 0)?.toFixed(0)}</span>
            <div style="display:flex; flex-flow:column; justify-content: stretch;">
                <span class="smallText">5 Day</span>
                <span class="smallText">Net Wh</span>
            </div>
        </div>
        <div style="display:flex; flex-flow:row; justify-content: flex-end; align-items: flex-end; flex: 2; gap: 10px;">
            <span class="normalText">{($powerStatsData?.ten_day_net ? $powerStatsData?.ten_day_net : 0)?.toFixed(0)}</span>
            <div style="display:flex; flex-flow:column; justify-content: stretch;">
                <span class="smallText">10 Day</span>
                <span class="smallText">Net Wh</span>
            </div>
        </div>
    </div>
    <div style="display:flex; flex-flow:row; justify-content: space-between; width: 100%;" class="card" >
        <div style="display:flex; flex-flow:row; justify-content: flex-end; align-items: flex-end; flex: 2; gap: 10px;">
            <span class="normalText">{$powerStatsData?.battery_min_percent?.toFixed(0) ?? '---'}/{$powerStatsData?.battery_max_percent?.toFixed(0) ?? '---'}</span>
            <div style="display:flex; flex-flow:column; justify-content: stretch;">
                <span class="smallText">% Min/Max</span>
                <span class="smallText">Today</span>
            </div>
        </div>
        <div style="display:flex; flex-flow:row; justify-content: flex-end; align-items: flex-end; flex: 2; gap: 10px;">
            <span class="normalText">{$powerStatsData?.battery_min_percent_one_day_ago?.toFixed(0) ?? '---'}/{$powerStatsData?.battery_max_percent_one_day_ago?.toFixed(0) ?? '---'}</span>
            <div style="display:flex; flex-flow:column; justify-content: stretch;">
                <span class="smallText">% Min/Max</span>
                <span class="smallText">Yesterday</span>
            </div>
        </div>
        <div style="display:flex; flex-flow:row; justify-content: flex-end; align-items: flex-end; flex: 2; gap: 10px;">
            <span class="normalText">{$powerStatsData?.battery_min_percent_two_days_ago?.toFixed(0) ?? '---'}/{$powerStatsData?.battery_max_percent_two_days_ago?.toFixed(0) ?? '---'}</span>
            <div style="display:flex; flex-flow:column; justify-content: stretch;">
                <span class="smallText">% Min/Max</span>
                <span class="smallText">2 Days Ago</span>
            </div>
        </div>
        <div style="display:flex; flex-flow:row; justify-content: flex-end; align-items: flex-end; flex: 2; gap: 10px;">
            <span class="normalText">{$powerStatsData?.battery_min_percent_three_days_ago?.toFixed(0) ?? '---'}/{$powerStatsData?.battery_max_percent_three_days_ago?.toFixed(0) ?? '---'}</span>
            <div style="display:flex; flex-flow:column; justify-content: stretch;">
                <span class="smallText">% Min/Max</span>
                <span class="smallText">3 Days Ago</span>
            </div>
        </div>
    </div>
</div>
