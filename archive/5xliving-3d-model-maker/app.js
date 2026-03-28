/**
 * 5XLiving Universal 3D Model Maker (FIXED + UPGRADED)
 * - Working upload + AI detection (TensorFlow.js MobileNet)
 * - Humanoid preset
 * - Universal generators (car, house, tree, robot)
 * - Stable render loop (no disappearing models)
 */

import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { GLTFExporter } from 'three/addons/exporters/GLTFExporter.js';

// ===================================
// MODEL PRESETS
// ===================================

const MODEL_PRESETS = {
    dog: { bodySize: 1, bodyLength: 1, headSize: 1, snoutLength: 0.5, earSize: 1, legLength: 1, tailLength: 1.5, eyeSize: 1 },
    cat: { bodySize: 0.9, bodyLength: 0.9, headSize: 0.95, snoutLength: 0.2, earSize: 1.2, legLength: 0.8, tailLength: 2, eyeSize: 1.2 },
    fox: { bodySize: 0.85, bodyLength: 1.1, headSize: 0.9, snoutLength: 0.7, earSize: 1.5, legLength: 0.9, tailLength: 2.5, eyeSize: 1 },
    bird: { bodySize: 0.7, bodyLength: 0.6, headSize: 0.6, snoutLength: 0.8, earSize: 1.8, legLength: 0.6, tailLength: 1.2, eyeSize: 1.3 },
    fish: { bodySize: 0.8, bodyLength: 1.3, headSize: 0.8, snoutLength: 0.3, earSize: 1.5, legLength: 0.3, tailLength: 1.8, eyeSize: 1.1 },
    rabbit: { bodySize: 0.95, bodyLength: 0.8, headSize: 1.1, snoutLength: 0.3, earSize: 2, legLength: 0.7, tailLength: 0.5, eyeSize: 1.2 },
    human: { bodySize: 0.7, bodyLength: 1.2, headSize: 0.8, snoutLength: 0.1, earSize: 0.3, legLength: 1.5, tailLength: 0, eyeSize: 0.6 },
    car: { bodySize: 1.2, bodyLength: 1.5, headSize: 0.7, snoutLength: 0.5, earSize: 0.8, legLength: 0.4, tailLength: 0.8, eyeSize: 0.6 },
    house: { bodySize: 1.3, bodyLength: 1.2, headSize: 1.2, snoutLength: 0.8, earSize: 0.5, legLength: 1.2, tailLength: 0.5, eyeSize: 0.8 },
    tree: { bodySize: 0.6, bodyLength: 0.6, headSize: 1.5, snoutLength: 0, earSize: 0.5, legLength: 1.5, tailLength: 0.5, eyeSize: 0.5 },
    robot: { bodySize: 1, bodyLength: 0.8, headSize: 0.9, snoutLength: 0.4, earSize: 0.8, legLength: 1.2, tailLength: 0.6, eyeSize: 1 },
    custom: { bodySize: 1, bodyLength: 1, headSize: 1, snoutLength: 0.5, earSize: 1, legLength: 1, tailLength: 1, eyeSize: 1 }
};

// ===================================
// AI DETECTION (TensorFlow.js MobileNet)
// ===================================

let mobilenetModel = null;
let isLoadingModel = false;

async function loadMobileNet() {
    if (mobilenetModel) return mobilenetModel;
    if (isLoadingModel) {
        // Wait for existing load
        while (isLoadingModel) {
            await new Promise(resolve => setTimeout(resolve, 100));
        }
        return mobilenetModel;
    }
    
    isLoadingModel = true;
    addLog('Loading AI model (MobileNet)...', 'info');
    
    try {
        if (typeof tf === 'undefined' || typeof mobilenet === 'undefined') {
            throw new Error('TensorFlow.js or MobileNet not loaded');
        }
        mobilenetModel = await mobilenet.load();
        addLog('AI model loaded successfully!', 'success');
        isLoadingModel = false;
        return mobilenetModel;
    } catch (error) {
        addLog('AI model failed to load: ' + error.message, 'warning');
        console.error(error);
        isLoadingModel = false;
        return null;
    }
}

async function detectWithMobileNet(imgElement) {
    try {
        const model = await loadMobileNet();
        if (!model) {
            return fallbackDetection();
        }
        
        const predictions = await model.classify(imgElement);
        addLog(`AI detected: ${predictions[0].className} (${Math.round(predictions[0].probability * 100)}%)`, 'success');
        
        // Map MobileNet classes to our presets
        const topResult = predictions[0].className.toLowerCase();
        const detectedType = mapMobileNetToPreset(topResult);
        
        return {
            detectedType: detectedType,
            confidence: predictions[0].probability,
            description: `AI detected: ${predictions[0].className}`,
            rawPredictions: predictions
        };
    } catch (error) {
        addLog('AI detection failed, using fallback', 'warning');
        console.error(error);
        return fallbackDetection();
    }
}

function mapMobileNetToPreset(className) {
    const lower = className.toLowerCase();
    
    // Dog family
    if (lower.includes('dog') || lower.includes('canine') || lower.includes('wolf') || 
        lower.includes('labrador') || lower.includes('shepherd') || lower.includes('poodle') ||
        lower.includes('retriever') || lower.includes('beagle')) {
        return 'dog';
    }
    
    // Cat family
    if (lower.includes('cat') || lower.includes('feline') || lower.includes('kitten') ||
        lower.includes('tabby') || lower.includes('persian')) {
        return 'cat';
    }
    
    // Fox
    if (lower.includes('fox')) {
        return 'fox';
    }
    
    // Bird
    if (lower.includes('bird') || lower.includes('eagle') || lower.includes('robin') ||
        lower.includes('parrot') || lower.includes('owl') || lower.includes('chicken') ||
        lower.includes('duck') || lower.includes('goose')) {
        return 'bird';
    }
    
    // Fish
    if (lower.includes('fish') || lower.includes('goldfish') || lower.includes('shark')) {
        return 'fish';
    }
    
    // Rabbit
    if (lower.includes('rabbit') || lower.includes('hare') || lower.includes('bunny')) {
        return 'rabbit';
    }
    
    // Human/Person
    if (lower.includes('person') || lower.includes('human') || lower.includes('man') ||
        lower.includes('woman') || lower.includes('boy') || lower.includes('girl') ||
        lower.includes('people')) {
        return 'human';
    }
    
    // Car/Vehicle
    if (lower.includes('car') || lower.includes('vehicle') || lower.includes('truck') ||
        lower.includes('van') || lower.includes('automobile') || lower.includes('sedan')) {
        return 'car';
    }
    
    // House/Building
    if (lower.includes('house') || lower.includes('building') || lower.includes('home') ||
        lower.includes('cottage') || lower.includes('mansion')) {
        return 'house';
    }
    
    // Tree/Plant
    if (lower.includes('tree') || lower.includes('plant') || lower.includes('oak') ||
        lower.includes('pine') || lower.includes('palm')) {
        return 'tree';
    }
    
    // Robot
    if (lower.includes('robot') || lower.includes('android')) {
        return 'robot';
    }
    
    return 'custom';
}

function fallbackDetection() {
    return {
        detectedType: 'custom',
        confidence: 0.5,
        description: "AI unavailable. Please select a preset manually.",
        rawPredictions: []
    };
}

// ===================================
// APP STATE
// ===================================

const APP_STATE = {
    currentModelType: 'dog',
    renderStyle: 'toonSmooth', // 'lowPoly', 'toonSmooth', 'clay'
    parameters: {
        bodySize: 1,
        bodyLength: 1,
        headSize: 1,
        snoutLength: 0.5,
        earSize: 1,
        legLength: 1,
        tailLength: 1.5,
        eyeSize: 1,
        bodyColor: '#8B7355',
        accentColor: '#5C4B3A',
        eyeColor: '#2C1810',
    },
    tier: 'free',
    exportsThisSession: 0,
    maxFreeExports: 1,
    exportLocked: false,
    lastDetectedImage: null,
};

// ===================================
// THREE.JS SCENE SETUP (STABLE)
// ===================================

let scene, camera, renderer, controls;
let modelGroup;
let gridHelper, axisHelper, groundPlane;
let animationFrameId = null;

