/**
 * Three.js Background Scenes
 * Handles 3D animations for Landing and Auth pages
 */

// Global variables
let scene, camera, renderer;
let particles, geometry, material;
let shapes = [];
let mouseX = 0, mouseY = 0;
let windowHalfX = window.innerWidth / 2;
let windowHalfY = window.innerHeight / 2;

// Event listeners for interactivity
document.addEventListener('mousemove', onDocumentMouseMove, false);
window.addEventListener('resize', onWindowResize, false);

function onDocumentMouseMove(event) {
    mouseX = (event.clientX - windowHalfX) / 2;
    mouseY = (event.clientY - windowHalfY) / 2;
}

function onWindowResize() {
    windowHalfX = window.innerWidth / 2;
    windowHalfY = window.innerHeight / 2;

    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
}

/**
 * Initialize Landing Page Scene - Particle Network
 */
function initLandingScene() {
    const container = document.getElementById('canvas-container');
    if (!container) return;

    // SCENE & CAMERA
    scene = new THREE.Scene();
    scene.fog = new THREE.FogExp2(0x0f172a, 0.002); // Matches dark-bg color

    camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 1, 2000);
    camera.position.z = 1000;

    // RENDERER
    renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true });
    renderer.setPixelRatio(window.devicePixelRatio);
    renderer.setSize(window.innerWidth, window.innerHeight);
    container.appendChild(renderer.domElement);

    // PARTICLES
    geometry = new THREE.BufferGeometry();
    const particleCount = 1000;
    const vertices = [];

    for (let i = 0; i < particleCount; i++) {
        const x = Math.random() * 2000 - 1000;
        const y = Math.random() * 2000 - 1000;
        const z = Math.random() * 2000 - 1000;
        vertices.push(x, y, z);
    }

    geometry.setAttribute('position', new THREE.Float32BufferAttribute(vertices, 3));

    material = new THREE.PointsMaterial({
        color: 0x3b82f6, // Primary blue
        size: 3,
        transparent: true,
        opacity: 0.8
    });

    particles = new THREE.Points(geometry, material);
    scene.add(particles);

    // Add some connecting lines for "network" effect
    // Note: LineSegments is expensive with many points, keeping it simple for performance

    animateLanding();
}

function animateLanding() {
    requestAnimationFrame(animateLanding);

    camera.position.x += (mouseX - camera.position.x) * 0.05;
    camera.position.y += (-mouseY - camera.position.y) * 0.05;
    camera.lookAt(scene.position);

    particles.rotation.x += 0.0005;
    particles.rotation.y += 0.001;

    renderer.render(scene, camera);
}

/**
 * Initialize Auth Page Scene - Geometric Shapes
 */
function initAuthScene() {
    const container = document.getElementById('canvas-container');
    if (!container) return;

    // SCENE & CAMERA
    scene = new THREE.Scene();
    camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
    camera.position.z = 30;

    // RENDERER
    renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true });
    renderer.setSize(window.innerWidth, window.innerHeight);
    container.appendChild(renderer.domElement);

    // LIGHTING
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.5);
    scene.add(ambientLight);

    const pointLight = new THREE.PointLight(0x3b82f6, 1);
    pointLight.position.set(25, 50, 25);
    scene.add(pointLight);

    const pointLight2 = new THREE.PointLight(0x10b981, 1);
    pointLight2.position.set(-25, -50, 25);
    scene.add(pointLight2);

    // SHAPES
    // Icosahedron
    const geometry1 = new THREE.IcosahedronGeometry(10, 0);
    const material1 = new THREE.MeshPhongMaterial({
        color: 0x3b82f6,
        shininess: 100,
        wireframe: true,
        transparent: true,
        opacity: 0.3
    });
    const shape1 = new THREE.Mesh(geometry1, material1);
    shape1.position.set(-30, 10, -20);
    scene.add(shape1);
    shapes.push(shape1);

    // TorusKnot
    const geometry2 = new THREE.TorusKnotGeometry(8, 2, 100, 16);
    const material2 = new THREE.MeshPhongMaterial({
        color: 0x10b981,
        shininess: 100,
        wireframe: true,
        transparent: true,
        opacity: 0.2
    });
    const shape2 = new THREE.Mesh(geometry2, material2);
    shape2.position.set(30, -10, -30);
    scene.add(shape2);
    shapes.push(shape2);

    // Octahedron
    const geometry3 = new THREE.OctahedronGeometry(6);
    const material3 = new THREE.MeshPhongMaterial({
        color: 0x8b5cf6, // Violet
        shininess: 100,
        wireframe: false,
        flatShading: true,
        transparent: true,
        opacity: 0.6
    });
    const shape3 = new THREE.Mesh(geometry3, material3);
    shape3.position.set(0, 0, -50);
    scene.add(shape3);
    shapes.push(shape3);

    animateAuth();
}

function animateAuth() {
    requestAnimationFrame(animateAuth);

    // Rotate shapes
    shapes.forEach((shape, index) => {
        shape.rotation.x += 0.003 * (index + 1);
        shape.rotation.y += 0.003 * (index + 1);
    });

    // Subtle camera movement
    camera.position.x += (mouseX * 0.01 - camera.position.x) * 0.05;
    camera.position.y += (-mouseY * 0.01 - camera.position.y) * 0.05;
    camera.lookAt(scene.position);

    renderer.render(scene, camera);
}
