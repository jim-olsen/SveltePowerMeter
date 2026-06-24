<script>
    import {onDestroy} from 'svelte';
    import {starlinkStatus} from "../../stores.svelte.js";

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
<div class="status-indicator">
    <div class="state-row">
        <span class="state-label">{state}</span>
        {#if state === 'CONNECTED'}
            <div class="state-dot connected"></div>
        {:else}
            <div class="state-dot disconnected"></div>
        {/if}
    </div>
    <div class="service-grid">
        {#each services as service}
            <div class="service-chip">
                <span class="service-name">{service.serviceName}</span>
                {#if service.serviceState}
                    <div class="service-dot ok"></div>
                {:else}
                    <div class="service-dot down"></div>
                {/if}
            </div>
        {/each}
    </div>
</div>

<style>
    .status-indicator {
        display: flex;
        flex-flow: column;
        gap: 6px;
        min-height: 0;
    }

    .state-row {
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 7px;
    }

    .state-label {
        font-size: clamp(0.82rem, 1.35vw, 1rem);
        font-weight: 700;
        letter-spacing: 0.05em;
        line-height: 1;
    }

    .state-dot,
    .service-dot {
        border-radius: 999px;
        flex: 0 0 auto;
    }

    .state-dot {
        width: 9px;
        height: 9px;
        box-shadow: 0 0 8px currentColor;
    }

    .connected,
    .ok {
        color: #7CFF9A;
        background: #7CFF9A;
    }

    .disconnected,
    .down {
        color: #FF5C5C;
        background: #FF5C5C;
    }

    .service-grid {
        display: grid;
        grid-template-columns: repeat(2, minmax(0, 1fr));
        gap: 5px;
        min-height: 0;
    }

    .service-chip {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 8px;
        padding: 4px 7px;
        border-radius: 999px;
        background: rgba(255, 255, 255, 0.06);
        min-width: 0;
    }

    .service-name {
        font-size: clamp(0.62rem, 1vw, 0.76rem);
        color: #c9d3e3;
        line-height: 1;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }

    .service-dot {
        width: 7px;
        height: 7px;
    }

    @media (max-width: 560px), (max-height: 560px) {
        .service-grid {
            gap: 4px;
        }

        .service-chip {
            padding: 3px 6px;
        }

        .service-name {
            font-size: 0.58rem;
        }
    }
    </style>


