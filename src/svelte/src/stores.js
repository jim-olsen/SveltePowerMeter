import {writable, get} from 'svelte/store';
import {io} from 'socket.io-client'

export const powerGraphDuration = writable(2)
export const weatherGraphDuration = writable(1)

let lastBlueIrisAlert = {};
let lastADSBData = {};
let websocket = io();

export const currentView = writable('dashboard');

/**
 * Retrieve the graph data for battery voltage over time.  The powerGraphDuration writeable provides the number of
 * days over which to fetch the data.
 */
function getBatteryVoltageGraphData() {
    fetch(`/graphData?days=${get(powerGraphDuration)}&dataField=battery_voltage&dataField=target_regulation_voltage`, {
        headers: {
            "Accept": "application/json"
        }
    })
        .then(d => d.json())
        .then(d => {
            batteryVoltageGraphData.set(d);
        });
}

/**
 * Subscribable that contains the latest graph data representing battery voltage over time, based on powerGraphDuration
 * subscribable.
 * @type {Writable<{}>}
 */
export const batteryVoltageGraphData = writable({}, () => {
    let unsubscribe = powerGraphDuration.subscribe(getBatteryVoltageGraphData)
    getBatteryVoltageGraphData();
    let batteryVoltageGraphInterval = setInterval(getBatteryVoltageGraphData, 15000);
    return () => {
        unsubscribe();
        clearInterval(batteryVoltageGraphInterval);
    };
});

/**
 * Retrieve the graph data for battery wattage over time.  The powerGraphDuration writeable provides the number of
 * days over which to fetch the data.
 */
function getBatteryWattsGraphData() {
    fetch(`/graphData?days=${get(powerGraphDuration)}&dataField=battery_watts`, {
        headers: {
            "Accept": "application/json"
        }
    })
        .then(d => d.json())
        .then(d => {
            batteryWattsGraphData.set(d);
        });
}

/**
 * Subscribable that contains the latest graph data representing battery watts over time, based on powerGraphDuration
 * subscribable.
 * @type {Writable<{}>}
 */
export const batteryWattsGraphData = writable({}, () => {
    let unsubscribe = powerGraphDuration.subscribe(getBatteryWattsGraphData)
    getBatteryWattsGraphData();
    let batteryWattsGraphInterval = setInterval(getBatteryWattsGraphData, 15000);
    return () => {
        unsubscribe();
        clearInterval(batteryWattsGraphInterval);
    };
});

/**
 * Retrieve the graph data for load over time.  The powerGraphDuration writeable provides the number of
 * days over which to fetch the data.
 */
function getLoadWattsGraphData() {
    fetch(`/graphData?days=${get(powerGraphDuration)}&dataField=load_watts`, {
        headers: {
            "Accept": "application/json"
        }
    })
        .then(d => d.json())
        .then(d => {
            loadWattsGraphData.set(d);
        });
}

/**
 * Subscribable that contains the latest graph data representing load over time, based on powerGraphDuration
 * subscribable.
 * @type {Writable<{}>}
 */
export const loadWattsGraphData = writable({}, () => {
    let unsubscribe = powerGraphDuration.subscribe(getLoadWattsGraphData)
    getLoadWattsGraphData();
    let loadWattsGraphInterval = setInterval(getLoadWattsGraphData, 15000);
    return () => {
        unsubscribe();
        clearInterval(loadWattsGraphInterval);
    };
});

/**
 * Retrieve the graph data for solar watts over time.  The powerGraphDuration writeable provides the number of
 * days over which to fetch the data.
 */
function getSolarWattsGraphData() {
    fetch(`/graphData?days=${get(powerGraphDuration)}&dataField=solar_watts`, {
        headers: {
            "Accept": "application/json"
        }
    })
        .then(d => d.json())
        .then(d => {
            solarWattsGraphData.set(d);
        });
}

/**
 * Subscribable that contains the latest graph data representing battery voltage over time, based on powerGraphDuration
 * subscribable.
 * @type {Writable<{}>}
 */
