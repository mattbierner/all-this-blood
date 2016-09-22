import {ip, beatoffset} from './config'

/**
 * 
 */
export const createPulseClient = (handler) => {
    const ws = new WebSocket(`ws://${ip}:5678/`)
    ws.onmessage = (event) => {
        const data = JSON.parse(event.data)

        const now = Date.now()
        const expectedNextbeat = 1 / data.bpm * 60 * 1000
        const time = Math.max(expectedNextbeat - (now - data.time - beatoffset), 0)
        
        setTimeout(() => {
            handler(data)
        }, time)
    }
    return ws
}
