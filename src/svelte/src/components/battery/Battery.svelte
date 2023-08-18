<script xmlns="http://www.w3.org/1999/html">
    import {currentView} from "../../stores";

    export let battery = {};
    export let height = 200;
</script>
<style>
    .battery {
        position: relative;
        display: block;
        margin: 35px 0 0 5px;
        background: #059669;
        width: 50px;
        height: 28px;
        float: left;
    }

    .battery:before {
        content: "";
        display: block;
        background: transparent;
        border: 6px solid #ffffff;
        margin: -12px;
        width: 85px;
        height: 40px;
        position: absolute;
        border-radius: 2px;
    }

    .battery:after {
        content: "";
        display: block;
        background: transparent;
        border: 6px solid #ffffff;
        margin: 0px 80px;
        width: 6px;
        height: 16px;
        position: absolute;
        border-radius: 2px;
    }</style>
<div on:click={() => currentView.set('dashboard')}>
    <div class="battery" style="width: {battery.capacity_percent * 15}%">
    </div>
</div>