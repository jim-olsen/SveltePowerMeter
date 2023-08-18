<script xmlns="http://www.w3.org/1999/html">
    import {batteryCurrentData, currentView} from "../../stores";

    export let battery = {};
    let batteryFill;



    function updateCellStatus() {
        if (batteryFill && battery.protection_status.indexOf('Cell Block Over-Vol') > -1) {
            batteryFill.style.background = 'orangered';
        } else if (batteryFill && battery.control_status === 'Discharging') {
            batteryFill.style.background = 'blue';
        }  else if (batteryFill && battery.control_status == 'Charging') {
            batteryFill.style.background = 'yellow';
        }  else if (batteryFill) {
            batteryFill.style.background = 'lightgreen';
        }
    }

    $: $batteryCurrentData, updateCellStatus();

</script>
<style>
    .battery {
        position: relative;
        display: block;
        margin: 0 0 0 5px;
        width: 50px;
        height: 28px;
        float: left;
    }

    .battery:before {
        content: "";
        display: block;
        background: transparent;
        border: 6px solid #ffffff;
        margin: 0px;
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
        margin: 12px 93px;
        width: 6px;
        height: 16px;
        position: absolute;
        border-radius: 2px;
    }

    .battery_level {
        margin: 12px;
        background: #059669;
        content: "";
        display: block;
        position: absolute;
        height: 100%;
    }
</style>
<div on:click={() => currentView.set('dashboard')} style="height: 60px;">
    <div class="battery">
        <div bind:this={batteryFill} class="battery_level" style="width: {battery.capacity_percent * 1.45}%;"></div>
    </div>
</div>