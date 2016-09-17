import THREE from 'three';

/**
 * 
 */
export default {
    uniforms: {
        map: { type: 't', value: new THREE.Texture() },

        progress: { value: 0.0 },
    },
    vertexShader: `
        varying vec2 vUv;
        
        void main() {
            vUv = uv;
            gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
        }
    `,
    fragmentShader: `
        uniform sampler2D map;
        uniform float progress;

        varying vec2 vUv;
        
        void main() {
            vec4 sum = texture2D(map, vUv);
            sum.x += progress;
            gl_FragColor = vec4(sum.xyz, 1.0);
        }
    `,
};