function initScene() {
    try {
        // Scene
        scene = new THREE.Scene();
        scene.background = new THREE.Color(0x0a0a0a);

        // Canvas
        const canvas = document.getElementById('canvas3d');
        if (!canvas) {
            throw new Error('Canvas element not found');
        }

        // Camera
        camera = new THREE.PerspectiveCamera(
            50,
            canvas.clientWidth / canvas.clientHeight,
            0.1,
            1000
        );
        camera.position.set(5, 4, 8);

        // Renderer (with color management)
        renderer = new THREE.WebGLRenderer({ 
            canvas, 
            antialias: true,
            preserveDrawingBuffer: true
        });
        resizeRendererToDisplaySize();
        renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
        renderer.shadowMap.enabled = true;
        renderer.shadowMap.type = THREE.PCFSoftShadowMap;
        renderer.outputColorSpace = THREE.SRGBColorSpace;
        renderer.toneMapping = THREE.ACESFilmicToneMapping;
        renderer.toneMappingExposure = 1.2;

        // Controls
        controls = new OrbitControls(camera, renderer.domElement);
        controls.enableDamping = true;
        controls.dampingFactor = 0.05;
        controls.minDistance = 3;
        controls.maxDistance = 20;
        controls.maxPolarAngle = Math.PI / 2;
        controls.target.set(0, 0.8, 0);

        // Lights (HDRI-like setup)
        const hemisphereLight = new THREE.HemisphereLight(0xffffff, 0x444444, 0.6);
        scene.add(hemisphereLight);

        const directionalLight = new THREE.DirectionalLight(0xffffff, 1.2);
        directionalLight.position.set(5, 10, 7);
        directionalLight.castShadow = true;
        directionalLight.shadow.mapSize.width = 2048;
        directionalLight.shadow.mapSize.height = 2048;
        directionalLight.shadow.camera.near = 0.5;
        directionalLight.shadow.camera.far = 50;
        directionalLight.shadow.camera.left = -10;
        directionalLight.shadow.camera.right = 10;
        directionalLight.shadow.camera.top = 10;
        directionalLight.shadow.camera.bottom = -10;
        directionalLight.shadow.bias = -0.0001;
        scene.add(directionalLight);

        const fillLight = new THREE.DirectionalLight(0xd4af37, 0.4);
        fillLight.position.set(-5, 5, -5);
        scene.add(fillLight);

        const rimLight = new THREE.DirectionalLight(0xffffff, 0.5);
        rimLight.position.set(0, 3, -8);
        scene.add(rimLight);

        // Ground
        const groundGeometry = new THREE.PlaneGeometry(50, 50);
        const groundMaterial = new THREE.ShadowMaterial({ opacity: 0.3 });
        groundPlane = new THREE.Mesh(groundGeometry, groundMaterial);
        groundPlane.rotation.x = -Math.PI / 2;
        groundPlane.receiveShadow = true;
        scene.add(groundPlane);

        // Grid
        gridHelper = new THREE.GridHelper(20, 20, 0xd4af37, 0x333333);
        scene.add(gridHelper);

        // Axis
        axisHelper = new THREE.AxesHelper(5);
        axisHelper.visible = false;
        scene.add(axisHelper);

        // Model group
        modelGroup = new THREE.Group();
        modelGroup.name = 'Model';
        scene.add(modelGroup);

        // Start animation loop
        startAnimationLoop();
        
        addLog('Scene initialized successfully', 'success');
    } catch (error) {
        addLog('FATAL: Scene init failed: ' + error.message, 'error');
        console.error('Scene initialization error:', error);
    }
}

function resizeRendererToDisplaySize() {
    const canvas = renderer.domElement;
    const width = canvas.clientWidth;
    const height = canvas.clientHeight;
    const needResize = canvas.width !== width || canvas.height !== height;
    if (needResize) {
        renderer.setSize(width, height, false);
        camera.aspect = width / height;
        camera.updateProjectionMatrix();
    }
    return needResize;
}

function startAnimationLoop() {
    function animate() {
        animationFrameId = requestAnimationFrame(animate);
        
        try {
            // Handle resize
            resizeRendererToDisplaySize();
            
            // Update controls
            if (controls) controls.update();
            
            // Render
            if (renderer && scene && camera) {
                renderer.render(scene, camera);
            }
        } catch (error) {
            addLog('Render error: ' + error.message, 'error');
            console.error('Animation loop error:', error);
        }
    }
    animate();
}

// ===================================
// MODEL GENERATION (UNIVERSAL)
// ===================================

function generateModel() {
    showLoadingState();
    
    setTimeout(() => {
        try {
            // Clear existing model
            clearModelGroup();
            
            const type = APP_STATE.currentModelType;
            const params = APP_STATE.parameters;
            
            // Generate based on type
            switch (type) {
                case 'human':
                    generateHumanoid();
                    break;
                case 'car':
                    generateCar();
                    break;
                case 'house':
                    generateHouse();
                    break;
                case 'tree':
                    generateTree();
                    break;
                case 'robot':
                    generateRobot();
                    break;
                default:
                    generateAnimal();
            }
            
            updateStats();
            autoFrameCamera();
            hideLoadingState();
            hidePlaceholder();
            addLog(`Generated ${type} model`, 'success');
        } catch (error) {
            addLog('Generation failed: ' + error.message, 'error');
            console.error('Model generation error:', error);
            hideLoadingState();
        }
    }, 100);
}

function clearModelGroup() {
    while (modelGroup.children.length > 0) {
        const child = modelGroup.children[0];
        if (child.geometry) child.geometry.dispose();
        if (child.material) {
            if (Array.isArray(child.material)) {
                child.material.forEach(m => m.dispose());
            } else {
                child.material.dispose();
            }
        }
        modelGroup.remove(child);
    }
}

// ===================================
// TOON STYLIZED MATERIAL HELPER
// ===================================

function createToonMaterial(color, options = {}) {
    const style = APP_STATE.renderStyle;
    const matOptions = {
        color: color,
        metalness: 0.05,
        roughness: 0.6,
        ...options
    };

    if (style === 'lowPoly') {
        matOptions.flatShading = true;
    } else if (style === 'clay') {
        matOptions.color = new THREE.Color(0xf5e6d3);
        matOptions.roughness = 0.8;
    }

    return new THREE.MeshStandardMaterial(matOptions);
}

// Auto-frame camera to model bounds
function autoFrameCamera() {
    if (!modelGroup || modelGroup.children.length === 0) return;

    const box = new THREE.Box3().setFromObject(modelGroup);
    const size = box.getSize(new THREE.Vector3());
    const center = box.getCenter(new THREE.Vector3());

    const maxDim = Math.max(size.x, size.y, size.z);
    const fov = camera.fov * (Math.PI / 180);
    let cameraZ = Math.abs(maxDim / 2 / Math.tan(fov / 2));
    cameraZ *= 2.5; // Zoom out a bit

    camera.position.set(
        center.x + cameraZ * 0.7,
        center.y + cameraZ * 0.5,
        center.z + cameraZ * 0.9
    );

    controls.target.copy(center);
    controls.update();
}

// ===================================
// HUMANOID GENERATOR
// ===================================

function generateHumanoid() {
    const params = APP_STATE.parameters;
    const bodyColor = new THREE.Color(params.bodyColor);
    const accentColor = new THREE.Color(params.accentColor);
    const eyeColor = new THREE.Color(params.eyeColor);
    
    const material = new THREE.MeshStandardMaterial({ color: bodyColor });
    const accentMaterial = new THREE.MeshStandardMaterial({ color: accentColor });
    const eyeMaterial = new THREE.MeshStandardMaterial({ color: eyeColor });
    
    // Torso
    const torsoGeom = new THREE.CapsuleGeometry(0.3 * params.bodySize, 0.8 * params.bodyLength, 8, 16);
    const torso = new THREE.Mesh(torsoGeom, material);
    torso.name = 'Torso';
    torso.castShadow = true;
    torso.position.set(0, 0.4 * params.legLength + 0.4 * params.bodyLength, 0);
    modelGroup.add(torso);
    
    // Head
    const headGeom = new THREE.SphereGeometry(0.25 * params.headSize, 16, 16);
    const head = new THREE.Mesh(headGeom, material);
    head.name = 'Head';
    head.castShadow = true;
    const headY = 0.4 * params.legLength + 0.8 * params.bodyLength + 0.3 * params.headSize;
    head.position.set(0, headY, 0);
    modelGroup.add(head);
    
    // Eyes
    const eyeGeom = new THREE.SphereGeometry(0.04 * params.eyeSize, 8, 8);
    const leftEye = new THREE.Mesh(eyeGeom, eyeMaterial);
    leftEye.position.set(-0.08, headY + 0.05, 0.2 * params.headSize);
    modelGroup.add(leftEye);
    
    const rightEye = new THREE.Mesh(eyeGeom.clone(), eyeMaterial.clone());
    rightEye.position.set(0.08, headY + 0.05, 0.2 * params.headSize);
    modelGroup.add(rightEye);
    
    // Arms
    const armGeom = new THREE.CapsuleGeometry(0.08 * params.earSize, 0.6 * params.bodyLength, 6, 12);
    const leftArm = new THREE.Mesh(armGeom, accentMaterial);
    leftArm.name = 'LeftArm';
    leftArm.castShadow = true;
    leftArm.position.set(-0.35 * params.bodySize, 0.4 * params.legLength + 0.5 * params.bodyLength, 0);
    modelGroup.add(leftArm);
    
    const rightArm = new THREE.Mesh(armGeom.clone(), accentMaterial.clone());
    rightArm.name = 'RightArm';
    rightArm.castShadow = true;
    rightArm.position.set(0.35 * params.bodySize, 0.4 * params.legLength + 0.5 * params.bodyLength, 0);
    modelGroup.add(rightArm);
    
    // Legs
    const legGeom = new THREE.CapsuleGeometry(0.1 * params.bodySize, 0.7 * params.legLength, 8, 12);
    const leftLeg = new THREE.Mesh(legGeom, material.clone());
    leftLeg.name = 'LeftLeg';
    leftLeg.castShadow = true;
    leftLeg.position.set(-0.12 * params.bodySize, 0.35 * params.legLength, 0);
    modelGroup.add(leftLeg);
    
    const rightLeg = new THREE.Mesh(legGeom.clone(), material.clone());
    rightLeg.name = 'RightLeg';
    rightLeg.castShadow = true;
    rightLeg.position.set(0.12 * params.bodySize, 0.35 * params.legLength, 0);
    modelGroup.add(rightLeg);
    
    // Hands (optional)
    if (params.eyeSize > 0.8) {
        const handGeom = new THREE.SphereGeometry(0.06 * params.earSize, 8, 8);
        const leftHand = new THREE.Mesh(handGeom, accentMaterial.clone());
        leftHand.position.set(-0.35 * params.bodySize, 0.4 * params.legLength + 0.2 * params.bodyLength - 0.3, 0);
        modelGroup.add(leftHand);
        
        const rightHand = new THREE.Mesh(handGeom.clone(), accentMaterial.clone());
        rightHand.position.set(0.35 * params.bodySize, 0.4 * params.legLength + 0.2 * params.bodyLength - 0.3, 0);
        modelGroup.add(rightHand);
    }
}

