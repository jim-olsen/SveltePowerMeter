<script>
    import Fa from "svelte-fa";
    import {faArrowLeft, faImage, faInfoCircle, faLink, faBullseye, faStopwatch, faClock} from "@fortawesome/free-solid-svg-icons";
    import {birdData} from "../../stores.svelte.js";
    import {currentView} from "../../states.svelte.js";

    let scientificName = '';
    let bird = {};
    let count = 0;
    let image = null;
    let lastFetchedName = '';

    $: scientificName = currentView.value.startsWith('bird_details_')
        ? currentView.value.substring('bird_details_'.length)
        : '';

    $: {
        let entry = $birdData[scientificName];
        bird = entry?.bird ?? {};
        count = entry?.count ?? 0;
    }

    $: if (scientificName && scientificName !== lastFetchedName) {
        lastFetchedName = scientificName;
        image = null;
        fetch(`/birdPicture?scientificName=${encodeURIComponent(scientificName)}`, {
            headers: {
                "Accept": "application/json"
            }
        })
            .then(d => d.json())
            .then(d => {
                image = d?.image ?? null;
            });
    }

    function goBack() {
        currentView.value = 'birdDashboard';
    }

    function fmtConfidence(v) {
        return v === undefined || v === null ? '---' : (Number(v) * 100).toFixed(1) + '%';
    }

    function fmtTime(v) {
        return v === undefined || v === null ? '---' : new Date(v).toLocaleString();
    }
</script>

<div class="bird-details">
    <div class="dash-header" role="button" tabindex="0" on:click={goBack} on:keydown={(event) => (event.key === 'Enter' || event.key === ' ') && goBack()}>
        <div class="back-btn"><Fa icon={faArrowLeft}/></div>
        <div class="header-title">{bird.common_name ?? 'Unknown Bird'}</div>
        <div class="header-count">{count}</div>
    </div>

    <div class="content">
        <div class="tile tile-picture">
            {#if image}
                <img src="{'data:image/jpeg;base64, ' + image}" alt="{bird.common_name}" class="bird-img"/>
            {:else}
                <div class="no-picture">
                    <Fa icon={faImage} style="font-size: 48px; opacity: 0.3;"/>
                    <span>No Picture Available</span>
                </div>
            {/if}
        </div>

        <div class="tile tile-info">
            <div class="info-row">
                <span class="scientific-name">{bird.scientific_name ?? '---'}</span>
            </div>
            <div class="info-row">
                <span class="stat"><Fa icon={faBullseye}/> {fmtConfidence(bird.confidence)}</span>
                <span class="stat"><Fa icon={faStopwatch}/> {bird.start_time ?? '---'}s - {bird.end_time ?? '---'}s</span>
            </div>
            <div class="info-row">
                <span class="stat"><Fa icon={faClock}/> Last heard: {fmtTime(bird.time)}</span>
            </div>
            {#if bird.description}
                <div class="description">
                    <Fa icon={faInfoCircle}/> {bird.description}
                </div>
            {/if}
            <div class="links">
                {#if bird.media_url}
                    <a class="link" href="{bird.media_url}" target="_blank" rel="noreferrer"><Fa icon={faLink}/> Source: {bird.source ?? 'link'}</a>
                {/if}
            </div>
        </div>
    </div>
</div>

<style>
    .bird-details {
        display: flex;
        flex-direction: column;
        width: 100%;
        height: 100%;
        box-sizing: border-box;
        padding: 3px;
        gap: 4px;
        color: #e6eaf2;
        font-family: inherit;
        overflow: hidden;
    }

    .dash-header {
        display: flex;
        align-items: center;
        gap: 14px;
        padding: 10px 16px;
        border-radius: 10px;
        background: linear-gradient(145deg, rgba(34, 40, 56, 0.85), rgba(20, 24, 36, 0.85));
        border: 1px solid rgba(255, 255, 255, 0.06);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.4), inset 0 1px 0 rgba(255, 255, 255, 0.04);
        cursor: pointer;
        -webkit-tap-highlight-color: transparent;
        touch-action: manipulation;
        transition: transform 0.15s ease;
        flex-shrink: 0;
    }
    .dash-header:active { transform: scale(0.985); }

    .back-btn { font-size: 26px; color: #8892A6; }
    .header-title { font-size: 24px; font-weight: 700; letter-spacing: 0.5px; flex: 1; }
    .header-count { font-size: 30px; font-weight: 700; font-variant-numeric: tabular-nums; color: #fca503; }

    .content {
        display: flex;
        flex-direction: column;
        gap: 4px;
        flex: 1;
        min-height: 0;
        overflow-y: auto;
    }

    .tile {
        border-radius: 12px;
        padding: 10px 14px;
        background: linear-gradient(145deg, rgba(34, 40, 56, 0.85), rgba(20, 24, 36, 0.85));
        border: 1px solid rgba(255, 255, 255, 0.06);
        box-shadow: 0 6px 18px rgba(0, 0, 0, 0.45), inset 0 1px 0 rgba(255, 255, 255, 0.04);
    }

    .tile-picture {
        flex: 2 0 0;
        display: flex;
        align-items: center;
        justify-content: center;
        min-height: 0;
        overflow: hidden;
    }

    .bird-img {
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

    .tile-info {
        flex: 1 0 0;
        display: flex;
        flex-direction: column;
        gap: 10px;
    }

    .info-row {
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
        align-items: center;
    }

    .scientific-name {
        font-size: 20px;
        font-style: italic;
        color: #8892A6;
    }

    .stat {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        font-size: 18px;
        font-weight: 600;
        padding: 6px 12px;
        border-radius: 10px;
        background: rgba(255, 255, 255, 0.04);
        border: 1px solid rgba(255, 255, 255, 0.05);
        color: #fca503;
    }

    .description {
        font-size: 16px;
        color: #cbd2df;
        line-height: 1.4;
        display: flex;
        gap: 8px;
        align-items: flex-start;
    }

    .links {
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
    }

    .link {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        font-size: 16px;
        color: #5EC6FF;
        text-decoration: none;
    }

    @media (max-width: 400px) {
        .header-title { font-size: 16px; }
        .header-count { font-size: 20px; }
        .scientific-name { font-size: 14px; }
        .stat { font-size: 14px; }
        .description { font-size: 13px; }
    }
</style>
