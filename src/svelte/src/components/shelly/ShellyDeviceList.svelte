<script>
    import ShellyRelayDevice from "./ShellyRelayDevice.svelte";
    import {onDestroy, onMount} from "svelte";
    import {currentView} from "../../stores";

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

    onDestroy(() => { clearInterval(deviceInterval)})
</script>
<div role="button" tabindex="0" style="display: flex; flex-flow: row wrap; justify-content: center; align-content: center; row-gap: 15px; gap: 15px;"
     on:click={(e) => {if (e.target === this) {$currentView = 'dashboard'}}}
     on:keydown={(e) => {if ((e.key === 'Enter' || e.key === ' ') && e.target === e.currentTarget) {$currentView = 'dashboard'}}}>
{#each shellyDevices as device}
        <ShellyRelayDevice shellyDeviceName={device.name} />
{/each}
</div>