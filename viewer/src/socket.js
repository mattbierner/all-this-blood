import {ip} from './config'

/**
 * 
 */
export const createSocket = (handler) => {
    const ws = new WebSocket(`ws://${ip}:5678/`)
    ws.onmessage = (event) => {
        handler(JSON.parse(event.data))
    }
    return ws
}
