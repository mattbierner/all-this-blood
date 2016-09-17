import Renderer from './renderer'

const canvas3d = document.getElementById('canvas3d')

const img = new Image()
img.crossOrigin = 'anonymous'
img.src = 'http://192.168.1.6:8080'
img.onload = () => {
    new Renderer(canvas3d, null, img)
}