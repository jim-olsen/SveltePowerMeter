<script>
    import { onDestroy } from 'svelte';
    import { starlinkStatus } from "../../stores";
    let alerts = [];

    const unsubscribeStatus = starlinkStatus.subscribe(status => {
        alerts = [];
        for (const property in status.alerts) {
            if (status.alerts.hasOwnProperty(property)) {
                alerts.push({alertName: property, alertState: status.alerts[property]})
            }
        }
    } );

    onDestroy(unsubscribeStatus)
</script>
<div style="display:flex; flex-flow: column;" >
    {#each alerts as alert}
        <div style="display:flex; flex-flow: row wrap; justify-content: space-between; align-items: center; gap:10px;">
            <span class="smallText">{alert.alertName}</span>
            {#if alert.alertState}
                <div style="background-color: orangered; border-radius: 9999px; height: 1vw; width: 1vw;"></div>
            {:else}
                <div style="background-color: lightgreen; border-radius: 9999px; height: 1vw; width: 1vw;"></div>
            {/if}
        </div>
    {/each}
</div>