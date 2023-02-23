import { writable } from 'svelte/store';

export const powerGraphData = writable({})
export const powerCurrentData = writable( {})
export const powerStatsData = writable({})
export const powerGraphDuration = writable(4)
export const starlinkStatus = writable({})
export const starlinkHistory = writable( {})
