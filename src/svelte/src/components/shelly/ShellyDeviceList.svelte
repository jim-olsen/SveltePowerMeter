<script xmlns="http://www.w3.org/1999/xhtml">
    import ShellyRelayDevice from "./ShellyRelayDevice.svelte";
    import { onMount } from "svelte";

    let shellyDevices = []

    function getDevices() {
        fetch('/shelly', {
            headers: {
                "Accept": "application.json"
            }
        })
            .then(d => d.json())
            .then(d => {
                shellyDevices = d;
            })
    }

    onMount( async() => {
        getDevices();
    });

    let deviceInterval;
    $: {
        clearInterval(deviceInterval);
        deviceInterval = setInterval(getDevices, 5000);
    }
</script>
{#each shellyDevices as device}
    <div style="display:flex; flex-flow: column; gap:10px">
        <ShellyRelayDevice shellyDeviceName={device.name} />
    </div>
{/each}