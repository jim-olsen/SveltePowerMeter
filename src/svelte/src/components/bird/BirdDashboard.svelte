<script>
    import Fa from "svelte-fa";
    import {faCrow, faArrowLeft, faClockRotateLeft, faImage, faBullseye, faClock, faInfoCircle, faLink} from "@fortawesome/free-solid-svg-icons";
    import {birdData} from "../../stores.svelte.js";
    import {currentView} from "../../states.svelte.js";

    let birds = [];
    let flashingBirds = {};
    let previousCounts = {};
    let liveMode = false;
    let latestBird = null;
    let latestImage = null;
    let lastFetchedImageName = '';
    let birdThumbnails = {};

    $: birds = Object.values($birdData)
        .filter(entry => entry?.bird?.scientific_name)
        .sort((a, b) => b.count - a.count);

    $: {
        for (const entry of birds) {
            const name = entry.bird.scientific_name;
            const prevCount = previousCounts[name];
            if (prevCount !== undefined && entry.count > prevCount) {
                flashBird(name);
                latestBird = entry;
            }
            previousCounts[name] = entry.count;
        }
    }

    $: if (!latestBird && birds.length > 0) {
        latestBird = birds.slice().sort((a, b) => new Date(b.bird.time ?? 0) - new Date(a.bird.time ?? 0))[0];
    }

    $: {
        for (const entry of birds) {
            fetchThumbnail(entry.bird.scientific_name);
        }
    }

    $: if (latestBird && latestBird.bird.scientific_name !== lastFetchedImageName) {
        lastFetchedImageName = latestBird.bird.scientific_name;
        latestImage = null;
        fetch(`/birdPicture?scientificName=${encodeURIComponent(latestBird.bird.scientific_name)}`, {
            headers: {
                "Accept": "application/json"
            }
        })
            .then(d => d.json())
            .then(d => {
                latestImage = d?.image ?? null;
            });
    }

    function fetchThumbnail(name) {
        if (!name || Object.prototype.hasOwnProperty.call(birdThumbnails, name)) {
            return;
        }
        birdThumbnails[name] = null;
        birdThumbnails = birdThumbnails;
        fetch(`/birdPicture?scientificName=${encodeURIComponent(name)}`, {
            headers: {
                "Accept": "application/json"
            }
        })
            .then(d => d.json())
            .then(d => {
                birdThumbnails[name] = d?.image ?? null;
                birdThumbnails = birdThumbnails;
            });
    }

    function flashBird(name) {
        flashingBirds[name] = true;
        flashingBirds = flashingBirds;
        setTimeout(() => {
            delete flashingBirds[name];
            flashingBirds = flashingBirds;
        }, 1000);
    }

    function go(view) {
        return () => currentView.value = view;
    }

    function enterLiveMode() {
        liveMode = true;
    }

    function exitLiveMode() {
        liveMode = false;
    }

    function fmtConfidence(v) {
        return v === undefined || v === null ? '---' : (Number(v) * 100).toFixed(1) + '%';
    }

    function fmtTime(v) {
        return v === undefined || v === null ? '---' : new Date(v).toLocaleString();
    }
</script>

