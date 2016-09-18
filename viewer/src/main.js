import Renderer from './renderer'
import {createSocket} from './socket'

const renderer = new Renderer(
    document.getElementById('canvas3d'),
    document.getElementById('main'))

const socket = createSocket((data) => {
    renderer.pulse(data)
})

const img = new Image()
img.crossOrigin = 'anonymous'
img.onload = () => {
    renderer.setImage(img)
    renderer.animate()
}
img.src = 'http://192.168.1.6:8080'
