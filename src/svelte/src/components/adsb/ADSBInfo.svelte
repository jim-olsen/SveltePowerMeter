<script>
    import Fa from "svelte-fa";
    import {
        faPlane,
        faTachometerAlt,
        faArrowsAltV,
        faBroadcastTower,
        faTag,
        faUser,
        faInfoCircle,
        faImage
    } from "@fortawesome/free-solid-svg-icons";
    import {adsbData, currentView} from "../../stores";

    let categories = {
        "A0": "No Info",
        "A1": "Light (<15.5k lbs)",
        "A2": "Small (15.5-75k lbs)",
        "A3": "Large (75-300k lbs)",
        "A4": "High Vortex",
        "A5": "Heavy (>300k lbs)",
        "A6": "High Performance",
        "A7": "Rotorcraft",
        "B0": "No Info",
        "B1": "Glider",
        "B2": "Balloon",
        "B3": "Parachute",
        "B4": "Ultralight",
        "B5": "Reserved",
        "B6": "UAV",
        "B7": "Space",
        "C0": "Land Unk",
        "C1": "Emergency Vehicle",
        "C2": "Service Vehicle",
        "C3": "Point Obstacle",
        "C4": "Cluster Obstacle",
        "C5": "Line Obstacle",
        "C6": "C6",
        "C7": "C7"
    };

    function val(key, fallback = 'Unknown') {
        return $adsbData.hasOwnProperty(key) ? $adsbData[key] : fallback;
    }
</script>