// ===================================
// CAR GENERATOR
// ===================================

function generateCar() {
    const params = APP_STATE.parameters;
    const bodyColor = new THREE.Color(params.bodyColor);
    const accentColor = new THREE.Color(params.accentColor);
    const eyeColor = new THREE.Color(params.eyeColor);
    
    // Car body
    const bodyGeom = new THREE.BoxGeometry(1 * params.bodyLength, 0.4 * params.bodySize, 0.6 * params.bodySize);
    const bodyMat = new THREE.MeshStandardMaterial({ color: bodyColor });
    const body = new THREE.Mesh(bodyGeom, bodyMat);
    body.name = 'CarBody';
    body.castShadow = true;
    body.position.set(0, 0.2 * params.legLength + 0.2 * params.bodySize, 0);
    modelGroup.add(body);
    
    // Cabin
    const cabinGeom = new THREE.BoxGeometry(0.5 * params.bodyLength, 0.35 * params.headSize, 0.55 * params.bodySize);
    const cabinMat = new THREE.MeshStandardMaterial({ color: accentColor });
    const cabin = new THREE.Mesh(cabinGeom, cabinMat);
    cabin.castShadow = true;
    cabin.position.set(0, 0.2 * params.legLength + 0.4 * params.bodySize + 0.175 * params.headSize, 0);
    modelGroup.add(cabin);
    
    // Wheels (4)
    const wheelGeom = new THREE.CylinderGeometry(0.15 * params.legLength, 0.15 * params.legLength, 0.1, 16);
    const wheelMat = new THREE.MeshStandardMaterial({ color: eyeColor });
    
    const positions = [
        { x: 0.35 * params.bodyLength, z: 0.4 * params.bodySize },
        { x: 0.35 * params.bodyLength, z: -0.4 * params.bodySize },
        { x: -0.35 * params.bodyLength, z: 0.4 * params.bodySize },
        { x: -0.35 * params.bodyLength, z: -0.4 * params.bodySize },
    ];
    
    positions.forEach((pos, i) => {
        const wheel = new THREE.Mesh(wheelGeom.clone(), wheelMat.clone());
        wheel.name = `Wheel${i}`;
        wheel.rotation.z = Math.PI / 2;
        wheel.castShadow = true;
        wheel.position.set(pos.x, 0.15 * params.legLength, pos.z);
        modelGroup.add(wheel);
    });
    
    // Headlights
    if (params.eyeSize > 0.5) {
        const lightGeom = new THREE.SphereGeometry(0.08 * params.eyeSize, 8, 8);
        const lightMat = new THREE.MeshStandardMaterial({ color: 0xffff00, emissive: 0xffff00, emissiveIntensity: 0.5 });
        
        const leftLight = new THREE.Mesh(lightGeom, lightMat);
        leftLight.position.set(0.5 * params.bodyLength, 0.2 * params.legLength + 0.25 * params.bodySize, 0.2 * params.bodySize);
        modelGroup.add(leftLight);
        
        const rightLight = new THREE.Mesh(lightGeom.clone(), lightMat.clone());
        rightLight.position.set(0.5 * params.bodyLength, 0.2 * params.legLength + 0.25 * params.bodySize, -0.2 * params.bodySize);
        modelGroup.add(rightLight);
    }
}

// ===================================
// HOUSE GENERATOR
// ===================================

function generateHouse() {
    const params = APP_STATE.parameters;
    const bodyColor = new THREE.Color(params.bodyColor);
    const accentColor = new THREE.Color(params.accentColor);
    const eyeColor = new THREE.Color(params.eyeColor);
    
    // Base walls
    const wallGeom = new THREE.BoxGeometry(1.2 * params.bodyLength, 0.8 * params.legLength, 1 * params.bodySize);
    const wallMat = new THREE.MeshStandardMaterial({ color: bodyColor });
    const walls = new THREE.Mesh(wallGeom, wallMat);
    walls.name = 'Walls';
    walls.castShadow = true;
    walls.receiveShadow = true;
    walls.position.set(0, 0.4 * params.legLength, 0);
    modelGroup.add(walls);
    
    // Roof (pyramid)
    const roofGeom = new THREE.ConeGeometry(0.8 * params.bodySize, 0.6 * params.headSize, 4);
    const roofMat = new THREE.MeshStandardMaterial({ color: accentColor });
    const roof = new THREE.Mesh(roofGeom, roofMat);
    roof.name = 'Roof';
    roof.castShadow = true;
    roof.rotation.y = Math.PI / 4;
    roof.position.set(0, 0.8 * params.legLength + 0.3 * params.headSize, 0);
    modelGroup.add(roof);
    
    // Door
    const doorGeom = new THREE.BoxGeometry(0.25 * params.bodyLength, 0.4 * params.legLength, 0.05);
    const doorMat = new THREE.MeshStandardMaterial({ color: eyeColor });
    const door = new THREE.Mesh(doorGeom, doorMat);
    door.name = 'Door';
    door.position.set(0, 0.2 * params.legLength, 0.51 * params.bodySize);
    modelGroup.add(door);
    
    // Windows
    if (params.eyeSize > 0.5) {
        const windowGeom = new THREE.BoxGeometry(0.2 * params.eyeSize, 0.2 * params.eyeSize, 0.05);
        const windowMat = new THREE.MeshStandardMaterial({ color: 0x87CEEB });
        
        const leftWindow = new THREE.Mesh(windowGeom, windowMat);
        leftWindow.position.set(-0.3 * params.bodyLength, 0.5 * params.legLength, 0.51 * params.bodySize);
        modelGroup.add(leftWindow);
        
        const rightWindow = new THREE.Mesh(windowGeom.clone(), windowMat.clone());
        rightWindow.position.set(0.3 * params.bodyLength, 0.5 * params.legLength, 0.51 * params.bodySize);
        modelGroup.add(rightWindow);
    }
}

// ===================================
// TREE GENERATOR
// ===================================

function generateTree() {
    const params = APP_STATE.parameters;
    const bodyColor = new THREE.Color(params.bodyColor);
    const accentColor = new THREE.Color(params.accentColor);
    
    // Trunk
    const trunkGeom = new THREE.CylinderGeometry(0.15 * params.bodySize, 0.2 * params.bodySize, 1 * params.legLength, 12);
    const trunkMat = new THREE.MeshStandardMaterial({ color: bodyColor });
    const trunk = new THREE.Mesh(trunkGeom, trunkMat);
    trunk.name = 'Trunk';
    trunk.castShadow = true;
    trunk.position.set(0, 0.5 * params.legLength, 0);
    modelGroup.add(trunk);
    
    // Foliage (sphere)
    const foliageGeom = new THREE.SphereGeometry(0.6 * params.headSize, 16, 16);
    const foliageMat = new THREE.MeshStandardMaterial({ color: accentColor });
    const foliage = new THREE.Mesh(foliageGeom, foliageMat);
    foliage.name = 'Foliage';
    foliage.castShadow = true;
    foliage.position.set(0, 1 * params.legLength + 0.4 * params.headSize, 0);
    modelGroup.add(foliage);
    
    // Add some smaller foliage clusters
    if (params.earSize > 0.7) {
        const smallFoliageGeom = new THREE.SphereGeometry(0.3 * params.headSize * params.earSize, 12, 12);
        const offsets = [
            { x: 0.4, y: 0.2, z: 0 },
            { x: -0.4, y: 0.2, z: 0 },
            { x: 0, y: 0.2, z: 0.4 },
            { x: 0, y: 0.2, z: -0.4 },
        ];
        
        offsets.forEach((offset, i) => {
            const cluster = new THREE.Mesh(smallFoliageGeom.clone(), foliageMat.clone());
            cluster.position.set(
                offset.x * params.headSize,
                1 * params.legLength + offset.y * params.headSize,
                offset.z * params.headSize
            );
            modelGroup.add(cluster);
        });
    }
}

// ===================================
// ROBOT GENERATOR
// ===================================

