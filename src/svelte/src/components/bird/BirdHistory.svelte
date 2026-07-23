<script>
    import Fa from "svelte-fa";
    import {faClockRotateLeft, faArrowLeft, faTrash, faImage} from "@fortawesome/free-solid-svg-icons";
    import {birdHistoryData, getBirdHistoryData} from "../../stores.svelte.js";
    import {currentView} from "../../states.svelte.js";

    let birds = [];
    let birdToDelete = null;
    let birdThumbnails = {};

    $: birds = $birdHistoryData;

    $: {
        for (const entry of birds) {
            fetchThumbnail(entry.scientific_name);
        }
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

    function go(view) {
        return () => currentView.value = view;
    }

    function fmtTime(v) {
        return v === undefined || v === null ? '---' : new Date(v).toLocaleString();
    }

    function fmtConfidence(v) {
        return v === undefined || v === null ? '---' : (Number(v) * 100).toFixed(1) + '%';
    }

    function confirmDelete(entry) {
        return (event) => {
            event.stopPropagation();
            birdToDelete = entry;
        };
    }

    function cancelDelete() {
        birdToDelete = null;
    }

    function performDelete() {
        if (!birdToDelete) {
            return;
        }
        fetch(`/birdHistory?scientificName=${encodeURIComponent(birdToDelete.scientific_name)}`, {
            method: 'DELETE'
        })
            .then(() => {
                birdToDelete = null;
                getBirdHistoryData();
            });
    }
</script>

<div class="bird-dash">
    <div class="dash-header" role="button" tabindex="0" on:click={go('birdDashboard')} on:keydown={(event) => (event.key === 'Enter' || event.key === ' ') && go('birdDashboard')()}>
        <div class="back-btn"><Fa icon={faArrowLeft}/></div>
        <div class="header-icon"><Fa icon={faClockRotateLeft}/></div>
        <div class="header-title">Bird History</div>
        <div class="header-count">{birds.length}</div>
    </div>

    <div class="bird-list">
        {#each birds as entry}
            <div class="bird-row" role="button" tabindex="0"
                 on:click={go('bird_details_' + entry.scientific_name)}
                 on:keydown={(event) => (event.key === 'Enter' || event.key === ' ') && go('bird_details_' + entry.scientific_name)()}>
                <div class="bird-names">
                    <span class="common-name">{entry.common_name}</span>
                    <span class="scientific-name">{entry.scientific_name}</span>
                </div>
                <div class="bird-right">
                    <div class="bird-thumb">
                        {#if birdThumbnails[entry.scientific_name]}
                            <img src="{'data:image/jpeg;base64, ' + birdThumbnails[entry.scientific_name]}" alt="{entry.common_name}"/>
                        {:else}
                            <Fa icon={faImage}/>
                        {/if}
                    </div>
                    <div class="bird-stats">
                        <span class="last-heard">{fmtTime(entry.last_heard)}</span>
                        <span class="bird-confidence">{fmtConfidence(entry.confidence)}</span>
                        <span class="bird-count">{entry.count}</span>
                    </div>
                    <div class="delete-btn" role="button" tabindex="0"
                         on:click={confirmDelete(entry)}
                         on:keydown={(event) => (event.key === 'Enter' || event.key === ' ') && confirmDelete(entry)(event)}>
                        <Fa icon={faTrash}/>
                    </div>
                </div>
            </div>
        {:else}
            <div class="no-birds">No Birds Recorded Yet</div>
        {/each}
    </div>

    {#if birdToDelete}
        <div class="modal-overlay" role="button" tabindex="0" on:click={cancelDelete} on:keydown={(event) => event.key === 'Escape' && cancelDelete()}>
            <div class="modal" role="dialog" on:click|stopPropagation on:keydown|stopPropagation>
                <div class="modal-title">Delete Bird History</div>
                <div class="modal-message">Delete all recorded entries for {birdToDelete.common_name}?</div>
                <div class="modal-actions">
                    <button class="modal-btn cancel-btn" on:click={cancelDelete}>Cancel</button>
                    <button class="modal-btn delete-confirm-btn" on:click={performDelete}>Yes, Delete</button>
                </div>
            </div>
        </div>
    {/if}
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
        flex: 1;
    }

    .bird-right {
        display: flex;
        align-items: center;
        gap: 6px;
        flex-shrink: 0;
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
        min-width: 70px;
    }

    .last-heard {
        font-size: 14px;
        color: #8892A6;
        white-space: nowrap;
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

    .delete-btn {
        font-size: 20px;
        color: #8892A6;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 10px;
        margin: -10px -10px -10px 0;
        flex-shrink: 0;
        -webkit-tap-highlight-color: transparent;
        touch-action: manipulation;
        transition: color 0.15s ease;
    }
    .delete-btn:hover, .delete-btn:active {
        color: #FF5C5C;
    }

    .modal-overlay {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.6);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 1000;
        cursor: default;
    }

    .modal {
        display: flex;
        flex-direction: column;
        gap: 14px;
        width: min(320px, 85vw);
        padding: 20px;
        border-radius: 12px;
        background: linear-gradient(145deg, rgba(34, 40, 56, 0.97), rgba(20, 24, 36, 0.97));
        border: 1px solid rgba(255, 255, 255, 0.08);
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.6);
        color: #e6eaf2;
    }

    .modal-title {
        font-size: 18px;
        font-weight: 700;
    }

    .modal-message {
        font-size: 14px;
        color: #c3c9d6;
    }

    .modal-actions {
        display: flex;
        justify-content: flex-end;
        gap: 10px;
    }

    .modal-btn {
        font-size: 14px;
        font-weight: 700;
        border: none;
        border-radius: 8px;
        padding: 8px 16px;
        cursor: pointer;
        -webkit-tap-highlight-color: transparent;
        touch-action: manipulation;
    }

    .cancel-btn {
        background: rgba(255, 255, 255, 0.08);
        color: #e6eaf2;
    }

    .delete-confirm-btn {
        background: #FF5C5C;
        color: #1a1a1a;
    }

    @media (max-width: 400px) {
        .header-title { font-size: 18px; }
        .header-count { font-size: 22px; }
        .common-name { font-size: 18px; }
        .scientific-name { font-size: 13px; }
        .bird-count { font-size: 20px; }
        .last-heard { font-size: 11px; }
        .bird-confidence { font-size: 11px; }
        .delete-btn { font-size: 16px; }
        .bird-stats { min-width: 56px; }
    }
</style>
