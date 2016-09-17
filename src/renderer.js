import THREE from 'three'
import pulseShader from './shaders/pulse_shader'

const canvas2d = document.getElementById('canvas2d')
const ctx = canvas2d.getContext('2d')
const map = new THREE.Texture(canvas2d)

const material = new THREE.ShaderMaterial(pulseShader)
material.uniforms.map.value = map
material.uniforms.map.needsUpdate = true

export default class Renderer {
    constructor(canvas, container, stream) {
        this._stream = stream
        this._clock = new THREE.Clock()
        this._last = 0;

        setInterval(() => {
            this._last = this._clock.getElapsedTime()
        }, 1000)

        this._initRenderer(canvas)
        this._init()
        this._animate()
    }

    _initRenderer(canvas) {
        this._renderer = new THREE.WebGLRenderer({ canvas: canvas })
        this._renderer.setClearColor(0xffff00)
    }

    _init(){
        this._scene = new THREE.Scene()

        this._camera = new THREE.OrthographicCamera(-1, 1, 1, -1, 1, 1000)
        this._camera.position.set(0, 0, 5)
        this._scene.add(this._camera)

        const geometry = new THREE.PlaneGeometry(1, 2);
        const mesh = new THREE.Mesh(geometry, material)
        mesh.position.setX(-0.5)
        this._scene.add(mesh)
    }

    _animate() {
        const start = this._clock.getElapsedTime()
        const delta = this._clock.getDelta()

        requestAnimationFrame(() => this._animate())

        // Update image
        ctx.drawImage(this._stream, 0, 0, canvas2d.clientWidth, canvas2d.clientHeight)
        map.needsUpdate = true
        material.needsUpdate = true

        const val = (0.5 - (start - this._last)) / 0.5;
        const progress = Math.min(Math.max(val, 0), 1)
        material.uniforms.progress.value = progress
        material.uniforms.progress.needsUpdate = true


        this._render()
   }

    _render() {
        this._renderer.render(this._scene, this._camera)
    }
}