function generateRobot() {
    const params = APP_STATE.parameters;
    const bodyColor = new THREE.Color(params.bodyColor);
    const accentColor = new THREE.Color(params.accentColor);
    const eyeColor = new THREE.Color(params.eyeColor);
    
    // Torso (box)
    const torsoGeom = new THREE.BoxGeometry(0.5 * params.bodySize, 0.6 * params.bodyLength, 0.4 * params.bodySize);
    const torsoMat = new THREE.MeshStandardMaterial({ color: bodyColor, metalness: 0.7, roughness: 0.3 });
    const torso = new THREE.Mesh(torsoGeom, torsoMat);
    torso.name = 'RobotTorso';
    torso.castShadow = true;
    torso.position.set(0, 0.5 * params.legLength + 0.3 * params.bodyLength, 0);
    modelGroup.add(torso);
    
    // Head (box)
    const headGeom = new THREE.BoxGeometry(0.35 * params.headSize, 0.35 * params.headSize, 0.35 * params.headSize);
    const headMat = new THREE.MeshStandardMaterial({ color: accentColor, metalness: 0.7, roughness: 0.3 });
    const head = new THREE.Mesh(headGeom, headMat);
    head.name = 'RobotHead';
    head.castShadow = true;
    const headY = 0.5 * params.legLength + 0.6 * params.bodyLength + 0.2 * params.headSize;
    head.position.set(0, headY, 0);
    modelGroup.add(head);
    
    // Eyes (glowing)
    if (params.eyeSize > 0.5) {
        const eyeGeom = new THREE.SphereGeometry(0.06 * params.eyeSize, 8, 8);
        const eyeMat = new THREE.MeshStandardMaterial({ color: eyeColor, emissive: eyeColor, emissiveIntensity: 0.8 });
        
        const leftEye = new THREE.Mesh(eyeGeom, eyeMat);
        leftEye.position.set(-0.1 * params.headSize, headY, 0.18 * params.headSize);
        modelGroup.add(leftEye);
        
        const rightEye = new THREE.Mesh(eyeGeom.clone(), eyeMat.clone());
        rightEye.position.set(0.1 * params.headSize, headY, 0.18 * params.headSize);
        modelGroup.add(rightEye);
    }
    
    // Arms (cylinders)
    const armGeom = new THREE.CylinderGeometry(0.06 * params.earSize, 0.06 * params.earSize, 0.5 * params.bodyLength, 12);
    const armMat = new THREE.MeshStandardMaterial({ color: accentColor, metalness: 0.7, roughness: 0.3 });
    
    const leftArm = new THREE.Mesh(armGeom, armMat);
    leftArm.name = 'LeftArm';
    leftArm.castShadow = true;
    leftArm.position.set(-0.3 * params.bodySize, 0.5 * params.legLength + 0.4 * params.bodyLength, 0);
    modelGroup.add(leftArm);
    
    const rightArm = new THREE.Mesh(armGeom.clone(), armMat.clone());
    rightArm.name = 'RightArm';
    rightArm.castShadow = true;
    rightArm.position.set(0.3 * params.bodySize, 0.5 * params.legLength + 0.4 * params.bodyLength, 0);
    modelGroup.add(rightArm);
    
    // Legs (cylinders)
    const legGeom = new THREE.CylinderGeometry(0.08 * params.bodySize, 0.08 * params.bodySize, 0.8 * params.legLength, 12);
    const legMat = new THREE.MeshStandardMaterial({ color: bodyColor, metalness: 0.7, roughness: 0.3 });
    
    const leftLeg = new THREE.Mesh(legGeom, legMat);
    leftLeg.name = 'LeftLeg';
    leftLeg.castShadow = true;
    leftLeg.position.set(-0.12 * params.bodySize, 0.4 * params.legLength, 0);
    modelGroup.add(leftLeg);
    
    const rightLeg = new THREE.Mesh(legGeom.clone(), legMat.clone());
    rightLeg.name = 'RightLeg';
    rightLeg.castShadow = true;
    rightLeg.position.set(0.12 * params.bodySize, 0.4 * params.legLength, 0);
    modelGroup.add(rightLeg);
    
    // Antenna
    const antennaGeom = new THREE.CylinderGeometry(0.02, 0.02, 0.3 * params.headSize, 6);
    const antenna = new THREE.Mesh(antennaGeom, armMat.clone());
    antenna.position.set(0, headY + 0.175 * params.headSize + 0.15 * params.headSize, 0);
    modelGroup.add(antenna);
    
    const antennaBall = new THREE.Mesh(
        new THREE.SphereGeometry(0.05, 8, 8),
        new THREE.MeshStandardMaterial({ color: 0xff0000, emissive: 0xff0000, emissiveIntensity: 0.5 })
    );
    antennaBall.position.set(0, headY + 0.175 * params.headSize + 0.3 * params.headSize, 0);
    modelGroup.add(antennaBall);
}

// ===================================
// ANIMAL GENERATOR (CUTE TOON STYLE)
// ===================================

function generateAnimal() {
    const params = APP_STATE.parameters;
    const type = APP_STATE.currentModelType;
    const bodyColor = new THREE.Color(params.bodyColor);
    const accentColor = new THREE.Color(params.accentColor);
    const eyeColor = new THREE.Color(params.eyeColor);

    // Body (using LatheGeometry for smoother, rounder body)
    const bodyProfile = [
        new THREE.Vector2(0, 0),
        new THREE.Vector2(0.3 * params.bodySize, 0.1),
        new THREE.Vector2(0.42 * params.bodySize, 0.3 * params.bodyLength),
        new THREE.Vector2(0.45 * params.bodySize, 0.6 * params.bodyLength),
        new THREE.Vector2(0.4 * params.bodySize, 0.9 * params.bodyLength),
        new THREE.Vector2(0.3 * params.bodySize, 1.1 * params.bodyLength),
        new THREE.Vector2(0, 1.2 * params.bodyLength)
    ];
    const bodyGeom = new THREE.LatheGeometry(bodyProfile, 24);
    const bodyMat = createToonMaterial(bodyColor);
    const body = new THREE.Mesh(bodyGeom, bodyMat);
    body.name = 'Body';
    body.castShadow = true;
    body.receiveShadow = true;
    body.position.set(0, 0.8 * params.legLength, 0);
    body.rotation.z = Math.PI / 2;
    modelGroup.add(body);

    // Head (spherical with slight squash)
    const headGeom = new THREE.SphereGeometry(0.4 * params.headSize, 24, 16);
    const headMat = createToonMaterial(bodyColor);
    const head = new THREE.Mesh(headGeom, headMat);
    head.name = 'Head';
    head.castShadow = true;
    head.scale.set(1, 0.95, 1); // Slightly squashed for cuteness
    const headY = 0.8 * params.legLength;
    const headX = (1.2 * params.bodyLength) / 2 + 0.3 * params.headSize;
    head.position.set(headX, headY, 0);
    modelGroup.add(head);

    // Snout (rounded using capsule)
    if (params.snoutLength > 0.1) {
        const snoutGeom = new THREE.CapsuleGeometry(
            0.18 * params.headSize,
            0.35 * params.snoutLength,
            8,
            12
        );
        const snoutMat = createToonMaterial(accentColor);
        const snout = new THREE.Mesh(snoutGeom, snoutMat);
        snout.name = 'Snout';
        snout.castShadow = true;
        const snoutX = headX + 0.4 * params.headSize + 0.18 * params.snoutLength;
        snout.position.set(snoutX, headY - 0.08 * params.headSize, 0);
        snout.rotation.z = Math.PI / 2;
        modelGroup.add(snout);

        // Nose (tiny sphere)
        const noseGeom = new THREE.SphereGeometry(0.08 * params.headSize, 12, 12);
        const noseMat = createToonMaterial(new THREE.Color(0x000000));
        const nose = new THREE.Mesh(noseGeom, noseMat);
        nose.position.set(snoutX + 0.2 * params.snoutLength, headY - 0.08 * params.headSize, 0);
        modelGroup.add(nose);
    }

    // Ears (stylized based on type)
    const ears = createStylizedEars(type, bodyColor, headX, headY);
    ears.forEach(ear => modelGroup.add(ear));

    // Eyes (larger, cuter, with highlights)
    const eyeGeom = new THREE.SphereGeometry(0.08 * params.eyeSize, 16, 16);
    const eyeMat = createToonMaterial(eyeColor, { emissive: eyeColor, emissiveIntensity: 0.1 });
    
    const eyeX = headX + 0.28 * params.headSize;
    const leftEye = new THREE.Mesh(eyeGeom, eyeMat);
    leftEye.name = 'LeftEye';
    leftEye.position.set(eyeX, headY + 0.12 * params.headSize, 0.18 * params.headSize);
    modelGroup.add(leftEye);
    
    const rightEye = new THREE.Mesh(eyeGeom.clone(), eyeMat.clone());
    rightEye.name = 'RightEye';
    rightEye.position.set(eyeX, headY + 0.12 * params.headSize, -0.18 * params.headSize);
    modelGroup.add(rightEye);

    // Eye highlights (tiny white spheres for cuteness)
    const highlightGeom = new THREE.SphereGeometry(0.03 * params.eyeSize, 8, 8);
    const highlightMat = createToonMaterial(new THREE.Color(0xffffff), { emissive: new THREE.Color(0xffffff), emissiveIntensity: 0.8 });
    
    const leftHighlight = new THREE.Mesh(highlightGeom, highlightMat);
    leftHighlight.position.set(eyeX + 0.04, headY + 0.15 * params.headSize, 0.2 * params.headSize);
    modelGroup.add(leftHighlight);
    
    const rightHighlight = new THREE.Mesh(highlightGeom.clone(), highlightMat.clone());
    rightHighlight.position.set(eyeX + 0.04, headY + 0.15 * params.headSize, -0.16 * params.headSize);
    modelGroup.add(rightHighlight);

    // Legs (tapered capsules)
    const legGeom = new THREE.CapsuleGeometry(0.12 * params.bodySize, 0.75 * params.legLength, 12, 8);
    const legMat = createToonMaterial(bodyColor);
    
    const legPositions = [
        { x: 0.45 * params.bodyLength, z: 0.28 * params.bodySize },
        { x: 0.45 * params.bodyLength, z: -0.28 * params.bodySize },
        { x: -0.35 * params.bodyLength, z: 0.28 * params.bodySize },
        { x: -0.35 * params.bodyLength, z: -0.28 * params.bodySize },
    ];
    
    legPositions.forEach((pos, i) => {
        const leg = new THREE.Mesh(legGeom.clone(), legMat.clone());
        leg.name = `Leg${i}`;
        leg.castShadow = true;
        leg.position.set(pos.x, 0.38 * params.legLength, pos.z);
        leg.scale.set(1, 1, 0.9); // Slightly thinner
        modelGroup.add(leg);

        // Paws (rounded, cute)
        const pawGeom = new THREE.SphereGeometry(0.14 * params.bodySize, 16, 16);
        pawGeom.scale(1, 0.7, 1); // Flatten slightly
        const pawMat = createToonMaterial(accentColor);
        const paw = new THREE.Mesh(pawGeom, pawMat);
        paw.name = `Paw${i}`;
        paw.castShadow = true;
        paw.position.set(pos.x, 0.08, pos.z);
        modelGroup.add(paw);
    });

    // Tail (curved using TubeGeometry with CatmullRomCurve3)
    if (params.tailLength > 0.2) {
        const tailCurvePoints = [];
        const tailBaseX = -(1.2 * params.bodyLength) / 2 - 0.2;
        const tailBaseY = 0.85 * params.legLength;
        const segments = 8;
        
        for (let i = 0; i <= segments; i++) {
            const t = i / segments;
            const x = tailBaseX - t * 0.7 * params.tailLength;
            const y = tailBaseY + Math.sin(t * Math.PI * 0.8) * 0.3 * params.tailLength;
            const z = 0;
            tailCurvePoints.push(new THREE.Vector3(x, y, z));
        }
        
        const tailCurve = new THREE.CatmullRomCurve3(tailCurvePoints);
        const tailRadius = 0.08 * params.bodySize;
        const tailGeom = new THREE.TubeGeometry(tailCurve, 16, tailRadius, 8, false);
        const tailMat = createToonMaterial(accentColor);
        const tail = new THREE.Mesh(tailGeom, tailMat);
        tail.name = 'Tail';
        tail.castShadow = true;
        modelGroup.add(tail);

        // Tail tip (sphere for rounded end)
        const tailTipGeom = new THREE.SphereGeometry(tailRadius * 1.3, 12, 12);
        const tailTip = new THREE.Mesh(tailTipGeom, tailMat.clone());
        tailTip.position.copy(tailCurvePoints[tailCurvePoints.length - 1]);
        modelGroup.add(tailTip);
    }
}

