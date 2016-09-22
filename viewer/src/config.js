/**
 * Hostname of Raspberry Pi streaming server.
 */
export const ip =  window.location.href.indexOf('eth') >= 0 ? '192.168.1.2' : '172.20.10.3'

/**
 * Offset in ms of when heartbeat occured and when the pi detected it
 */
export const beatoffset = -75