/**
 * 
 */
export const createSocket = (handler) => {
    const ws = new WebSocket("ws://192.168.1.2:5678/")
    ws.onmessage = (event) => {
        handler(JSON.parse(event.data))
    }
    return ws
}