function createStylizedEars(type, color, headX, headY) {
    const params = APP_STATE.parameters;
    const ears = [];
    const material = createToonMaterial(color);
    
    if (type === 'dog') {
        // Floppy rounded ears
        const earGeom = new THREE.CapsuleGeometry(0.12 * params.earSize, 0.35 * params.earSize, 8, 12);
        
        const leftEar = new THREE.Mesh(earGeom, material);
        leftEar.name = 'LeftEar';
        leftEar.castShadow = true;
        leftEar.position.set(headX - 0.15, headY + 0.25 * params.headSize, 0.28 * params.headSize);
        leftEar.rotation.set(0.4, 0, 0.3);
        ears.push(leftEar);
        
        const rightEar = new THREE.Mesh(earGeom.clone(), material.clone());
        rightEar.name = 'RightEar';
        rightEar.castShadow = true;
        rightEar.position.set(headX - 0.15, headY + 0.25 * params.headSize, -0.28 * params.headSize);
        rightEar.rotation.set(-0.4, 0, -0.3);
        ears.push(rightEar);
        
    } else if (type === 'cat') {
        // Pointy triangle ears
        const earGeom = new THREE.ConeGeometry(0.15 * params.earSize, 0.45 * params.earSize, 8);
        
        const leftEar = new THREE.Mesh(earGeom, material);
        leftEar.name = 'LeftEar';
        leftEar.castShadow = true;
        leftEar.position.set(headX - 0.05, headY + 0.42 * params.headSize, 0.22 * params.headSize);
        leftEar.rotation.set(0, 0, 0.1);
        ears.push(leftEar);
        
        const rightEar = new THREE.Mesh(earGeom.clone(), material.clone());
        rightEar.name = 'RightEar';
        rightEar.castShadow = true;
        rightEar.position.set(headX - 0.05, headY + 0.42 * params.headSize, -0.22 * params.headSize);
        rightEar.rotation.set(0, 0, -0.1);
        ears.push(rightEar);
        
    } else {
        // Default large pointy ears (fox, rabbit, bird)
        const earGeom = new THREE.ConeGeometry(0.18 * params.earSize, 0.55 * params.earSize, 8);
        
        const leftEar = new THREE.Mesh(earGeom, material);
        leftEar.name = 'LeftEar';
        leftEar.castShadow = true;
        leftEar.position.set(headX - 0.08, headY + 0.48 * params.headSize, 0.2 * params.headSize);
        ears.push(leftEar);
        
        const rightEar = new THREE.Mesh(earGeom.clone(), material.clone());
        rightEar.name = 'RightEar';
        rightEar.castShadow = true;
        rightEar.position.set(headX - 0.08, headY + 0.48 * params.headSize, -0.2 * params.headSize);
        ears.push(rightEar);
    }
    
    return ears;
}

// ===================================
// UI CONTROLS
// ===================================

