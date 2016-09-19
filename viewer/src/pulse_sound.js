import audio_context from './audio_context'

/**
 * "Ah, I see you have the machine that goes 'ping!'"
 * 
 * Plays beep sound on heartbeat. 
 */
export default class PulseSound {
    constructor() {
        const req = new XMLHttpRequest()
        req.open('GET', './resources/beat.wav', true)
        req.responseType = 'arraybuffer'
        req.onload = () => 
            audio_context.then(ctx => {
                this._ctx = ctx
                this._ctx.decodeAudioData(req.response, buffer => {
                    this._sound = buffer
                }, console.error)
            })
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