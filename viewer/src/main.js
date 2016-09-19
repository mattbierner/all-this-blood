import Renderer from './renderer'
import {createSocket} from './socket'
import {ip} from './config'
import PulseSound from './sound'

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