export const solarWattsGraphData = writable({}, () => {
    let unsubscribe = powerGraphDuration.subscribe(getSolarWattsGraphData)
    getSolarWattsGraphData();
    let solarWattsGraphInterval = setInterval(getSolarWattsGraphData, 15000);
    return () => {
        unsubscribe();
        clearInterval(solarWattsGraphInterval);
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
export const powerCurrentData = writable({}, () => {
    getPowerCurrentData();
    websocket.on('current_data', (currentData) => {
       powerCurrentData.set(currentData)
    });
    return () => {
        websocket.removeAllListeners('current_data');
    };
});

/**
 * Retrieve the current live data values related to the batteries.
 */
function getBatteryCurrentData() {
    fetch("/batteryData", {
        headers: {
            "Accept": "application/json"
        }
    })
        .then(d => d.json())
        .then(d => {
            batteryCurrentData.set(d.sort((a, b) => a.name.localeCompare(b.name)));
        });
}

/**
 * A subscribable that contains the latest live values for battery related values
 * @type {Writable<{}>}
 */
export const batteryCurrentData = writable([], () => {
    getBatteryCurrentData();
    websocket.on('battery_data', (data) => batteryCurrentData.set(data));
    return () => {
        websocket.removeAllListeners('battery_data');
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
    websocket.on('stats_data', (data) => powerStatsData.set(data));
    return () => {
        websocket.removeAllListeners('stats_data');
    };
});

/**
 * Retrieve the last recorded alert from blue iris
 */
function getBlueIrisAlert() {
    fetch("/blueIrisAlert?noImage=True", {
        headers: {
            "Accept": "application/json"
        }
    })
        .then(d => d.json())
        .then(d => {
            if (d.hasOwnProperty("id") &&
                (!lastBlueIrisAlert.hasOwnProperty("id") || lastBlueIrisAlert.id !== d.id)) {
                fetch("/blueIrisAlert", {
                    headers: {
                        "Accept": "application/json"
                    }
                })
                    .then(d => d.json())
                    .then(d => {
                        blueIrisAlert.set(d)
                        lastBlueIrisAlert = d;
                    });
            } else {
                blueIrisAlert.set(lastBlueIrisAlert)
            }
        });
}

/**
 * A subscribable that contains the latest alert from blue iris
 * @type {Writeable<{}>}
 */
export const blueIrisAlert = writable({}, () => {
    websocket.on('blueiris_alert', (data) => blueIrisAlert.set(data));
    return () => {
        websocket.removeAllListeners('blueiris_alert');
    }
})


/**
 * Retrieve the last recorded adsb packet
 */
function getADSBData() {
    fetch("/adsbData?noImage=True", {
        headers: {
            "Accept": "application/json"
        }
    })
        .then(d => d.json())
        .then(d => {
            if (d.hasOwnProperty("id") &&
                (!lastADSBData.hasOwnProperty("id") || lastADSBData.id !== d.id)) {
                fetch("/adsbData", {
                    headers: {
                        "Accept": "application/json"
                    }
                })
                    .then(d => d.json())
                    .then(d => {
                        adsbData.set(d)
                        lastADSBData = d;
                    });
            } else {
                adsbData.set(lastADSBData)
            }
        });
}

/**
 * A subscribable that contains the latest adsb data
 * @type {Writeable<{}>}
 */
export const adsbData = writable({}, () => {
    websocket.on('adsb_data', (data) => adsbData.set(data));
    return () => {
        websocket.removeAllListeners('adsb_data');
    }
})

/**
 * Returns live starlink status values as defined by the dishy component of starlink
 */
function getStarlinkStatus() {
    fetch("/starlink/status", {
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
    websocket.on('starlink_status', (data) => starlinkStatus.set(data));
    return () => {
        websocket.removeAllListeners('starlink_status');
    }
})

/**
 * Retrieve historical values available from the dishy component of starlink
 */
function getStarlinkHistory() {
    fetch("/starlink/history?skipGraphs=True", {
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
export const starlinkHistory = writable({}, () => {
    getStarlinkHistory();
    websocket.on('starlink_history', (data) => starlinkHistory.set(data));
    return () => {
        websocket.removeAllListeners('starlink_history');
    }
})

/**
 * Retrieve historical values available from the dishy component of starlink
 */
function getStarlinkGraphHistory() {
    fetch("/starlink/history?skipGraphs=False", {
        headers: {
            "Accept": "application/json"
        }
    })
        .then(d => d.json())
        .then(d => {
            starlinkGraphHistory.set(d);
        });
}

/**
 * A subscribable that contains the latest historical data from the dishy component of starlink
 * @type {Writable<{}>}
 */
export const starlinkGraphHistory = writable({}, () => {
    getStarlinkGraphHistory();
    let historyInterval = setInterval(getStarlinkGraphHistory, 10000);
    return () => {
        clearInterval(historyInterval);
    }
})

/**
 * Retrieve the current weather data
 */
function getWeatherData() {
    fetch("/weatherData", {
        headers: {
            "Accept": "application/json"
        }
    })
        .then(d => d.json())
        .then(d => {
            weatherData.set(d);
        });
}

/**
 * A subscribable that contains the latest weather data
 * @type {Writable<{}>}
 */
export const weatherData = writable({}, () => {
    getWeatherData();
    websocket.on('weather_data', (data) => {
       weatherData.set(data);
    });
    return () => {
        websocket.removeAllListeners('weather_data');
    }
})

/**
 * Retrieve the current temperature graph data
 */
function getTemperatureGraphData() {
    fetch(`/graphWxData?days=${get(weatherGraphDuration)}&dataField=outTemp_F&dataField=inTemp_F&dataField=windchill_F`, {
        headers: {
            "Accept": "application/json"
        }
    })
        .then(d => d.json())
        .then(d => {
            temperatureGraphData.set(d);
        });
}

/**
 * A subscribable that contains the latest temperature graph data
 * @type {Writable<{}>}
 */
export const temperatureGraphData = writable({}, () => {
    let unsubscribe = weatherGraphDuration.subscribe(getTemperatureGraphData)
    getTemperatureGraphData()
    let temperatureGraphInterval = setInterval(getTemperatureGraphData, 15000);
    return () => {
        unsubscribe();
        clearInterval(temperatureGraphInterval);
    }
})

/**
 * Retrieve the current wind graph data
 */
function getWindGraphData() {
    fetch(`/graphWxData?days=${get(weatherGraphDuration)}&dataField=windSpeed_mph&dataField=wind_average`, {
        headers: {
            "Accept": "application/json"
        }
    })
        .then(d => d.json())
        .then(d => {
            windGraphData.set(d);
        });
}

/**
 * A subscribable that contains the latest wind graph data
 * @type {Writable<{}>}
 */
export const windGraphData = writable({}, () => {
    let unsubscribe = weatherGraphDuration.subscribe(getWindGraphData)
    getWindGraphData()
    let windGraphInterval = setInterval(getWindGraphData, 15000);
    return () => {
        unsubscribe();
        clearInterval(windGraphInterval);
    }
});

/**
 * Retrieve the current pressure graph data
 */
function getPressureGraphData() {
    fetch(`/graphWxData?days=${get(weatherGraphDuration)}&dataField=pressure_inHg`, {
        headers: {
            "Accept": "application/json"
        }
    })
        .then(d => d.json())
        .then(d => {
            pressureGraphData.set(d);
        });
}

/**
 * A subscribable that contains the latest pressure graph data
 * @type {Writable<{}>}
 */
export const pressureGraphData = writable({}, () => {
    let unsubscribe = weatherGraphDuration.subscribe(getPressureGraphData)
    getPressureGraphData()
    let pressureGraphInterval = setInterval(getPressureGraphData, 15000);
    return () => {
        unsubscribe();
        clearInterval(pressureGraphInterval);
    }
})

/**
 * Retrieve the current pressure graph data
 */
function getHumidityGraphData() {
    fetch(`/graphWxData?days=${get(weatherGraphDuration)}&dataField=outHumidity`, {
        headers: {
            "Accept": "application/json"
        }
    })
        .then(d => d.json())
        .then(d => {
            humidityGraphData.set(d);
        });
}

/**
 * A subscribable that contains the latest pressure graph data
 * @type {Writable<{}>}
 */
export const humidityGraphData = writable({}, () => {
    let unsubscribe = weatherGraphDuration.subscribe(getHumidityGraphData)
    getHumidityGraphData()
    let humidityGraphInterval = setInterval(getHumidityGraphData, 15000);
    return () => {
        unsubscribe();
        clearInterval(humidityGraphInterval);
    }
})

/**
 * Retrieve the current daily min/max weather data
 */
function getWeatherDailyMinMax() {
    fetch("/weatherDailyMinMax", {
        headers: {
            "Accept": "application/json"
        }
    })
        .then(d => d.json())
        .then(d => {
            weatherDailyMinMax.set(d);
        });
}

/**
 * A subscribable that contains the latest weather data
 * @type {Writable<{}>}
 */
export const weatherDailyMinMax = writable({}, () => {
    getWeatherDailyMinMax()
    let weatherMinMaxInterval = setInterval(getWeatherDailyMinMax, 5000);
    return () => {
        clearInterval(weatherMinMaxInterval);
    }
})

/**
 * Retrieve the graph data for battery voltages in the bank over time.  The powerGraphDuration writeable provides the
 * number of days over which to fetch the data.
 */
function getBatteryBankVoltageGraphData() {
    fetch(`/graphBatteryData?days=${get(powerGraphDuration)}&dataField=voltage&dataField=name`, {
        headers: {
            "Accept": "application/json"
        }
    })
        .then(d => d.json())
        .then(d => {
            batteryBankVoltageGraphData.set(d);
        });
}

/**
 * Subscribable that contains the latest graph data representing battery bank voltages over time, based on
 * powerGraphDuration subscribable.
 * @type {Writable<{}>}
 */
export const batteryBankVoltageGraphData = writable({}, () => {
    let unsubscribe = powerGraphDuration.subscribe(getBatteryBankVoltageGraphData)
    getBatteryBankVoltageGraphData();
    let batteryBankVoltageGraphInterval = setInterval(getBatteryBankVoltageGraphData, 30000);
    return () => {
        unsubscribe();
        clearInterval(batteryBankVoltageGraphInterval);
    };
});

/**
 * Retrieve the graph data for battery voltages in the bank over time.  The powerGraphDuration writeable provides the
 * number of days over which to fetch the data.
 */
function getBatteryBankCellVoltageGraphData() {
    fetch(`/graphBatteryData?days=${get(powerGraphDuration)}&dataField=cell_voltage_one&dataField=cell_voltage_two&dataField=cell_voltage_three&dataField=cell_voltage_four&dataField=name`, {
        headers: {
            "Accept": "application/json"
        }
    })
        .then(d => d.json())
        .then(d => {
            batteryBankCellVoltageGraphData.set(d);
        });
}

/**
 * Subscribable that contains the latest graph data representing battery bank cell voltages over time, based on
 * powerGraphDuration subscribable.
 * @type {Writable<{}>}
 */
export const batteryBankCellVoltageGraphData = writable({}, () => {
    let unsubscribe = powerGraphDuration.subscribe(getBatteryBankCellVoltageGraphData)
    getBatteryBankCellVoltageGraphData();
    let batteryBankCellVoltageGraphInterval = setInterval(getBatteryBankCellVoltageGraphData, 30000);
    return () => {
        unsubscribe();
        clearInterval(batteryBankCellVoltageGraphInterval);
    };
});

/**
 * Retrieve the graph data for battery temperatures in the bank over time.  The powerGraphDuration writeable provides the
 * number of days over which to fetch the data.
 */
function getBatteryBankTemperatureGraphData() {
    fetch(`/graphBatteryData?days=${get(powerGraphDuration)}&dataField=battery_temp_two&dataField=name`, {
        headers: {
            "Accept": "application/json"
        }
    })
        .then(d => d.json())
        .then(d => {
            batteryBankTemperatureGraphData.set(d);
        });
}

/**
 * Subscribable that contains the latest graph data representing battery bank temperature over time, based on
 * powerGraphDuration subscribable.
 * @type {Writable<{}>}
 */
export const batteryBankTemperatureGraphData = writable({}, () => {
    let unsubscribe = powerGraphDuration.subscribe(getBatteryBankTemperatureGraphData)
    getBatteryBankTemperatureGraphData();
    let batteryBankVoltageGraphInterval = setInterval(getBatteryBankTemperatureGraphData, 30000);
    return () => {
        unsubscribe();
        clearInterval(batteryBankVoltageGraphInterval);
    };
});

/**
 * Retrieve the current lighthing data
 */
function getLightningData() {
    fetch("/lightningData", {
        headers: {
            "Accept": "application/json"
        }
    })
        .then(d => d.json())
        .then(d => {
            lightningData.set(d);
        });
}

/**
 * A subscribable that contains the latest lightning data
 * @type {Writable<{}>}
 */
export const lightningData = writable({}, () => {
    getLightningData()
    websocket.on('lightning_data', (data) => getLightningData());
    return () => {
        websocket.removeAllListeners('lightning_data');
    }
})
