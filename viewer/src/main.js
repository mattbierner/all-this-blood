import Renderer from './renderer'
import {createSocket} from './socket'

const socket = createSocket((data) => {
    console.log(data)
})

const img = new Image()
img.crossOrigin = 'anonymous'
img.onload = () => {
    new Renderer(
        document.getElementById('canvas3d'),
        document.getElementById('main'),
        img)
}

img.src = 'http://192.168.1.6:8080'