function setupUIControls() {
    // Preset buttons
    document.querySelectorAll('.pet-type-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            APP_STATE.currentModelType = btn.dataset.type;
            
            // Load preset if available
            if (MODEL_PRESETS[APP_STATE.currentModelType]) {
                const preset = MODEL_PRESETS[APP_STATE.currentModelType];
                Object.keys(preset).forEach(key => {
                    if (APP_STATE.parameters.hasOwnProperty(key)) {
                        APP_STATE.parameters[key] = preset[key];
                    }
                });
                syncUIWithState();
            }
            
            generateModel();
            addLog(`Loaded ${btn.dataset.type} preset`, 'success');
        });
    });

    // Style toggle buttons
    document.querySelectorAll('.style-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            APP_STATE.renderStyle = btn.dataset.style;
            
            // Update active state
            document.querySelectorAll('.style-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            
            // Regenerate model with new style
            generateModel();
            addLog(`Changed style to ${btn.dataset.style}`, 'success');
        });
    });
    
    // Image upload
    const imageUpload = document.getElementById('imageUploadStep1');
    if (imageUpload) {
        imageUpload.addEventListener('change', async (e) => {
            const file = e.target.files[0];
            if (!file) return;
            
            addLog('Processing uploaded image...', 'info');
            
            const uploadPreview = document.getElementById('uploadPreview');
            
            try {
                // Read file and display preview
                const reader = new FileReader();
                reader.onload = async (event) => {
                    // Show preview in upload tab
                    if (uploadPreview) {
                        uploadPreview.innerHTML = `<img src="${event.target.result}" alt="Uploaded Image" style="max-width: 100%; border-radius: 8px;">`;\n                        uploadPreview.classList.remove('hidden');
                    }
                    
                    // Show detection overlay
                    showImageDetectionOverlay();
                    
                    const preview = document.getElementById('uploadedImagePreview');
                    const result = document.getElementById('detectionResult');
                    
                    if (preview) {
                        preview.src = event.target.result;
                        preview.onload = async () => {
                            // Run AI detection
                            result.textContent = 'Analyzing with AI...';
                            
                            try {
                                const detection = await detectWithMobileNet(preview);
                                APP_STATE.lastDetectedImage = detection;
                                
                                result.textContent = `${detection.description}\n(Confidence: ${Math.round(detection.confidence * 100)}%)`;
                                addLog(`Detected: ${detection.detectedType} (${Math.round(detection.confidence * 100)}%)`, 'success');
                            } catch (error) {
                                result.textContent = 'AI detection unavailable. Pick a preset manually.';
                                addLog('Detection fallback mode', 'warning');
                            }
                        };
                    }
                };
                reader.readAsDataURL(file);
            } catch (error) {
                addLog('Error processing image: ' + error.message, 'error');
                hideImageDetectionOverlay();
            }
            
            e.target.value = '';
        });
    }
    
    // Confirm detection
    const confirmBtn = document.getElementById('confirmDetectionBtn');
    if (confirmBtn) {
        confirmBtn.addEventListener('click', () => {
            if (APP_STATE.lastDetectedImage) {
                APP_STATE.currentModelType = APP_STATE.lastDetectedImage.detectedType;
                
                // Load preset
                if (MODEL_PRESETS[APP_STATE.currentModelType]) {
                    const preset = MODEL_PRESETS[APP_STATE.currentModelType];
                    Object.keys(preset).forEach(key => {
                        if (APP_STATE.parameters.hasOwnProperty(key)) {
                            APP_STATE.parameters[key] = preset[key];
                        }
                    });
                    syncUIWithState();
                }
                
                hideImageDetectionOverlay();
                generateModel();
                addLog(`Generated ${APP_STATE.currentModelType} from image`, 'success');
                
                // Enable Step 1 Next button
                const step1NextBtn = document.getElementById('step1NextBtn');
                if (step1NextBtn) {
                    step1NextBtn.disabled = false;
                }
            }
        });
    }
    
    // Cancel detection
    const cancelBtn = document.getElementById('cancelDetectionBtn');
    if (cancelBtn) {
        cancelBtn.addEventListener('click', hideImageDetectionOverlay);
    }

    // Parameter sliders
    const params = ['bodySize', 'bodyLength', 'headSize', 'snoutLength', 'earSize', 'legLength', 'tailLength', 'eyeSize'];
    params.forEach(param => {
        const slider = document.getElementById(param);
        const valueDisplay = document.getElementById(param + 'Value');
        
        if (!slider || !valueDisplay) return;
        
        const updateSliderFill = (slider) => {
            const min = parseFloat(slider.min);
            const max = parseFloat(slider.max);
            const value = parseFloat(slider.value);
            const percentage = ((value - min) / (max - min)) * 100;
            slider.style.setProperty('--value', `${percentage}%`);
        };
        
        updateSliderFill(slider);
        
        slider.addEventListener('input', (e) => {
            const value = parseFloat(e.target.value);
            APP_STATE.parameters[param] = value;
            valueDisplay.textContent = value.toFixed(1);
            updateSliderFill(e.target);
            generateModel();
        });
    });

    // Color pickers
    const colors = ['bodyColor', 'accentColor', 'eyeColor'];
    colors.forEach(colorParam => {
        const picker = document.getElementById(colorParam);
        if (!picker) return;
        picker.addEventListener('input', (e) => {
            APP_STATE.parameters[colorParam] = e.target.value;
            generateModel();
        });
    });

    // Randomize
    document.getElementById('randomizeBtn')?.addEventListener('click', () => {
        randomizeModel();
    });

    // Export
    document.getElementById('exportGlbBtn')?.addEventListener('click', exportGLB);

    // Save/Load presets
    document.getElementById('savePresetBtn')?.addEventListener('click', savePreset);
    document.getElementById('loadPresetBtn')?.addEventListener('click', () => {
        document.getElementById('loadPresetFile')?.click();
    });
    document.getElementById('loadPresetFile')?.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            loadPreset(e.target.files[0]);
        }
    });

    // Canvas controls
    document.getElementById('toggleGrid')?.addEventListener('click', () => {
        if (gridHelper) gridHelper.visible = !gridHelper.visible;
    });
    document.getElementById('toggleAxis')?.addEventListener('click', () => {
        if (axisHelper) axisHelper.visible = !axisHelper.visible;
    });
    document.getElementById('screenshotBtn')?.addEventListener('click', takeScreenshot);
    document.getElementById('resetCamera')?.addEventListener('click', () => {
        if (camera && controls) {
            camera.position.set(5, 4, 8);
            controls.target.set(0, 0.8, 0);
            controls.update();
        }
    });

    // Export overlay
    document.getElementById('unlockExportBtn')?.addEventListener('click', startCheckout);
    document.getElementById('closeOverlayBtn')?.addEventListener('click', hideExportLockedOverlay);

    // Tab switching
    setupTabSwitching();

    // AI Chat Interface
    setupAIChat();

    // Step 1 Next button
    setupStepNavigation();

    syncUIWithState();
}

// ===================================
// TAB SWITCHING
// ===================================

function setupTabSwitching() {
    const tabButtons = document.querySelectorAll('.tab-btn');
    const uploadTab = document.getElementById('tab-upload');
    const aiTab = document.getElementById('tab-ai');
    
    if (!tabButtons.length || !uploadTab || !aiTab) return;
    
    tabButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            const targetTab = btn.dataset.tab;
            
            // Update active button
            tabButtons.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            
            // Show/hide tabs
            if (targetTab === 'upload') {
                uploadTab.classList.remove('hidden');
                aiTab.classList.add('hidden');
            } else if (targetTab === 'ai') {
                uploadTab.classList.add('hidden');
                aiTab.classList.remove('hidden');
            }
        });
    });
}

// ===================================
// STEP NAVIGATION
// ===================================

function setupStepNavigation() {
    const step1NextBtn = document.getElementById('step1NextBtn');
    const step1 = document.getElementById('step1');
    const step2 = document.getElementById('step2');
    
    if (!step1NextBtn || !step1 || !step2) return;
    
    step1NextBtn.addEventListener('click', () => {
        if (!step1NextBtn.disabled) {
            step1.classList.add('hidden');
            step2.classList.remove('hidden');
            addLog('Moving to Step 2: Generate 3D Mesh', 'info');
        }
    });
}

// ===================================
// AI CHAT INTERFACE
// ===================================

function setupAIChat() {
    const chatInput = document.getElementById('aiChatInput');
    const sendBtn = document.getElementById('aiChatSendBtn');
    const chatMessages = document.getElementById('aiChatMessages');
    
    if (!chatInput || !sendBtn || !chatMessages) return;
    
    // Send message on Enter key
    chatInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendAIMessage();
        }
    });
    
    // Send message on button click
    sendBtn.addEventListener('click', sendAIMessage);
    
    function sendAIMessage() {
        const message = chatInput.value.trim();
        if (!message) return;
        
        // Add user message to chat
        addChatMessage(message, 'user');
        chatInput.value = '';
        
        // Show generating message
        addChatMessage('Generating...', 'assistant', true);
        
        // Get style and aspect settings
        const style = document.getElementById('aiStyle')?.value || 'PetPaws';
        const aspect = document.getElementById('aiAspect')?.value || '1:1';
        
        // Generate AI image
        generateAIImage(message, style, aspect);
    }
}

function addChatMessage(content, sender = 'assistant', isLoading = false) {
    const chatMessages = document.getElementById('aiChatMessages');
    if (!chatMessages) return;
    
    const messageDiv = document.createElement('div');
    messageDiv.className = `chat-message ${sender}`;
    
    const avatar = document.createElement('div');
    avatar.className = 'message-avatar';
    avatar.textContent = sender === 'user' ? '👤' : '🤖';
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    
    if (isLoading) {
        const loadingSpan = document.createElement('div');
        loadingSpan.className = 'message-loading';
        loadingSpan.innerHTML = '<span></span><span></span><span></span>';
        contentDiv.appendChild(loadingSpan);
    } else {
        const p = document.createElement('p');
        p.textContent = content;
        contentDiv.appendChild(p);
    }
    
    messageDiv.appendChild(avatar);
    messageDiv.appendChild(contentDiv);
    chatMessages.appendChild(messageDiv);
    
    // Auto-scroll to bottom
    chatMessages.scrollTop = chatMessages.scrollHeight;
    
    return messageDiv;
}

// ===================================
// AI IMAGE GENERATION
// ===================================

