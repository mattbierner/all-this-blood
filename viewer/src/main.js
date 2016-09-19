import Renderer from './renderer'
import * as audioCtx from './audio_context'
import {createSocket} from './socket'
import {ip} from './config'
import PulseSound from './sound'

const onIos = () =>
    /iPad|iPhone|iPod/.test(navigator.userAgent) && !window.MSStream

// The audio context must be created inside of a touch event on IOS
if (onIos) {
    document.body.addEventListener('touchstart', () => audio_context.init(), false);
} else {
    audio_context.init()
}

const renderer = new Renderer(
    document.getElementById('canvas3d'),
    document.getElementById('main'))

const sound = new PulseSound()

const socket = createSocket((data) => {
    renderer.pulse(data)
    sound.play()
})

const img = new Image()
img.crossOrigin = 'anonymous'
img.onload = () => {
    renderer.setImage(img)
    renderer.animate()
}
img.src = `http://${ip}:8080/?action=stream_0`
