<script>
    import {onDestroy} from 'svelte';
    import {starlinkStatus} from "../../stores";

    let services = [];
    let state = "UNKNOWN";

    const unsubscribeStatus = starlinkStatus.subscribe(status => {
        state = status.state;
        services = [];
        for (const property in status.ready_states) {
            if (status.ready_states.hasOwnProperty(property)) {
                services.push({serviceName: property, serviceState: status.ready_states[property]})
            }
        }
    });

    onDestroy(unsubscribeStatus)
</script>
<div style="display:flex; flex-flow:column; justify-content: space-between;">
    <div style="display:flex; flex-flow: row; justify-content: center; align-items: center; gap: 30px;">
        <span class="normalText">{state}</span>
        {#if state === 'CONNECTED'}
            <div style="background-color: lightgreen; border-radius: 9999px; height: 2vw; width: 2vw"></div>
        {:else}
            <div style="background-color: orangered; border-radius: 9999px; height: 2vw; width: 2vw"></div>
        {/if}
    </div>
    <div style="display:flex; flex-flow: row wrap; justify-content: space-around; gap: 20px;">
        {#each services as service}
            <div style="display:flex; flex-flow: row; justify-content: space-between; align-items: center; gap:10px;">
                <span class="smallText">{service.serviceName}</span>
                {#if service.serviceState}
                    <div style="background-color: lightgreen; border-radius: 9999px; height: 1vw; width: 1vw;"></div>
                {:else}
                    <div style="background-color: orangered; border-radius: 9999px; height: 1vw; width: 1vw;"></div>
                {/if}
            </div>
        {/each}
    </div>
</div>