async function generateAIImage(prompt, style, aspect) {
    const aiImagePreview = document.getElementById('aiImagePreview');
    const aiProgress = document.getElementById('aiProgress');
    const step1NextBtn = document.getElementById('step1NextBtn');
    const chatMessages = document.getElementById('aiChatMessages');
    
    try {
        // Show progress
        if (aiProgress) {
            aiProgress.classList.remove('hidden');
            const progressFill = aiProgress.querySelector('.progress-fill');
            const progressText = aiProgress.querySelector('.progress-text');
            if (progressFill) progressFill.style.width = '30%';
            if (progressText) progressText.textContent = '30%';
        }
        
        let imageUrl = null;
        
        // Try real API if api-client exists
        if (typeof APIClient !== 'undefined') {
            try {
                const apiClient = new APIClient();
                const result = await apiClient.generateImage(prompt, style, aspect);
                imageUrl = result.imageUrl || result.url;
            } catch (apiError) {
                console.warn('API call failed, using fallback:', apiError);
            }
        }
        
        // Fallback: Generate placeholder based on prompt
        if (!imageUrl) {
            imageUrl = generatePlaceholderImageUrl(prompt, style);
            await new Promise(resolve => setTimeout(resolve, 1500)); // Simulate delay
        }
        
        // Update progress
        if (aiProgress) {
            const progressFill = aiProgress.querySelector('.progress-fill');
            const progressText = aiProgress.querySelector('.progress-text');
            if (progressFill) progressFill.style.width = '100%';
            if (progressText) progressText.textContent = '100%';
        }
        
        // Show image preview
        if (aiImagePreview) {
            aiImagePreview.innerHTML = `<img src="${imageUrl}" alt="Generated Image" style="max-width: 100%; border-radius: 8px;">`;
            aiImagePreview.classList.remove('hidden');
        }
        
        // Hide progress
        if (aiProgress) {
            setTimeout(() => aiProgress.classList.add('hidden'), 500);
        }
        
        // Enable Step 1 Next button
        if (step1NextBtn) {
            step1NextBtn.disabled = false;
        }
        
        // Remove loading message and add success
        const loadingMessages = chatMessages?.querySelectorAll('.message-loading');
        if (loadingMessages) {
            loadingMessages.forEach(msg => msg.closest('.chat-message')?.remove());
        }
        addChatMessage(`✨ Image generated! You can now proceed to Step 2.`, 'assistant');
        
        addLog(`AI image generated: ${prompt}`, 'success');
        
    } catch (error) {
        console.error('Image generation error:', error);
        
        // Hide progress
        if (aiProgress) aiProgress.classList.add('hidden');
        
        // Remove loading messages
        const loadingMessages = chatMessages?.querySelectorAll('.message-loading');
        if (loadingMessages) {
            loadingMessages.forEach(msg => msg.closest('.chat-message')?.remove());
        }
        
        addChatMessage(`❌ Error: ${error.message}. Please try again.`, 'assistant');
        addLog('Image generation failed: ' + error.message, 'error');
    }
}

function generatePlaceholderImageUrl(prompt, style) {
    // Generate a placeholder image URL based on prompt keywords
    const lower = prompt.toLowerCase();
    const width = 512;
    const height = 512;
    
    // Extract color from prompt
    let color = '6366f1'; // default purple
    if (lower.includes('red')) color = 'ef4444';
    else if (lower.includes('blue')) color = '3b82f6';
    else if (lower.includes('green')) color = '10b981';
    else if (lower.includes('yellow')) color = 'fbbf24';
    else if (lower.includes('brown')) color = '92400e';
    else if (lower.includes('orange')) color = 'f97316';
    else if (lower.includes('pink')) color = 'ec4899';
    else if (lower.includes('purple')) color = 'a855f7';
    
    // Extract subject
    let text = 'AI Generated';
    if (lower.includes('dog')) text = 'Dog';
    else if (lower.includes('cat')) text = 'Cat';
    else if (lower.includes('robot')) text = 'Robot';
    else if (lower.includes('car')) text = 'Car';
    else if (lower.includes('tree')) text = 'Tree';
    else if (lower.includes('house')) text = 'House';
    
    // Use a placeholder service
    return `https://via.placeholder.com/${width}x${height}/${color}/ffffff?text=${encodeURIComponent(text + ' - ' + style)}`;
}

async function processAIChat(userMessage) {
    const lower = userMessage.toLowerCase();
    
    // Show loading message
    const loadingMsg = addChatMessage('', 'assistant', true);
    
    // Simulate AI thinking delay
    await new Promise(resolve => setTimeout(resolve, 800));
    
    // Remove loading message
    if (loadingMsg) loadingMsg.remove();
    
    // Parse user intent and detect what they want to create
    const detectedType = detectModelTypeFromText(lower);
    const colors = extractColorsFromText(lower);
    const style = detectStyleFromText(lower);
    
    // Build AI response
    let response = '';
    let shouldGenerate = false;
    
    if (detectedType !== 'custom') {
        response = `I understand you want to create a ${detectedType}! `;
        shouldGenerate = true;
        
        if (colors.length > 0) {
            response += `I'll use ${colors.join(', ')} colors. `;
        }
        
        if (style) {
            response += `Style: ${style}. `;
        }
        
        response += `Generating your 3D model now...`;
        
        // Add response
        addChatMessage(response, 'assistant');
        
        // Load preset and generate
        APP_STATE.currentModelType = detectedType;
        if (MODEL_PRESETS[detectedType]) {
            const preset = MODEL_PRESETS[detectedType];
            Object.keys(preset).forEach(key => {
                if (APP_STATE.parameters.hasOwnProperty(key)) {
                    APP_STATE.parameters[key] = preset[key];
                }
            });
        }
        
        // Apply colors if detected
        if (colors.length > 0) {
            APP_STATE.colors.body = colors[0] || APP_STATE.colors.body;
            APP_STATE.colors.accent = colors[1] || colors[0] || APP_STATE.colors.accent;
        }
        
        syncUIWithState();
        generateModel();
        updateStats();
        
        // Show success message
        await new Promise(resolve => setTimeout(resolve, 1000));
        addChatMessage(`✨ Done! Your ${detectedType} is ready. You can adjust it using the sliders below.`, 'assistant');
        
    } else {
        // Couldn't detect specific type
        response = `I'm not sure what you'd like to create. Could you be more specific? For example:
        
• "Create a brown dog"
• "Make a futuristic robot"
• "Generate a fantasy tree"
• "Build a sports car"`;
        
        addChatMessage(response, 'assistant');
    }
}

function detectModelTypeFromText(text) {
    // Dog keywords
    if (text.match(/\b(dog|puppy|canine|wolf|husky|labrador|shepherd|poodle)\b/i)) {
        return 'dog';
    }
    
    // Cat keywords
    if (text.match(/\b(cat|kitten|feline|kitty|meow|persian|tabby)\b/i)) {
        return 'cat';
    }
    
    // Fox keywords
    if (text.match(/\b(fox|vixen)\b/i)) {
        return 'fox';
    }
    
    // Bird keywords
    if (text.match(/\b(bird|eagle|hawk|parrot|crow|raven|owl|chicken)\b/i)) {
        return 'bird';
    }
    
    // Fish keywords
    if (text.match(/\b(fish|shark|dolphin|whale|goldfish)\b/i)) {
        return 'fish';
    }
    
    // Rabbit keywords
    if (text.match(/\b(rabbit|bunny|hare)\b/i)) {
        return 'rabbit';
    }
    
    // Human keywords
    if (text.match(/\b(human|person|character|man|woman|boy|girl|humanoid)\b/i)) {
        return 'human';
    }
    
    // Car keywords
    if (text.match(/\b(car|vehicle|automobile|truck|van|suv|sports car|race car)\b/i)) {
        return 'car';
    }
    
    // House keywords
    if (text.match(/\b(house|home|building|cottage|mansion|cabin)\b/i)) {
        return 'house';
    }
    
    // Tree keywords
    if (text.match(/\b(tree|oak|pine|palm|forest|plant)\b/i)) {
        return 'tree';
    }
    
    // Robot keywords
    if (text.match(/\b(robot|android|mech|cyborg|automaton|droid)\b/i)) {
        return 'robot';
    }
    
    return 'custom';
}

function extractColorsFromText(text) {
    const colors = [];
    const colorMap = {
        'red': '#ff3333',
        'blue': '#3366ff',
        'green': '#33cc33',
        'yellow': '#ffdd33',
        'orange': '#ff9933',
        'purple': '#9933ff',
        'pink': '#ff99cc',
        'brown': '#8b4513',
        'black': '#222222',
        'white': '#ffffff',
        'gray': '#888888',
        'grey': '#888888',
        'gold': '#ffd700',
        'silver': '#c0c0c0',
        'cyan': '#00ffff',
        'magenta': '#ff00ff'
    };
    
    Object.keys(colorMap).forEach(colorName => {
        if (text.includes(colorName)) {
            colors.push(colorMap[colorName]);
        }
    });
    
    return colors;
}

function detectStyleFromText(text) {
    if (text.includes('cute') || text.includes('kawaii') || text.includes('adorable')) {
        return 'Cute';
    }
    if (text.includes('realistic') || text.includes('detailed')) {
        return 'realistic';
    }
    if (text.includes('ff14') || text.includes('final fantasy')) {
        return 'FF14-tone';
    }
    return 'PetPaws'; // Default
}

function syncUIWithState() {
    // Update sliders
    Object.keys(APP_STATE.parameters).forEach(key => {
        const element = document.getElementById(key);
        const valueElement = document.getElementById(key + 'Value');
        if (element && element.type === 'range') {
            element.value = APP_STATE.parameters[key];
            const min = parseFloat(element.min);
            const max = parseFloat(element.max);
            const value = parseFloat(element.value);
            const percentage = ((value - min) / (max - min)) * 100;
            element.style.setProperty('--value', `${percentage}%`);
            
            if (valueElement) {
                valueElement.textContent = parseFloat(APP_STATE.parameters[key]).toFixed(1);
            }
        } else if (element) {
            element.value = APP_STATE.parameters[key];
        }
    });

    // Update preset buttons
    document.querySelectorAll('.pet-type-btn').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.type === APP_STATE.currentModelType);
    });

    updateTierBadge();
    updateExportCount();
}

