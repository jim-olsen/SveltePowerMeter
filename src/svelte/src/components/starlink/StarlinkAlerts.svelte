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
<div class="alerts-grid-wrap">
    <div class="alerts-grid">
        {#each alerts as alert}
            <div class="alert-item" class:active={alert.alertState}>
                <span class="alert-name">{alert.alertName}</span>
                <div class="alert-status">
                    <span class="status-text">{alert.alertState ? 'ACTIVE' : 'OK'}</span>
                    {#if alert.alertState}
                        <div class="alert-dot critical"></div>
                    {:else}
                        <div class="alert-dot ok"></div>
                    {/if}
                </div>
            </div>
        {/each}
    </div>
</div>

<style>
    .alerts-grid-wrap {
        width: 100%;
        min-height: 0;
        overflow: hidden;
        border-radius: 10px;
        border: 1px solid rgba(255, 255, 255, 0.08);
        background: rgba(255, 255, 255, 0.02);
        padding: 4px;
    }

    .alerts-grid {
        display: grid;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: 3px;
        width: 100%;
    }

    .alert-item {
        min-height: 21px;
        padding: 3px 5px;
        font-size: clamp(0.54rem, 0.88vw, 0.68rem);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 8px;
        line-height: 1.05;
        color: #d6deeb;
        display: flex;
        justify-content: space-between;
        align-items: center;
        gap: 4px;
        background: rgba(124, 255, 154, 0.04);
    }

    .alert-item.active {
        background: rgba(255, 92, 92, 0.12);
    }

    .alert-name {
        overflow-wrap: anywhere;
        line-height: 1.1;
        flex: 1;
        min-width: 0;
    }

    .alert-status {
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 4px;
        font-weight: 600;
    }

    .status-text {
        letter-spacing: 0.01em;
        font-size: 0.92em;
    }

    .alert-dot {
        width: 6px;
        height: 6px;
        border-radius: 999px;
        flex: 0 0 auto;
    }

    .critical {
        background: #FF5C5C;
        box-shadow: 0 0 10px rgba(255, 92, 92, 0.8);
    }

    .ok {
        background: #7CFF9A;
    }

    @media (max-width: 520px) {
        .alerts-grid-wrap {
            padding: 3px;
        }

        .alerts-grid {
            grid-template-columns: repeat(2, minmax(0, 1fr));
            gap: 3px;
        }

        .alert-item {
            padding: 3px 4px;
            min-height: 20px;
            font-size: 0.54rem;
        }

        .status-text {
            letter-spacing: 0.01em;
        }
    }
    </style>