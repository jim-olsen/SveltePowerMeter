<script>
    import Fa from "svelte-fa";
    import {faCrow, faArrowLeft, faClockRotateLeft} from "@fortawesome/free-solid-svg-icons";
    import {birdData} from "../../stores.svelte.js";
    import {currentView} from "../../states.svelte.js";

    let birds = [];

    $: birds = Object.values($birdData)
        .filter(entry => entry?.bird?.scientific_name)
        .sort((a, b) => b.count - a.count);

    function go(view) {
        return () => currentView.value = view;
    }

    function fmtConfidence(v) {
        return v === undefined || v === null ? '---' : (Number(v) * 100).toFixed(1) + '%';
    }
</script>

<div class="bird-dash">
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
            <div class="bird-row" role="button" tabindex="0"
                 on:click={go('bird_details_' + entry.bird.scientific_name)}
                 on:keydown={(event) => (event.key === 'Enter' || event.key === ' ') && go('bird_details_' + entry.bird.scientific_name)()}>
                <div class="bird-names">
                    <span class="common-name" class:new-bird={entry.bird.is_new}>{entry.bird.common_name}</span>
                    <span class="scientific-name">{entry.bird.scientific_name}</span>
                </div>
                {#if entry.bird.is_new}
                    <div class="new-badge">NEW</div>
                {/if}
                <div class="bird-stats">
                    <span class="bird-confidence">{fmtConfidence(entry.bird.confidence)}</span>
                    <span class="bird-count">{entry.count}</span>
                </div>
            </div>
        {:else}
            <div class="no-birds">No Birds Detected Yet</div>
        {/each}
    </div>
</div>

<style>
    .bird-dash {
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

    .bird-stats {
        display: flex;
        flex-direction: column;
        align-items: flex-end;
        gap: 2px;
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
    }
</style>
