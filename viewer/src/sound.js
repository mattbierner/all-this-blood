/**
 * 
 */
export default class PulseSound {
    constructor() {
        this._ctx = new (window.AudioContext || window.webkitAudioContext)()

        const req = new XMLHttpRequest()
        req.open('GET', './resources/beat.wav', true)
        req.responseType = 'arraybuffer'
        req.onload = () => {
            this._ctx.decodeAudioData(req.response, buffer => {
                this._sound = buffer
            }, console.error)
        }
        req.send()
    }

    play() {
        if (!this._sound)
            return
        const source = this._ctx.createBufferSource()
        source.buffer = this._sound
        source.connect(this._ctx.destination)
        source.start(0)
    }
}