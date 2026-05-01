<script>
    import StarlinkStatusIndicator from "./StarlinkStatusIndicator.svelte";
    import StarlinkObstructionMap from "./StarlinkObstructionMap.svelte";
    import StarlinkFirmwareVersion from "./StarlinkFirmwareVersion.svelte";
    import StarlinkUpTime from "./StarlinkUpTime.svelte";
    import StarlinkAlerts from "./StarlinkAlerts.svelte";
    import {currentView} from "../../stores";
    import StarlinkAntenna from "./StarlinkAntenna.svelte";

    let displayAntenna = false;

    let outerHeight, outerWidth;

    $: mapSize = Math.max(120, Math.min(outerWidth || 0, outerHeight || 0, 250));
    $: antennaSize = Math.max(90, Math.min((outerWidth || 0) / 2.6, (outerHeight || 0) / 2.8, 150));
</script>

<div class="starlink-page" on:click|self={() => $currentView = 'dashboard'}>
    <div class="top-row">
        <div on:click={() => $currentView = 'dashboard'} class="status-panel card"
             bind:clientHeight={outerHeight} bind:clientWidth={outerWidth}>
            <div class="panel-title">Current Status</div>
            <StarlinkStatusIndicator />
            <div class="alerts-block">
                <span class="section-label">Alerts & Error Codes</span>
                <StarlinkAlerts/>
            </div>
        </div>
        <div class="map-panel card" on:click|stopPropagation={() => displayAntenna = !displayAntenna}>
            <div class="map-header">
                <span class="panel-title">{displayAntenna ? 'Antenna Orientation' : 'Obstruction Map'}</span>
                <button class="toggle-button" type="button">
                    {displayAntenna ? 'Show Obstruction Map' : 'Show Antenna'}
                </button>
            </div>
            {#if displayAntenna}
                <div class="antenna-wrap">
                    <StarlinkAntenna chartHeight={antennaSize}/>
                </div>
            {:else}
                <div class="map-wrap">
                    <StarlinkObstructionMap width={mapSize} height={mapSize}/>
                </div>
            {/if}
        </div>

    </div>
    <div on:click|self={() => $currentView = 'dashboard'} class="meta-row card">
        <div class="meta-item"><StarlinkFirmwareVersion/></div>
        <div class="meta-item"><StarlinkUpTime/></div>
    </div>
</div>

<style>
    .starlink-page {
        display: flex;
        flex-flow: column;
        justify-content: space-between;
        width: 100%;
        height: 100%;
        gap: 6px;
        color: #e6eaf2;
        box-sizing: border-box;
        overflow: hidden;
    }

    .top-row {
        display: flex;
        flex: 1;
        gap: 6px;
        min-height: 0;
    }

    .card {
        border-radius: 14px;
        padding: 8px;
        background: linear-gradient(145deg, rgba(34, 40, 56, 0.85), rgba(20, 24, 36, 0.85));
        border: 1px solid rgba(255, 255, 255, 0.08);
        box-shadow: 0 6px 18px rgba(0, 0, 0, 0.45), inset 0 1px 0 rgba(255, 255, 255, 0.04);
        backdrop-filter: blur(6px);
        -webkit-backdrop-filter: blur(6px);
        min-height: 0;
    }

    .status-panel {
        display: flex;
        flex: 1.4;
        flex-flow: column;
        justify-content: space-between;
        gap: 8px;
        min-width: 0;
        min-height: 0;
    }

    .alerts-block {
        display: flex;
        flex-flow: column;
        gap: 6px;
        min-height: 0;
        flex: 1;
        overflow: hidden;
    }

    .map-panel {
        flex: 1;
        display: flex;
        flex-flow: column;
        justify-content: space-between;
        gap: 8px;
        touch-action: manipulation;
        -webkit-tap-highlight-color: transparent;
        min-height: 0;
    }

    .panel-title {
        font-size: clamp(1.56rem, 2.9vw, 2rem);
        font-weight: 700;
        letter-spacing: 0.04em;
        text-transform: uppercase;
        line-height: 1.15;
    }

    .section-label {
        font-size: clamp(0.68rem, 1.2vw, 0.82rem);
        color: #aeb8cc;
        font-weight: 600;
        text-transform: uppercase;
    }

    .map-header {
        display: flex;
        flex-flow: column;
        gap: 6px;
        align-items: flex-start;
    }

    .toggle-button {
        border: 1px solid rgba(183, 140, 255, 0.45);
        background: rgba(183, 140, 255, 0.16);
        color: #e6eaf2;
        border-radius: 999px;
        padding: 6px 10px;
        font-size: clamp(0.66rem, 1.2vw, 0.78rem);
        font-weight: 600;
        min-height: 30px;
    }

    .map-wrap,
    .antenna-wrap {
        flex: 1;
        display: flex;
        align-items: center;
        justify-content: center;
        overflow: hidden;
        min-height: 0;
    }

    .meta-row {
        display: flex;
        justify-content: space-between;
        flex-wrap: wrap;
        gap: 6px;
        flex: 0 0 auto;
    }

    .meta-item {
        min-height: 30px;
        display: flex;
        align-items: center;
        padding: 2px 6px;
        border-radius: 10px;
        background: rgba(255, 255, 255, 0.04);
    }

    @media (max-width: 880px) {
        .starlink-page {
            gap: 4px;
        }

        .top-row {
            flex-flow: row;
            gap: 4px;
        }

        .status-panel {
            flex: 1.1;
        }

        .map-panel {
            flex: 0.9;
        }

        .card {
            padding: 6px;
            border-radius: 12px;
        }

        .panel-title {
            font-size: clamp(1.4rem, 3.6vw, 1.72rem);
        }

        .toggle-button {
            min-height: 26px;
            padding: 4px 8px;
        }

        .meta-item {
            min-height: 26px;
        }
    }

    @media (max-width: 560px), (max-height: 560px) {
        .top-row {
            gap: 3px;
        }

        .status-panel {
            flex: 1.2;
            gap: 5px;
        }

        .map-panel {
            flex: 0.8;
            gap: 5px;
        }

        .panel-title {
            letter-spacing: 0.03em;
        }

        .section-label {
            font-size: 0.62rem;
        }

        .meta-row {
            gap: 4px;
        }

        .meta-item {
            padding: 2px 5px;
        }
    }
</style>
