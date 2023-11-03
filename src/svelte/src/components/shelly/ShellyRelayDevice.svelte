<script xmlns="http://www.w3.org/1999/xhtml">
    import {onDestroy, onMount} from "svelte";
    import {faLightbulb, faRefresh} from "@fortawesome/free-solid-svg-icons";
    import Fa from "svelte-fa";

    export let shellyDeviceName

    let isOn = true;
    let deviceIcon;

    function getRelayStatus() {
        fetch(`/shelly/relay/status?name=${shellyDeviceName}&relay=0`, {
            headers: {
                "Accept": "application/json"
            }
        })
            .then(d => d.json())
            .then(d => {
                isOn = d.ison;
                if (deviceIcon?.style?.color && isOn) {
                    deviceIcon.style.color = 'gold';
                } else {
                    deviceIcon.style.color = 'darkgray';
                }
            });
    }

    function powerCycle() {
        console.log("power cycle")
        fetch(`/shelly/relay/cycle?name=${shellyDeviceName}&relay=0&delay=10`, {
            headers: {
                "Accept": "application/json"
            }
        })
            .then(d => d.json())
            .then(d => {
                isOn = d.ison;
            });
    }

    function executeCommand() {
        if (isOn) {
            console.log("Turn light off")
            fetch(`/shelly/relay/off?name=${shellyDeviceName}&relay=0`, {
                headers: {
                    "Accept": "application/json"
                }
            })
                .then(d => d.json())
                .then(d => {
                    isOn = d.ison;
                });
        } else {
            console.log("Turn light on")
            fetch(`/shelly/relay/on?name=${shellyDeviceName}&relay=0`, {
                headers: {
                    "Accept": "application/json"
                }
            })
                .then(d => d.json())
                .then(d => {
                    isOn = d.ison;
                });
        }

    }

    onMount(async () => {
        getRelayStatus();
    });

    let statusInterval;
    $: {
        clearInterval(statusInterval);
        statusInterval = setInterval(getRelayStatus, 2000);
    }

    onDestroy(() => clearInterval(statusInterval));
</script>
<div class="card"
     style="display: flex; flex-flow: column; justify-content: center; align-items: center; flex: 1 0 25%;">
    <span class="normalText">{shellyDeviceName}</span>
    <div style="display: flex; flex-flow: row; justify-content: space-between; font-size: 6vw;width: 100%;">
        <div bind:this={deviceIcon} on:click={(e) => {executeCommand(); e.stopPropagation()}} style="font-size: 6vw; color: darkgray;">
            <Fa icon="{faLightbulb}" style="font-size: 6vw;"/>
        </div>
        <div on:click={(e) => {powerCycle(); e.stopPropagation();}}>
            <Fa icon="{faRefresh}" style="font-size: 6vw; color: darkgray;"/>
        </div>
    </div>
</div>