function updateTierBadge() {
    const badge = document.getElementById('tier-badge');
    if (badge) {
        badge.textContent = APP_STATE.tier.toUpperCase();
        badge.classList.toggle('vip', APP_STATE.tier === 'vip');
    }
}

function updateExportCount() {
    const countElement = document.getElementById('exports-remaining');
    if (!countElement) return;
    
    if (APP_STATE.tier === 'free') {
        const remaining = APP_STATE.maxFreeExports - APP_STATE.exportsThisSession;
        countElement.textContent = `Exports: ${remaining}/${APP_STATE.maxFreeExports}`;
    } else {
        countElement.textContent = 'Exports: Unlimited';
    }
}

// ===================================
// STATS
// ===================================

function updateStats() {
    try {
        let triangleCount = 0;
        let meshCount = 0;
        const box = new THREE.Box3();
        
        modelGroup.traverse((obj) => {
            if (obj instanceof THREE.Mesh) {
                meshCount++;
                if (obj.geometry) {
                    const geo = obj.geometry;
                    if (geo.index) {
                        triangleCount += geo.index.count / 3;
                    } else if (geo.attributes.position) {
                        triangleCount += geo.attributes.position.count / 3;
                    }
                    box.expandByObject(obj);
                }
            }
        });
        
        const size = new THREE.Vector3();
        box.getSize(size);
        
        document.getElementById('triangleCount').textContent = Math.round(triangleCount);
        document.getElementById('meshCount').textContent = meshCount;
        document.getElementById('boundWidth').textContent = size.x.toFixed(2) + 'm';
        document.getElementById('boundHeight').textContent = size.y.toFixed(2) + 'm';
        document.getElementById('boundDepth').textContent = size.z.toFixed(2) + 'm';
    } catch (error) {
        console.error('Stats update error:', error);
    }
}

// ===================================
// EXPORT GLB
// ===================================

function exportGLB() {
    if (APP_STATE.exportLocked) {
        showExportLockedOverlay();
        addLog('Export locked - upgrade required', 'warning');
        return;
    }

    if (APP_STATE.tier === 'free') {
        if (APP_STATE.exportsThisSession >= APP_STATE.maxFreeExports) {
            showExportLockedOverlay();
            addLog('Free export limit reached', 'warning');
            return;
        }
        APP_STATE.exportsThisSession++;
        updateExportCount();
    }

    addLog('Exporting GLB...', 'info');

    const exporter = new GLTFExporter();
    
    exporter.parse(
        modelGroup,
        (gltf) => {
            const blob = new Blob([gltf], { type: 'application/octet-stream' });
            const url = URL.createObjectURL(blob);
            const link = document.createElement('a');
            link.href = url;
            link.download = `5xLiving_${APP_STATE.currentModelType}_${Date.now()}.glb`;
            link.click();
            URL.revokeObjectURL(url);
            
            addLog('GLB exported successfully!', 'success');
        },
        (error) => {
            console.error('Export error:', error);
            addLog('Export failed: ' + error.message, 'error');
        },
        { binary: true }
    );
}

// ===================================
// PRESETS
// ===================================

function savePreset() {
    const preset = {
        version: '2.0',
        modelType: APP_STATE.currentModelType,
        parameters: { ...APP_STATE.parameters },
        timestamp: new Date().toISOString(),
    };

    const json = JSON.stringify(preset, null, 2);
    const blob = new Blob([json], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `preset_${APP_STATE.currentModelType}_${Date.now()}.json`;
    link.click();
    URL.revokeObjectURL(url);

    addLog('Preset saved', 'success');
}

function loadPreset(file) {
    const reader = new FileReader();
    reader.onload = (e) => {
        try {
            const preset = JSON.parse(e.target.result);
            
            if (!preset.version || !preset.modelType || !preset.parameters) {
                throw new Error('Invalid preset format');
            }

            APP_STATE.currentModelType = preset.modelType;
            APP_STATE.parameters = { ...APP_STATE.parameters, ...preset.parameters };

            syncUIWithState();
            generateModel();

            addLog('Preset loaded successfully', 'success');
        } catch (error) {
            console.error('Preset load error:', error);
            addLog('Failed to load preset: ' + error.message, 'error');
        }
    };
    reader.readAsText(file);
}

function randomizeModel() {
    const params = APP_STATE.parameters;
    
    params.bodySize = 0.7 + Math.random() * 1.3;
    params.bodyLength = 0.7 + Math.random() * 1.3;
    params.headSize = 0.7 + Math.random() * 1.1;
    params.snoutLength = Math.random() * 1.2;
    params.earSize = 0.5 + Math.random() * 1.5;
    params.legLength = 0.6 + Math.random() * 1.4;
    params.tailLength = 0.5 + Math.random() * 2.5;
    params.eyeSize = 0.5 + Math.random();
    
    // Random colors
    params.bodyColor = '#' + Math.floor(Math.random()*16777215).toString(16).padStart(6, '0');
    params.accentColor = '#' + Math.floor(Math.random()*16777215).toString(16).padStart(6, '0');
    params.eyeColor = '#' + Math.floor(Math.random()*16777215).toString(16).padStart(6, '0');
    
    syncUIWithState();
    generateModel();
    addLog('Randomized parameters', 'success');
}

// ===================================
// SCREENSHOTS
// ===================================

function takeScreenshot() {
    try {
        renderer.render(scene, camera);
        const canvas = document.getElementById('canvas3d');
        canvas.toBlob((blob) => {
            const url = URL.createObjectURL(blob);
            const link = document.createElement('a');
            link.href = url;
            link.download = `5xLiving_Screenshot_${Date.now()}.png`;
            link.click();
            URL.revokeObjectURL(url);
            addLog('Screenshot saved', 'success');
        });
    } catch (error) {
        addLog('Screenshot failed: ' + error.message, 'error');
    }
}

// ===================================
// MONETIZATION
// ===================================

function showExportLockedOverlay() {
    document.getElementById('exportLockedOverlay')?.classList.remove('hidden');
}

function hideExportLockedOverlay() {
    document.getElementById('exportLockedOverlay')?.classList.add('hidden');
}

function startCheckout() {
    addLog('Checkout initiated (demo)', 'warning');
    alert('Demo: In production, this would redirect to payment processor.');
    
    // Demo upgrade
    APP_STATE.tier = 'vip';
    APP_STATE.exportLocked = false;
    updateTierBadge();
    updateExportCount();
    hideExportLockedOverlay();
    saveSettings();
    
    addLog('Upgraded to VIP (demo)', 'success');
}

// ===================================
// ACTIVITY LOG
// ===================================

function addLog(message, type = 'info') {
    const logContainer = document.getElementById('activityLog');
    if (!logContainer) return;
    
    const entry = document.createElement('div');
    entry.className = `log-entry ${type}`;
    
    const timestamp = new Date().toLocaleTimeString();
    entry.innerHTML = `<span class="log-timestamp">[${timestamp}]</span> ${message}`;
    
    logContainer.appendChild(entry);
    logContainer.scrollTop = logContainer.scrollHeight;

    // Keep only last 50 entries
    while (logContainer.children.length > 50) {
        logContainer.removeChild(logContainer.firstChild);
    }
    
    // Also log to console for debugging
    if (type === 'error') {
        console.error(message);
    } else if (type === 'warning') {
        console.warn(message);
    } else {
        console.log(message);
    }
}

// ===================================
// UI HELPERS
// ===================================

function showLoadingState() {
    document.getElementById('loadingskeleton')?.classList.add('visible');
}

function hideLoadingState() {
    document.getElementById('loadingSkeleton')?.classList.remove('visible');
}

function showPlaceholder() {
    document.getElementById('previewPlaceholder')?.classList.add('visible');
}

function hidePlaceholder() {
    document.getElementById('previewPlaceholder')?.classList.remove('visible');
}

function showImageDetectionOverlay() {
    document.getElementById('imagePreviewOverlay')?.classList.remove('hidden');
}

function hideImageDetectionOverlay() {
    document.getElementById('imagePreviewOverlay')?.classList.add('hidden');
}

// ===================================
// LOCAL STORAGE
// ===================================

function loadSettings() {
    const saved = localStorage.getItem('5xliving_model_settings');
    if (saved) {
        try {
            const settings = JSON.parse(saved);
            APP_STATE.tier = settings.tier || 'free';
            APP_STATE.exportsThisSession = settings.exportsThisSession || 0;
        } catch (e) {
            console.error('Failed to load settings:', e);
        }
    }
}

function saveSettings() {
    const settings = {
        tier: APP_STATE.tier,
        exportsThisSession: APP_STATE.exportsThisSession,
    };
    localStorage.setItem('5xliving_model_settings', JSON.stringify(settings));
}

window.addEventListener('beforeunload', saveSettings);

// ===================================
// INITIALIZATION
// ===================================

function init() {
    try {
        addLog('Initializing 5XLiving Universal 3D Model Maker...', 'info');
        loadSettings();
        initScene();
        setupUIControls();
        generateModel();
        addLog('Ready! Upload an image or select a preset.', 'success');
    } catch (error) {
        addLog('FATAL: Initialization failed: ' + error.message, 'error');
        console.error('Init error:', error);
    }
}

// Start when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}
