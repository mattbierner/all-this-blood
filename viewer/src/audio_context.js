let r
let ctx

export default new Promise((resolve, reject) => {
    r = resolve
})

/**
 * For IOS, audio context can only be created inside of a touch event.
 */
export const init = () => {
    if (ctx)
        return ctx
        
    ctx = new (window.AudioContext || window.webkitAudioContext)()

    var oscillator = ctx.createOscillator()
    oscillator.frequency.value = 1
    oscillator.connect(ctx.destination)
    oscillator.start(0)
    oscillator.stop(0)
    r(ctx)
    return ctx
}