<div class="adsb-dash" on:click={() => currentView.set('dashboard')}>
    <!-- COMPACT HEADER BAR -->
    <div class="tile tile-flight">
        <div class="header-row">
            <span class="flight-icon"><Fa icon={faPlane}/></span>
            <span class="flight-name">{val('flight', 'Unknown')}</span>
            <span class="flight-badge">{val('r_dst', '?')} nm</span>
        </div>
        <div class="stats-row">
            <span class="stat">
                <Fa icon={faArrowsAltV}/>
                {val('alt_baro', '---')}<span class="unit"> ft</span>
            </span>
            <span class="stat">
                <Fa icon={faTachometerAlt}/>
                {val('gs', '---')}<span class="unit"> kt</span>
            </span>
            <span class="stat">
                <Fa icon={faBroadcastTower}/>
                {val('squawk', '---')}
            </span>
            <span class="stat">
                <Fa icon={faTag}/>
                {$adsbData.hasOwnProperty('category') ? categories[$adsbData.category] : '---'}
            </span>
        </div>
        <div class="stats-row details-row">
            <span class="stat">
                <Fa icon={faInfoCircle}/>
                {val('desc', '---')}
            </span>
            <span class="stat">
                <Fa icon={faUser}/>
                {val('ownOp', '---')}
            </span>
        </div>
    </div>

    <!-- PICTURE -->
    <div class="tile tile-picture">
        {#if $adsbData.hasOwnProperty('picture')}
            <img src="{'data:image/png;base64, ' + $adsbData.picture}" alt="Aircraft" class="aircraft-img"/>
        {:else}
            <div class="no-picture">
                <Fa icon={faImage} style="font-size: 48px; opacity: 0.3;"/>
                <span>No Picture Available</span>
            </div>
        {/if}
    </div>
</div>

<style>
    .adsb-dash {
        display: flex;
        flex-direction: column;
        gap: 4px;
        width: 100%;
        height: 100%;
        box-sizing: border-box;
        padding: 2px;
        color: #e6eaf2;
        font-family: inherit;
        overflow: hidden;
    }

    .tile {
        position: relative;
        border-radius: 12px;
        padding: 6px 10px;
        background: linear-gradient(145deg, rgba(34, 40, 56, 0.85), rgba(20, 24, 36, 0.85));
        border: 1px solid rgba(255, 255, 255, 0.06);
        box-shadow: 0 6px 18px rgba(0, 0, 0, 0.45), inset 0 1px 0 rgba(255, 255, 255, 0.04);
        backdrop-filter: blur(6px);
        -webkit-backdrop-filter: blur(6px);
        overflow: hidden;
        -webkit-tap-highlight-color: transparent;
        touch-action: manipulation;
    }

    .tile::before {
        content: "";
        position: absolute;
        inset: 0;
        border-radius: inherit;
        pointer-events: none;
        opacity: 0.18;
        background: radial-gradient(circle at top right, var(--accent, #5EC6FF), transparent 60%);
    }

    .tile-flight  { --accent: #5EC6FF; flex: 1 0 0; display: flex; flex-direction: column; }
    .tile-picture { --accent: #fca503; flex: 2 0 0; display: flex; align-items: center; justify-content: center; min-height: 0; }

    .header-row {
        display: flex;
        align-items: center;
        gap: 8px;
        margin-bottom: 6px;
        flex: 0 0 auto;
    }

    .flight-icon {
        display: flex;
        align-items: center;
        justify-content: center;
        width: 44px;
        height: 44px;
        border-radius: 12px;
        background: rgba(255, 255, 255, 0.05);
        font-size: 24px;
        color: var(--accent);
        flex: 0 0 auto;
    }

    .flight-name {
        font-size: 26px;
        font-weight: 700;
        letter-spacing: 0.5px;
        color: #e6eaf2;
        flex: 1;
        text-transform: uppercase;
    }

    .flight-badge {
        font-size: 20px;
        font-weight: 700;
        padding: 4px 12px;
        border-radius: 999px;
        background: rgba(255, 255, 255, 0.06);
        color: #fca503;
        white-space: nowrap;
        font-variant-numeric: tabular-nums;
    }

    .stats-row {
        display: flex;
        flex-wrap: wrap;
        gap: 6px;
        margin-bottom: 4px;
        flex: 1 1 auto;
        align-content: center;
    }

    .stat {
        display: inline-flex;
        align-items: center;
        gap: 10px;
        font-size: 32px;
        font-weight: 600;
        padding: 12px 18px;
        border-radius: 10px;
        background: rgba(255, 255, 255, 0.04);
        border: 1px solid rgba(255, 255, 255, 0.05);
        color: #fca503;
        white-space: nowrap;
        font-variant-numeric: tabular-nums;
    }

    .stat :global(svg) {
        color: var(--accent);
        opacity: 0.85;
        font-size: 28px;
    }

    .stat .unit {
        font-size: 22px;
        font-weight: 500;
        color: #e6eaf2;
    }

    .details-row .stat {
        color: #cbd2df;
        white-space: normal;
        word-break: break-word;
    }

    .aircraft-img {
        width: 100%;
        height: 100%;
        object-fit: contain;
        border-radius: 10px;
    }

    .no-picture {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        gap: 12px;
        padding: 32px;
        color: #8892A6;
        font-size: 18px;
        font-weight: 600;
    }

    @media (max-width: 500px) {
        .flight-name { font-size: 20px; }
        .flight-badge { font-size: 18px; padding: 3px 10px; }
        .flight-icon { width: 38px; height: 38px; font-size: 20px; }
        .stat { font-size: 26px; padding: 10px 14px; }
        .stat :global(svg) { font-size: 22px; }
        .stat .unit { font-size: 18px; }
        .adsb-dash { gap: 3px; padding: 1px; }
    }

    @media (max-width: 380px) {
        .stat { font-size: 22px; padding: 8px 12px; gap: 7px; }
        .flight-name { font-size: 18px; }
    }

    @media (max-height: 700px) {
        .tile { padding: 4px 8px; }
        .header-row { margin-bottom: 3px; }
        .stat { font-size: 26px; padding: 8px 14px; }
        .stat :global(svg) { font-size: 22px; }
        .adsb-dash { gap: 3px; padding: 1px; }
    }
</style>
