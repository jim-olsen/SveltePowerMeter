<script xmlns="http://www.w3.org/1999/html">
    import {currentView} from "../../stores";

    export let battery = {};
    export let height = 200;
</script>
<style>
    .battery {
        border: 4px solid #ffffff;
        border-radius: 20px;
        position: relative;
        margin: 15px 0 20%;
    }

    .battery :before {
        content: '';
        height: 5%;
        width: 70%;
        background: #ffffff;
        display: block;
        position: relative;
        top: -35px;
        border-radius: 4px 4px 0 0;
        margin-left: 15%;
    }

    .battery :after {
        content: '';
        display: block;
        position: absolute;
        top: -1px;
        left: -1px;
        right: -1px;
        bottom: -1px;
        border: 1px solid #ffffff;
        border-radius: 2px;
    }

    .battery-level {
        background: #30b455;
        position: absolute;
        bottom: 0;
        left: 0;
        right: 0;
    }
</style>
<div style="display:flex; flex-direction: column; justify-content: space-between; align-items: center; gap:10px;"
     on:click={() => currentView.set('dashboard')}>
    <div class="battery" style="height: {height / 3}px; width: {height}px;">
        <div class="battery-level" style="width:{battery.capacity_percent}%"></div>
    </div>
</div>