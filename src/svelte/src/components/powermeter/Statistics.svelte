<script xmlns="http://www.w3.org/1999/html">
    import {onDestroy} from 'svelte'
    import {powerStatsData, currentView} from "../../stores";

    let statsData = {};

    const unsubscribeStats = powerStatsData.subscribe(data => {
        statsData = data;
    });

    onDestroy(unsubscribeStats);
</script>
<div style="display: flex; flex-flow: column; justify-content: space-between; align-items: flex-start; width:100%; height: 100%;"
        on:click={() => currentView.set('dashboard')}>
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
            <span class="normalText">{statsData?.day_load_wh ? statsData?.day_load_wh?.toFixed(1) : '---'}</span>
            <div style="display:flex; flex-flow:column; justify-content: stretch;">
                <span class="smallText">Today</span>
                <span class="smallText">Use Wh</span>
            </div>
        </div>
        <div style="display:flex; flex-flow:row; justify-content: flex-end; align-items: flex-end; flex: 2; gap: 10px;">
            <span class="normalText">{statsData?.avg_load ? statsData?.avg_load?.toFixed(1) : '---'}</span>
            <div style="display:flex; flex-flow:column; justify-content: stretch;">
                <span class="smallText">Avg</span>
                <span class="smallText">Use Wh</span>
            </div>
        </div>
        <div style="display:flex; flex-flow:row; justify-content: flex-end; align-items: flex-end; flex: 2; gap: 10px;">
            <span class="normalText">{statsData?.day_batt_wh ? statsData?.day_batt_wh?.toFixed(1) : '---'}</span>
            <div style="display:flex; flex-flow:column; justify-content: stretch;">
                <span class="smallText">Batt</span>
                <span class="smallText">Use Wh</span>
            </div>
        </div>
        <div style="display:flex; flex-flow:row; justify-content: flex-end; align-items: flex-end; flex: 2; gap: 10px;">
            <span class="normalText">{statsData?.yesterday_batt_wh ? statsData?.yesterday_batt_wh?.toFixed(1) : '---'}</span>
            <div style="display:flex; flex-flow:column; justify-content: stretch;">
                <span class="smallText">Yest Batt</span>
                <span class="smallText">Use Wh</span>
            </div>
        </div>
    </div>
    <div style="display:flex; flex-flow:row; justify-content: space-between; width: 100%;" class="card">
        <div style="display:flex; flex-flow:row; justify-content: flex-end; align-items: flex-end; flex: 2; gap: 10px;">
            <span class="normalText">{statsData?.day_solar_wh ? statsData?.day_solar_wh?.toFixed(1) : '---'}</span>
            <div style="display:flex; flex-flow:column; justify-content: stretch;">
                <span class="smallText">Today</span>
                <span class="smallText">Solar Wh</span>
            </div>
        </div>
        <div style="display:flex; flex-flow:row; justify-content: flex-end; align-items: flex-end; flex: 2; gap: 10px;">
            <span class="normalText">{statsData?.avg_solar ? statsData?.avg_solar?.toFixed(1) : '---'}</span>
            <div style="display:flex; flex-flow:column; justify-content: stretch;">
                <span class="smallText">Avg</span>
                <span class="smallText">Solar Wh</span>
            </div>
        </div>
        <div style="display:flex; flex-flow:row; justify-content: flex-end; align-items: flex-end; flex: 2; gap: 10px;">
            <span class="normalText">{((statsData?.day_solar_wh ? statsData?.day_solar_wh : 0) - (statsData?.day_load_wh ? statsData?.day_load_wh : 0))?.toFixed(1)}</span>
            <div style="display:flex; flex-flow:column; justify-content: stretch;">
                <span class="smallText">Today</span>
                <span class="smallText">Net Wh</span>
            </div>
        </div>
        <div style="display:flex; flex-flow:row; justify-content: flex-end; align-items: flex-end; flex: 2; gap: 10px;">
            <span class="normalText">{statsData?.avg_net ? statsData?.avg_net?.toFixed(1) : '---'}</span>
            <div style="display:flex; flex-flow:column; justify-content: stretch;">
                <span class="smallText">Avg</span>
                <span class="smallText">Net Wh</span>
            </div>
        </div>
    </div>
    <div style="display:flex; flex-flow:row; justify-content: space-between; width: 100%;" class="card">
        <div style="display:flex; flex-flow:row; justify-content: flex-end; align-items: flex-end; flex: 2; gap: 10px;">
            <span class="normalText">{statsData?.yesterday_load_wh ? statsData?.yesterday_load_wh?.toFixed(1) : '---'}</span>
            <div style="display:flex; flex-flow:column; justify-content: stretch;">
                <span class="smallText">Yest</span>
                <span class="smallText">Use Wh</span>
            </div>
        </div>
        <div style="display:flex; flex-flow:row; justify-content: flex-end; align-items: flex-end; flex: 2; gap: 10px;">
            <span class="normalText">{statsData?.yesterday_net_wh ? statsData?.yesterday_net_wh?.toFixed(1) : '---'}</span>
            <div style="display:flex; flex-flow:column; justify-content: stretch;">
                <span class="smallText">Yest</span>
                <span class="smallText">Net Wh</span>
            </div>
        </div>
        <div style="display:flex; flex-flow:row; justify-content: flex-end; align-items: flex-end; flex: 2; gap: 10px;">
            <span class="normalText">{(statsData?.five_day_net ? statsData?.five_day_net : 0)?.toFixed(0)}</span>
            <div style="display:flex; flex-flow:column; justify-content: stretch;">
                <span class="smallText">5 Day</span>
                <span class="smallText">Net Wh</span>
            </div>
        </div>
        <div style="display:flex; flex-flow:row; justify-content: flex-end; align-items: flex-end; flex: 2; gap: 10px;">
            <span class="normalText">{(statsData?.ten_day_net ? statsData?.ten_day_net : 0)?.toFixed(0)}</span>
            <div style="display:flex; flex-flow:column; justify-content: stretch;">
                <span class="smallText">10 Day</span>
                <span class="smallText">Net Wh</span>
            </div>
        </div>
    </div>
    <div style="display:flex; flex-flow:row; justify-content: space-between; width: 100%;" class="card" >
        <div style="display:flex; flex-flow:row; justify-content: flex-end; align-items: flex-end; flex: 2; gap: 10px;">
            <span class="normalText">{statsData?.total_load_wh ? statsData?.total_load_wh.toFixed(0) : '---'}</span>
            <div style="display:flex; flex-flow:column; justify-content: stretch;">
                <span class="smallText">Total</span>
                <span class="smallText">Use Wh</span>
            </div>
        </div>
        <div style="display:flex; flex-flow:row; justify-content: flex-end; align-items: flex-end; flex: 2; gap: 10px;">
            <span class="normalText">{statsData?.total_solar_wh ? statsData?.total_solar_wh.toFixed(0) : '---'}</span>
            <div style="display:flex; flex-flow:column; justify-content: stretch;">
                <span class="smallText">Total</span>
                <span class="smallText">Solar Wh</span>
            </div>
        </div>
        <div style="display:flex; flex-flow:row; justify-content: flex-end; align-items: flex-end; flex: 2; gap: 10px;">
        </div>
        <div style="display:flex; flex-flow:row; justify-content: flex-end; align-items: flex-end; flex: 2; gap: 10px;">
        </div>
    </div>
</div>
