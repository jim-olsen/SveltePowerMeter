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
                percentage = Math.min(100, Math.max(0, ((voltage - 2.5) / (3.65 - 2.5)) * 100));
                batteryFill.style.width = percentage + '%';
            }
        }
    }

    $: $batteryCurrentData, updateCellStatus();

</script>
<style>
    .battery {
        position: relative;
        display: block;
        margin: 0;
        width: 100%;
        height: 48px;
        flex-shrink: 0;
    }

    .battery:before {
        content: "";
        display: block;
        background: transparent;
        border: 3px solid #ffffff;
        margin: 0;
        width: 100%;
        height: 100%;
        position: absolute;
        border-radius: 2px;
        box-sizing: border-box;
    }

    .battery:after {
        content: "";
        display: block;
        background: transparent;
        border: 3px solid #ffffff;
        position: absolute;
        top: 25%;
        left: 100%;
        width: 8px;
        height: 50%;
        margin: 0;
        border-radius: 0 2px 2px 0;
        box-sizing: border-box;
    }

    .battery_level {
        margin: 3px;
        background: #059669;
        content: "";
        display: block;
        position: absolute;
        height: calc(100% - 6px);
        max-width: calc(100% - 6px);
    }
</style>
<div class="battery">
    <div bind:this={batteryFill} class="battery_level" style="width: {percentage}%;"></div>
</div>