<div class="bird-dash">
    {#if liveMode}
        <div class="dash-header" role="button" tabindex="0" on:click={exitLiveMode} on:keydown={(event) => (event.key === 'Enter' || event.key === ' ') && exitLiveMode()}>
            <div class="back-btn"><Fa icon={faArrowLeft}/></div>
            <div class="header-title">{latestBird?.bird?.common_name ?? 'Listening...'}</div>
            <div class="header-count">{latestBird?.count ?? 0}</div>
        </div>

        <div class="live-content">
            <div class="tile tile-picture">
                {#if latestImage}
                    <img src="{'data:image/jpeg;base64, ' + latestImage}" alt="{latestBird?.bird?.common_name}" class="bird-img"/>
                {:else}
                    <div class="no-picture">
                        <Fa icon={faImage} style="font-size: 48px; opacity: 0.3;"/>
                        <span>No Picture Available</span>
                    </div>
                {/if}
            </div>

            {#if latestBird}
                <div class="tile tile-info">
                    <div class="info-row">
                        <span class="scientific-name">{latestBird.bird.scientific_name ?? '---'}</span>
                    </div>
                    <div class="info-row">
                        <span class="stat"><Fa icon={faBullseye}/> {fmtConfidence(latestBird.bird.confidence)}</span>
                    </div>
                    <div class="info-row">
                        <span class="stat"><Fa icon={faClock}/> Last heard: {fmtTime(latestBird.bird.time)}</span>
                    </div>
                    {#if latestBird.bird.description}
                        <div class="description">
                            <Fa icon={faInfoCircle}/> {latestBird.bird.description}
                        </div>
                    {/if}
                    <div class="links">
                        {#if latestBird.bird.media_url}
                            <a class="link" href="{latestBird.bird.media_url}" target="_blank" rel="noreferrer"><Fa icon={faLink}/> Source: {latestBird.bird.source ?? 'link'}</a>
                        {/if}
                    </div>
                </div>
            {:else}
                <div class="no-birds">No Birds Detected Yet</div>
            {/if}
        </div>
    {:else}
        <div class="dash-header" role="button" tabindex="0" on:click={go('dashboard')} on:keydown={(event) => (event.key === 'Enter' || event.key === ' ') && go('dashboard')()}>
            <div class="back-btn"><Fa icon={faArrowLeft}/></div>
            <div class="header-icon"><Fa icon={faCrow}/></div>
            <div class="header-title">Birds</div>
            <div class="header-count">{birds.length}</div>
            <div class="history-btn" role="button" tabindex="0"
                 on:click|stopPropagation={go('birdHistory')}
                 on:keydown|stopPropagation={(event) => (event.key === 'Enter' || event.key === ' ') && go('birdHistory')()}>
                <Fa icon={faClockRotateLeft}/>
            </div>
        </div>

        <div class="bird-list">
            {#each birds as entry}
                <div class="bird-row" class:bird-detected={flashingBirds[entry.bird.scientific_name]} role="button" tabindex="0"
                     on:click={go('bird_details_' + entry.bird.scientific_name)}
                     on:keydown={(event) => (event.key === 'Enter' || event.key === ' ') && go('bird_details_' + entry.bird.scientific_name)()}>
                    <div class="bird-names">
                        <span class="common-name" class:new-bird={entry.bird.is_new}>{entry.bird.common_name}</span>
                        <span class="scientific-name">{entry.bird.scientific_name}</span>
                    </div>
                    {#if entry.bird.is_new}
                        <div class="new-badge">NEW</div>
                    {/if}
                    <div class="bird-right">
                        <div class="bird-thumb">
                            {#if birdThumbnails[entry.bird.scientific_name]}
                                <img src="{'data:image/jpeg;base64, ' + birdThumbnails[entry.bird.scientific_name]}" alt="{entry.bird.common_name}"/>
                            {:else}
                                <Fa icon={faImage}/>
                            {/if}
                        </div>
                        <div class="bird-stats">
                            <span class="bird-confidence">{fmtConfidence(entry.bird.confidence)}</span>
                            <span class="bird-count">{entry.count}</span>
                        </div>
                    </div>
                </div>
            {:else}
                <div class="no-birds">No Birds Detected Yet</div>
            {/each}
        </div>

        <div class="live-fab" role="button" tabindex="0" on:click={enterLiveMode} on:keydown={(event) => (event.key === 'Enter' || event.key === ' ') && enterLiveMode()}>
            <Fa icon={faCrow}/>
        </div>
    {/if}
</div>

<style>
    .bird-dash {
        position: relative;
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

    .live-fab {
        position: absolute;
        right: 18px;
        bottom: 18px;
        width: 54px;
        height: 54px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 26px;
        color: #0B1E10;
        background: #7CFF9A;
        box-shadow: 0 4px 14px rgba(0, 0, 0, 0.5);
        cursor: pointer;
        -webkit-tap-highlight-color: transparent;
        touch-action: manipulation;
        transition: transform 0.15s ease;
        z-index: 5;
    }
    .live-fab:active { transform: scale(0.92); }

    .live-content {
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
    .header-icon { font-size: 34px; display: flex; align-items: center; color: #7CFF9A; }
    .header-title { font-size: 26px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px; flex: 1; }
    .header-count { font-size: 36px; font-weight: 700; font-variant-numeric: tabular-nums; color: #fca503; }
    .history-btn {
        font-size: 26px;
        color: #8892A6;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 10px;
        margin: -10px;
        -webkit-tap-highlight-color: transparent;
        touch-action: manipulation;
    }

    .bird-list {
        display: flex;
        flex-direction: column;
        gap: 4px;
        flex: 1;
        min-height: 0;
        overflow-y: auto;
    }

    .bird-row {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 10px;
        padding: 10px 16px;
        border-radius: 10px;
        background: linear-gradient(145deg, rgba(34, 40, 56, 0.85), rgba(20, 24, 36, 0.85));
        border: 1px solid rgba(255, 255, 255, 0.06);
        box-shadow: 0 3px 10px rgba(0, 0, 0, 0.35), inset 0 1px 0 rgba(255, 255, 255, 0.04);
        cursor: pointer;
        -webkit-tap-highlight-color: transparent;
        touch-action: manipulation;
        transition: transform 0.15s ease;
    }
    .bird-row:active { transform: scale(0.985); }

    .bird-row.bird-detected {
        animation: bird-flash 1s ease-out;
    }

    @keyframes bird-flash {
        0% { background: rgba(94, 198, 255, 0.55); }
        100% { background: linear-gradient(145deg, rgba(34, 40, 56, 0.85), rgba(20, 24, 36, 0.85)); }
    }

    .bird-names {
        display: flex;
        flex-direction: column;
        min-width: 0;
    }
    .common-name {
        font-size: 24px;
        font-weight: 700;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    .scientific-name {
        font-size: 16px;
        font-style: italic;
        color: #8892A6;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }

    .common-name.new-bird {
        color: #39FF14;
    }

    .new-badge {
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 12px;
        font-weight: 800;
        letter-spacing: 0.5px;
        color: #0B1E10;
        background: #39FF14;
        border-radius: 999px;
        padding: 3px 12px;
        flex-shrink: 0;
        box-shadow: 0 0 6px rgba(57, 255, 20, 0.6);
    }

    .bird-right {
        display: flex;
        align-items: center;
        gap: 10px;
        flex-shrink: 0;
        margin-left: auto;
    }

    .bird-thumb {
        display: flex;
        align-items: center;
        justify-content: center;
        width: 44px;
        height: 44px;
        flex-shrink: 0;
        border-radius: 8px;
        overflow: hidden;
        background: rgba(255, 255, 255, 0.04);
        border: 1px solid rgba(255, 255, 255, 0.05);
        color: #8892A6;
        font-size: 18px;
    }

    .bird-thumb img {
        width: 100%;
        height: 100%;
        object-fit: cover;
        display: block;
    }

    .bird-stats {
        display: flex;
        flex-direction: column;
        align-items: flex-end;
        gap: 2px;
        flex-shrink: 0;
        min-width: 58px;
    }

    .bird-confidence {
        font-size: 14px;
        color: #8892A6;
        white-space: nowrap;
    }

    .bird-count {
        font-size: 28px;
        font-weight: 800;
        color: #5EC6FF;
        font-variant-numeric: tabular-nums;
        white-space: nowrap;
    }

    .no-birds {
        display: flex;
        align-items: center;
        justify-content: center;
        flex: 1;
        color: #8892A6;
        font-size: 20px;
        font-weight: 600;
    }

    @media (max-width: 400px) {
        .header-title { font-size: 18px; }
        .header-count { font-size: 22px; }
        .common-name { font-size: 18px; }
        .scientific-name { font-size: 13px; }
        .bird-count { font-size: 20px; }
        .bird-confidence { font-size: 11px; }
        .bird-stats { min-width: 44px; }
    }
</style>
