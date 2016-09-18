import THREE from 'three';

/**
 * Draws a red vignette on each beat.
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
        
        const float radius = 0.5;
        const float softness = 0.5;

        void main() {
            vec4 tex = texture2D(map, vUv);

            // vignette
            vec2 position = vUv - vec2(0.5);
            float len = length(position);
            float vignette = 1.0 - smoothstep(radius, radius - softness, len);
            tex.rgb = mix(tex.rgb, vec3(1, 0, 0), progress * vignette);

            gl_FragColor = vec4(tex.rgb, 1.0);
        }
    `,
};