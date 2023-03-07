import { writable, get } from 'svelte/store';

export const powerGraphDuration = writable(2)

let lastBlueIrisAlert = {};

/**
 * Retrieve the graph data for values over time.  The powerGraphDuration writeable provides the number of days over
 * which to fetch the data.
 */
function getPowerGraphData() {
    fetch(`/graphData?days=${get(powerGraphDuration)}`, {
        headers: {
            "Accept": "application/json"
        }
    })
        .then(d => d.json())
        .then(d => {
            powerGraphData.set(d);
        });
}

/**
 * Subscribable that contains the latest graph data representing values over time, based on powerGraphDuration
 * subscribable.
 * @type {Writable<{}>}
 */
export const powerGraphData = writable({}, () => {
    let unsubscribe = powerGraphDuration.subscribe(getPowerGraphData)
    getPowerGraphData()
    let powerGraphInterval = setInterval(getPowerGraphData, 15000);
    return () => {
        unsubscribe();
        clearInterval(powerGraphInterval);
    };
});

/**
 * Retrieve the current live data values related to the power system.
 */
function getPowerCurrentData() {
    fetch("/currentData", {
        headers: {
            "Accept": "application/json"
        }
    })
        .then(d => d.json())
        .then(d => {
            powerCurrentData.set(d);
        });
}

/**
 * A subscribable that contains the latest live values for power related values
 * @type {Writable<{}>}
 */
export const powerCurrentData = writable( {}, () => {
    getPowerCurrentData();
    let powerCurrentInterval = setInterval(getPowerCurrentData, 5000);
    return () => {
        clearInterval(powerCurrentInterval);
    };
});

/**
 * Retrieve statistical data for power related values showing cumulative and average values
 */
function getPowerStatsData() {
    fetch("/statsData", {
        headers: {
            "Accept": "application/json"
        }
    })
        .then(d => d.json())
        .then(d => {
            powerStatsData.set(d);
        });
}

/**
 * A subscribable that contains the latest statistical values for power related data.
 * @type {Writable<{}>}
 */
export const powerStatsData = writable({}, () => {
    getPowerStatsData();
    let powerStatsInterval = setInterval(getPowerStatsData, 5000);
    return () => {
        clearInterval(powerStatsInterval);
    };
});

/**
 * Retrieve the last recorded alert from blue iris
 */
function getBlueIrisAlert() {
    fetch("/blueIrisAlert", {
        headers: {
            "Accept": "application/json"
        }
    })
        .then(d => d.json())
        .then(d => {
            if (d.hasOwnProperty("id") &&
                (!lastBlueIrisAlert.hasOwnProperty("id") || lastBlueIrisAlert.id !== d.id)) {
                    blueIrisAlert.set(d)
                    lastBlueIrisAlert = d;
                    console.log("Setting blue iris alert " + lastBlueIrisAlert.id + "!=" + d.id );
            }
        });
}

/**
 * A subscribable that contains the latest alert from blue iris
 * @type {Writeable<{}>}
 */
export const blueIrisAlert = writable({}, () => {
    getBlueIrisAlert();
    let blueIrisAlertInterval = setInterval(getBlueIrisAlert, 10000);
    return () => {
        clearInterval(blueIrisAlertInterval);
        lastBlueIrisAlert = {};
    }
})

/**
 * Returns live starlink status values as defined by the dishy component of starlink
 */
function getStarlinkStatus() {
    fetch("/starlink/status/", {
        headers: {
            "Accept": "application/json"
        }
    })
        .then(d => d.json())
        .then(d => {
            starlinkStatus.set(d);
        });
}

/**
 * A subscribable that contains the latest starlink status values as retrieved from the dishy component of starlink
 * @type {Writable<{}>}
 */
export const starlinkStatus = writable({}, () => {
    getStarlinkStatus();
    let statusInterval = setInterval(getStarlinkStatus, 500)
    return () => {
        clearInterval(statusInterval)
    }
})

/**
 * Retrieve historical values available from the dishy component of starlink
 */
function getStarlinkHistory() {
    fetch("/starlink/history/", {
        headers: {
            "Accept": "application/json"
        }
    })
        .then(d => d.json())
        .then(d => {
            starlinkHistory.set(d);
        });
}

/**
 * A subscribable that contains the latest historical data from the dishy component of starlink
 * @type {Writable<{}>}
 */
export const starlinkHistory = writable( {}, () => {
    getStarlinkHistory();
    let historyInterval = setInterval(getStarlinkHistory, 1000);
    return () => {
        clearInterval(historyInterval);
    }
})


