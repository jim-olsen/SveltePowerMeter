<script xmlns="http://www.w3.org/1999/xhtml">
    import Switch from "../Switch.svelte";
    import { onMount } from "svelte";

    export let shellyDeviceName

    let isOn = true;
    let switchValue = 'on';

    function getRelayStatus() {
        fetch(`/shelly/relay/status?name=${shellyDeviceName}&relay=0`, {
            headers: {
                "Accept": "application/json"
            }
        })
            .then(d => d.json())
            .then(d => {
                isOn = d.ison;
            });
    }

    function powerCycle() {
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
        if (switchValue == 'on') {
            fetch(`/shelly/relay/on?name=${shellyDeviceName}&relay=0`, {
                headers: {
                    "Accept": "application/json"
                }
            })
                .then(d => d.json())
                .then(d => {
                    isOn = d.ison;
                });
        } else {
            fetch(`/shelly/relay/off?name=${shellyDeviceName}&relay=0`, {
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

    onMount( async() => {
        getRelayStatus();
    });

    let statusInterval;
    $: {
        clearInterval(statusInterval);
        statusInterval = setInterval(getRelayStatus, 2000);
    }

    $:switchValue && executeCommand();
</script>
<Switch bind:value={switchValue} label={shellyDeviceName} cycleButton=true cycleButtonAction={powerCycle} fontSize={24} design="slider" />
