<script xmlns="http://www.w3.org/1999/html">
    import {batteryCurrentData, currentView} from "../../stores";

    export let voltageIndex = 0;
    export let battery_name;
    let voltage = 0.0;
    let percentage = 0;
    let batteryFill;
    let battery;



    function updateCellStatus() {
        if (batteryFill && battery && battery.protection_status.indexOf('Cell Block Over-Vol') > -1) {
            batteryFill.style.background = 'orangered';
        } else if (batteryFill && battery && battery.control_status === 'Discharging') {
            batteryFill.style.background = 'blue';
        }  else if (batteryFill && battery && battery.control_status == 'Charging') {
            batteryFill.style.background = 'yellow';
        }  else if (batteryFill && battery) {
            batteryFill.style.background = 'lightgreen';
        }

        if (battery_name) {
            $batteryCurrentData.forEach(batt => {
                if (batt.name === battery_name) {
                    battery = batt;
                }
            });

            if (battery && batteryFill) {
                voltage = battery.cell_block_voltages[voltageIndex];
                percentage = ((voltage / 3.6) * 100) * 1.45;
                batteryFill.style.width = percentage;
            }
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
<div style="height: 60px;">
    <div class="battery">
        <div bind:this={batteryFill} class="battery_level" style="width: {percentage}%;"></div>
    </div>
</div>