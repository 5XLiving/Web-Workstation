/**
 * 5XLiving Universal 3D Model Maker
 * Main application logic with AI image detection
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
    car: { bodySize: 1.2, bodyLength: 1.5, headSize: 0.7, snoutLength: 0.5, earSize: 0.8, legLength: 0.5, tailLength: 0.8, eyeSize: 0.6 },
    house: { bodySize: 1.3, bodyLength: 1.2, headSize: 1.2, snoutLength: 0.8, earSize: 0.5, legLength: 1.2, tailLength: 0.5, eyeSize: 0.8 },
    tree: { bodySize: 0.6, bodyLength: 0.6, headSize: 1.5, snoutLength: 0, earSize: 0.5, legLength: 1.5, tailLength: 0.5, eyeSize: 0.5 },
    human: { bodySize: 0.7, bodyLength: 0.5, headSize: 0.8, snoutLength: 0.2, earSize: 0.5, legLength: 1.5, tailLength: 0.5, eyeSize: 0.8 },
    robot: { bodySize: 1, bodyLength: 0.8, headSize: 0.9, snoutLength: 0.4, earSize: 0.8, legLength: 1.2, tailLength: 0.6, eyeSize: 1 },
    custom: { bodySize: 1, bodyLength: 1, headSize: 1, snoutLength: 0.5, earSize: 1, legLength: 1, tailLength: 1, eyeSize: 1 }
};

// ===================================
// AI IMAGE DETECTION
// ===================================

async function detectObjectFromImage(imageFile) {
    return new Promise((resolve) => {
        const reader = new FileReader();
        reader.onload = (e) => {
            const img = new Image();
            img.onload = () => {
                // Create canvas for analysis
                const canvas = document.createElement('canvas');
                const ctx = canvas.getContext('2d');
                canvas.width = 224; // Standard size for analysis
                canvas.height = 224;
                ctx.drawImage(img, 0, 0, 224, 224);
                
                // Simple detection based on color analysis and edge detection
                const imageData = ctx.getImageData(0, 0, 224, 224);
                const analysis = analyzeImage(imageData);
                
                resolve({
                    detectedType: analysis.type,
                    confidence: analysis.confidence,
                    imageUrl: e.target.result,
                    description: analysis.description
                });
            };
            img.src = e.target.result;
        };
        reader.readAsDataURL(imageFile);
    });
}

function analyzeImage(imageData) {
    const pixels = imageData.data;
    let avgR = 0, avgG = 0, avgB = 0;
    let edgeCount = 0;
    let darkPixels = 0;
    let brightPixels = 0;
    
    // Analyze colors and brightness
    for (let i = 0; i < pixels.length; i += 4) {
        const r = pixels[i];
        const g = pixels[i + 1];
        const b = pixels[i + 2];
        
        avgR += r;
        avgG += g;
        avgB += b;
        
        const brightness = (r + g + b) / 3;
        if (brightness < 60) darkPixels++;
        if (brightness > 200) brightPixels++;
        
        // Simple edge detection
        if (i > 224 * 4) {
            const prevR = pixels[i - 224 * 4];
            if (Math.abs(r - prevR) > 30) edgeCount++;
        }
    }
    
    const pixelCount = pixels.length / 4;
    avgR /= pixelCount;
    avgG /= pixelCount;
    avgB /= pixelCount;
    
    const edgeDensity = edgeCount / pixelCount;
    const darkRatio = darkPixels / pixelCount;
    const brightRatio = brightPixels / pixelCount;
    
    // Detection logic based on color patterns
    let detectedType = 'custom';
    let confidence = 0.5;
    let description = 'Custom shape detected';
    
    // Brown/tan tones -> dog
    if (avgR > 100 && avgG > 70 && avgB < 90 && edgeDensity > 0.15) {
        detectedType = 'dog';
        confidence = 0.75;
        description = 'Detected canine/dog-like shape with brown tones';
    }
    // Orange tones -> fox/cat
    else if (avgR > 150 && avgG > 80 && avgG < 130 && avgB < 70) {
        detectedType = Math.random() > 0.5 ? 'fox' : 'cat';
        confidence = 0.7;
        description = 'Detected feline shape with orange/tan coloring';
    }
    // Gray/white tones with edges -> cat/rabbit
    else if (avgR > 120 && avgG > 120 && avgB > 120 && Math.abs(avgR - avgG) < 30) {
        detectedType = edgeDensity > 0.2 ? 'cat' : 'rabbit';
        confidence = 0.65;
        description = 'Detected small mammal with light coloring';
    }
    // Blue tones -> fish/bird
    else if (avgB > avgR && avgB > avgG && brightRatio > 0.3) {
        detectedType = edgeDensity > 0.18 ? 'bird' : 'fish';
        confidence = 0.7;
        description = 'Detected aquatic or avian creature with blue tones';
    }
    // Green tones -> tree
    else if (avgG > avgR && avgG > avgB && avgG > 100) {
        detectedType = 'tree';
        confidence = 0.8;
        description = 'Detected plant/tree with green foliage';
    }
    // Dark colors with geometric shapes -> car/robot
    else if (darkRatio > 0.4 && edgeDensity > 0.25) {
        detectedType = Math.random() > 0.5 ? 'car' : 'robot';
        confidence = 0.65;
        description = 'Detected mechanical/vehicle-like object';
    }
    // Strong edges and structure -> house
    else if (edgeDensity > 0.3 && darkRatio < 0.5 && brightRatio > 0.2) {
        detectedType = 'house';
        confidence = 0.7;
        description = 'Detected architectural structure';
    }
    // Human skin tones
    else if (avgR > 150 && avgR < 220 && avgG > 100 && avgG < 180 && avgB > 80 && avgB < 160) {
        detectedType = 'human';
        confidence = 0.68;
        description = 'Detected humanoid figure with skin tones';
    }
    
    return { type: detectedType, confidence, description };
}

// ===================================
// APP STATE
// ===================================

const APP_STATE = {
    currentPetType: 'dog',
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
    tier: 'free', // 'free' or 'vip'
    exportsThisSession: 0,
    maxFreeExports: 1,
    exportLocked: false, // Set to true to enable paywall
    lastDetectedImage: null,
};

// ===================================
// THREE.JS SCENE SETUP
// ===================================

let scene, camera, renderer, controls;
let petGroup; // Root group for the pet
let gridHelper, axisHelper;
let groundPlane;

function initScene() {
    // Scene
    scene = new THREE.Scene();
    scene.background = new THREE.Color(0x0a0a0a);

    // Camera
    camera = new THREE.PerspectiveCamera(
        50,
        window.innerWidth / window.innerHeight,
        0.1,
        1000
    );
    camera.position.set(5, 4, 8);

    // Renderer
    const canvas = document.getElementById('canvas3d');
    renderer = new THREE.WebGLRenderer({ 
        canvas, 
        antialias: true,
        preserveDrawingBuffer: true // For screenshots
    });
    renderer.setSize(canvas.clientWidth, canvas.clientHeight);
    renderer.setPixelRatio(window.devicePixelRatio);
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFSoftShadowMap;

    // Controls
    controls = new OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.05;
    controls.minDistance = 3;
    controls.maxDistance = 20;
    controls.maxPolarAngle = Math.PI / 2;

    // Lights
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.5);
    scene.add(ambientLight);

    const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
    directionalLight.position.set(5, 10, 7);
    directionalLight.castShadow = true;
    directionalLight.shadow.mapSize.width = 2048;
    directionalLight.shadow.mapSize.height = 2048;
    directionalLight.shadow.camera.far = 50;
    scene.add(directionalLight);

    const fillLight = new THREE.DirectionalLight(0xd4af37, 0.3);
    fillLight.position.set(-5, 5, -5);
    scene.add(fillLight);

    // Ground plane (invisible, for shadows)
    const groundGeometry = new THREE.PlaneGeometry(50, 50);
    const groundMaterial = new THREE.ShadowMaterial({ opacity: 0.3 });
    groundPlane = new THREE.Mesh(groundGeometry, groundMaterial);
    groundPlane.rotation.x = -Math.PI / 2;
    groundPlane.receiveShadow = true;
    scene.add(groundPlane);

    // Grid helper
    gridHelper = new THREE.GridHelper(20, 20, 0xd4af37, 0x333333);
    scene.add(gridHelper);

    // Axis helper
    axisHelper = new THREE.AxesHelper(5);
    axisHelper.visible = false;
    scene.add(axisHelper);

    // Pet group
    petGroup = new THREE.Group();
    petGroup.name = 'Pet';
    scene.add(petGroup);

    // Start animation loop
    animate();

    // Log
    addLog('Scene initialized', 'success');
}

function animate() {
    requestAnimationFrame(animate);
    controls.update();
    renderer.render(scene, camera);
}

// Handle window resize
window.addEventListener('resize', () => {
    const canvas = document.getElementById('canvas3d');
    camera.aspect = canvas.clientWidth / canvas.clientHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(canvas.clientWidth, canvas.clientHeight);
});

// ===================================
// PET GENERATION
// ===================================

function generatePet() {
    // Show loading state
    showLoadingState();
    
    // Small delay for visual feedback
    setTimeout(() => {
        // Clear existing pet
        while (petGroup.children.length > 0) {
            const child = petGroup.children[0];
            if (child.geometry) child.geometry.dispose();
            if (child.material) child.material.dispose();
            petGroup.remove(child);
        }

        const params = APP_STATE.parameters;
        const type = APP_STATE.currentPetType;

        // Colors
        const bodyColor = new THREE.Color(params.bodyColor);
        const accentColor = new THREE.Color(params.accentColor);
        const eyeColor = new THREE.Color(params.eyeColor);

        // Body
        const body = createBody(bodyColor);
        petGroup.add(body);

    // Head
    const head = createHead(bodyColor);
    petGroup.add(head);

    // Snout
    if (params.snoutLength > 0.1) {
        const snout = createSnout(accentColor);
        petGroup.add(snout);
    }

    // Ears
    const ears = createEars(type, bodyColor);
    ears.forEach(ear => petGroup.add(ear));

    // Eyes
    const eyes = createEyes(eyeColor);
    eyes.forEach(eye => petGroup.add(eye));

    // Legs
    const legs = createLegs(bodyColor);
    legs.forEach(leg => petGroup.add(leg));

    // Tail
    const tail = createTail(type, accentColor);
    petGroup.add(tail);

    // Update stats
    updateStats();
    
    // Hide loading, hide placeholder
    hideLoadingState();
    hidePlaceholder();

    // Log
    addLog(`Generated ${type} with custom parameters`, 'success');
    }, 300); // Short delay for loading animation
}

function createBody(color) {
    const params = APP_STATE.parameters;
    const geometry = new THREE.CapsuleGeometry(
        0.4 * params.bodySize,
        1.2 * params.bodyLength,
        8,
        16
    );
    const material = new THREE.MeshStandardMaterial({ color });
    const mesh = new THREE.Mesh(geometry, material);
    mesh.name = 'Body';
    mesh.castShadow = true;
    mesh.receiveShadow = true;
    mesh.position.set(0, 0.8 * params.legLength, 0);
    mesh.rotation.z = Math.PI / 2; // Horizontal
    return mesh;
}

function createHead(color) {
    const params = APP_STATE.parameters;
    const geometry = new THREE.SphereGeometry(0.35 * params.headSize, 16, 16);
    const material = new THREE.MeshStandardMaterial({ color });
    const mesh = new THREE.Mesh(geometry, material);
    mesh.name = 'Head';
    mesh.castShadow = true;
    mesh.receiveShadow = true;
    
    const headY = 0.8 * params.legLength;
    const headX = (1.2 * params.bodyLength) / 2 + 0.2 * params.headSize;
    mesh.position.set(headX, headY, 0);
    
    return mesh;
}

function createSnout(color) {
    const params = APP_STATE.parameters;
    const geometry = new THREE.CapsuleGeometry(
        0.15 * params.headSize,
        0.3 * params.snoutLength,
        6,
        8
    );
    const material = new THREE.MeshStandardMaterial({ color });
    const mesh = new THREE.Mesh(geometry, material);
    mesh.name = 'Snout';
    mesh.castShadow = true;
    mesh.receiveShadow = true;
    
    const headY = 0.8 * params.legLength;
    const headX = (1.2 * params.bodyLength) / 2 + 0.2 * params.headSize;
    const snoutX = headX + 0.35 * params.headSize + 0.15 * params.snoutLength;
    mesh.position.set(snoutX, headY - 0.05, 0);
    mesh.rotation.z = Math.PI / 2;
    
    return mesh;
}

function createEars(type, color) {
    const params = APP_STATE.parameters;
    const ears = [];
    
    const headY = 0.8 * params.legLength;
    const headX = (1.2 * params.bodyLength) / 2 + 0.2 * params.headSize;
    
    if (type === 'dog') {
        // Floppy ears
        const geometry = new THREE.BoxGeometry(
            0.15 * params.earSize,
            0.3 * params.earSize,
            0.05
        );
        const material = new THREE.MeshStandardMaterial({ color });
        
        const leftEar = new THREE.Mesh(geometry, material);
        leftEar.name = 'EarLeft';
        leftEar.castShadow = true;
        leftEar.position.set(headX - 0.1, headY + 0.2 * params.headSize, 0.25 * params.headSize);
        leftEar.rotation.x = 0.3;
        ears.push(leftEar);
        
        const rightEar = new THREE.Mesh(geometry, material.clone());
        rightEar.name = 'EarRight';
        rightEar.castShadow = true;
        rightEar.position.set(headX - 0.1, headY + 0.2 * params.headSize, -0.25 * params.headSize);
        rightEar.rotation.x = -0.3;
        ears.push(rightEar);
        
    } else if (type === 'cat') {
        // Pointy ears
        const geometry = new THREE.ConeGeometry(0.15 * params.earSize, 0.4 * params.earSize, 6);
        const material = new THREE.MeshStandardMaterial({ color });
        
        const leftEar = new THREE.Mesh(geometry, material);
        leftEar.name = 'EarLeft';
        leftEar.castShadow = true;
        leftEar.position.set(headX, headY + 0.35 * params.headSize, 0.2 * params.headSize);
        ears.push(leftEar);
        
        const rightEar = new THREE.Mesh(geometry, material.clone());
        rightEar.name = 'EarRight';
        rightEar.castShadow = true;
        rightEar.position.set(headX, headY + 0.35 * params.headSize, -0.2 * params.headSize);
        ears.push(rightEar);
        
    } else if (type === 'fox') {
        // Large pointy ears
        const geometry = new THREE.ConeGeometry(0.18 * params.earSize, 0.5 * params.earSize, 6);
        const material = new THREE.MeshStandardMaterial({ color });
        
        const leftEar = new THREE.Mesh(geometry, material);
        leftEar.name = 'EarLeft';
        leftEar.castShadow = true;
        leftEar.position.set(headX - 0.05, headY + 0.4 * params.headSize, 0.18 * params.headSize);
        ears.push(leftEar);
        
        const rightEar = new THREE.Mesh(geometry, material.clone());
        rightEar.name = 'EarRight';
        rightEar.castShadow = true;
        rightEar.position.set(headX - 0.05, headY + 0.4 * params.headSize, -0.18 * params.headSize);
        ears.push(rightEar);
    }
    
    return ears;
}

function createEyes(color) {
    const params = APP_STATE.parameters;
    const eyes = [];
    
    const geometry = new THREE.SphereGeometry(0.06 * params.eyeSize, 8, 8);
    const material = new THREE.MeshStandardMaterial({ color });
    
    const headY = 0.8 * params.legLength;
    const headX = (1.2 * params.bodyLength) / 2 + 0.2 * params.headSize;
    const eyeX = headX + 0.25 * params.headSize;
    
    const leftEye = new THREE.Mesh(geometry, material);
    leftEye.name = 'EyeLeft';
    leftEye.position.set(eyeX, headY + 0.08, 0.15 * params.headSize);
    eyes.push(leftEye);
    
    const rightEye = new THREE.Mesh(geometry, material.clone());
    rightEye.name = 'EyeRight';
    rightEye.position.set(eyeX, headY + 0.08, -0.15 * params.headSize);
    eyes.push(rightEye);
    
    return eyes;
}

function createLegs(color) {
    const params = APP_STATE.parameters;
    const legs = [];
    
    const geometry = new THREE.CylinderGeometry(0.12, 0.1, 0.6 * params.legLength, 8);
    const material = new THREE.MeshStandardMaterial({ color });
    
    const bodyY = 0.8 * params.legLength;
    const legY = (0.6 * params.legLength) / 2;
    
    const positions = [
        { x: 0.4 * params.bodyLength, z: 0.25 * params.bodySize, name: 'LegFrontLeft' },
        { x: 0.4 * params.bodyLength, z: -0.25 * params.bodySize, name: 'LegFrontRight' },
        { x: -0.4 * params.bodyLength, z: 0.25 * params.bodySize, name: 'LegBackLeft' },
        { x: -0.4 * params.bodyLength, z: -0.25 * params.bodySize, name: 'LegBackRight' },
    ];
    
    positions.forEach(pos => {
        const leg = new THREE.Mesh(geometry, material.clone());
        leg.name = pos.name;
        leg.castShadow = true;
        leg.receiveShadow = true;
        leg.position.set(pos.x, legY, pos.z);
        legs.push(leg);
    });
    
    return legs;
}

function createTail(type, color) {
    const params = APP_STATE.parameters;
    
    let geometry;
    if (type === 'cat' || type === 'fox') {
        // Thin tail
        geometry = new THREE.CylinderGeometry(0.08, 0.05, 0.8 * params.tailLength, 8);
    } else {
        // Dog tail
        geometry = new THREE.ConeGeometry(0.1, 0.6 * params.tailLength, 8);
    }
    
    const material = new THREE.MeshStandardMaterial({ color });
    const mesh = new THREE.Mesh(geometry, material);
    mesh.name = 'Tail';
    mesh.castShadow = true;
    mesh.receiveShadow = true;
    
    const tailX = -(1.2 * params.bodyLength) / 2 - 0.3 * params.tailLength;
    const tailY = 0.8 * params.legLength + 0.1;
    mesh.position.set(tailX, tailY, 0);
    mesh.rotation.z = -Math.PI / 4;
    
    return mesh;
}

// ===================================
// EXPORT GLB
// ===================================

function exportGLB() {
    // Check if export is locked
    if (APP_STATE.exportLocked) {
        showExportLockedOverlay();
        addLog('Export locked - upgrade required', 'warning');
        return;
    }

    // Check free tier limits
    if (APP_STATE.tier === 'free') {
        if (APP_STATE.exportsThisSession >= APP_STATE.maxFreeExports) {
            showExportLockedOverlay();
            addLog('Free export limit reached', 'warning');
            return;
        }
        APP_STATE.exportsThisSession++;
        updateExportCount();
    }

    addLog('Exporting GLB...', 'success');

    const exporter = new GLTFExporter();
    
    exporter.parse(
        petGroup,
        (gltf) => {
            const blob = new Blob([gltf], { type: 'application/octet-stream' });
            const url = URL.createObjectURL(blob);
            const link = document.createElement('a');
            link.href = url;
            link.download = `5xLiving_Pet_${APP_STATE.currentPetType}_${Date.now()}.glb`;
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
        version: '1.0',
        petType: APP_STATE.currentPetType,
        parameters: { ...APP_STATE.parameters },
        timestamp: new Date().toISOString(),
    };

    const json = JSON.stringify(preset, null, 2);
    const blob = new Blob([json], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `pet_preset_${APP_STATE.currentPetType}_${Date.now()}.json`;
    link.click();
    URL.revokeObjectURL(url);

    addLog('Preset saved', 'success');
}

function loadPreset(file) {
    const reader = new FileReader();
    reader.onload = (e) => {
        try {
            const preset = JSON.parse(e.target.result);
            
            // Validate preset
            if (!preset.version || !preset.petType || !preset.parameters) {
                throw new Error('Invalid preset format');
            }

            // Apply preset
            APP_STATE.currentPetType = preset.petType;
            APP_STATE.parameters = { ...APP_STATE.parameters, ...preset.parameters };

            // Update UI
            updateUIFromState();
            generatePet();

            addLog('Preset loaded successfully', 'success');
        } catch (error) {
            console.error('Preset load error:', error);
            addLog('Failed to load preset: ' + error.message, 'error');
        }
    };
    reader.readAsText(file);
}

// ===================================
// RANDOMIZE
// ===================================

function randomizePet(seed) {
    // Simple seeded random function
    const random = seed ? seededRandom(seed) : Math.random;

    APP_STATE.parameters.bodySize = 0.7 + random() * 1.0;
    APP_STATE.parameters.bodyLength = 0.7 + random() * 1.0;
    APP_STATE.parameters.headSize = 0.7 + random() * 0.8;
    APP_STATE.parameters.snoutLength = random() * 1.2;
    APP_STATE.parameters.earSize = 0.5 + random() * 1.2;
    APP_STATE.parameters.legLength = 0.7 + random() * 1.0;
    APP_STATE.parameters.tailLength = 0.8 + random() * 1.8;
    APP_STATE.parameters.eyeSize = 0.6 + random() * 0.8;

    // Random colors
    APP_STATE.parameters.bodyColor = randomColor(random);
    APP_STATE.parameters.accentColor = randomColor(random);
    APP_STATE.parameters.eyeColor = randomDarkColor(random);

    updateUIFromState();
    generatePet();

    addLog(`Randomized with seed: ${seed || 'random'}`, 'success');
}

function seededRandom(seed) {
    let value = parseInt(seed, 36) || 12345;
    return function() {
        value = (value * 9301 + 49297) % 233280;
        return value / 233280;
    };
}

function randomColor(random) {
    const hue = Math.floor(random() * 360);
    const sat = 30 + Math.floor(random() * 40);
    const light = 40 + Math.floor(random() * 30);
    return hslToHex(hue, sat, light);
}

function randomDarkColor(random) {
    const hue = Math.floor(random() * 360);
    const sat = 20 + Math.floor(random() * 30);
    const light = 10 + Math.floor(random() * 20);
    return hslToHex(hue, sat, light);
}

function hslToHex(h, s, l) {
    l /= 100;
    const a = s * Math.min(l, 1 - l) / 100;
    const f = n => {
        const k = (n + h / 30) % 12;
        const color = l - a * Math.max(Math.min(k - 3, 9 - k, 1), -1);
        return Math.round(255 * color).toString(16).padStart(2, '0');
    };
    return `#${f(0)}${f(8)}${f(4)}`;
}

// ===================================
// STATS
// ===================================

function updateStats() {
    let triangleCount = 0;
    let meshCount = 0;

    petGroup.traverse((child) => {
        if (child.isMesh) {
            meshCount++;
            if (child.geometry) {
                const positions = child.geometry.attributes.position;
                if (positions) {
                    triangleCount += positions.count / 3;
                }
            }
        }
    });

    // Calculate bounding box
    const box = new THREE.Box3().setFromObject(petGroup);
    const size = new THREE.Vector3();
    box.getSize(size);

    document.getElementById('triangleCount').textContent = Math.round(triangleCount).toLocaleString();
    document.getElementById('meshCount').textContent = meshCount;
    document.getElementById('boundWidth').textContent = size.x.toFixed(2) + 'm';
    document.getElementById('boundHeight').textContent = size.y.toFixed(2) + 'm';
    document.getElementById('boundDepth').textContent = size.z.toFixed(2) + 'm';
}

// ===================================
// UI CONTROLS
// ===================================

function setupUIControls() {
    // Pet type buttons
    document.querySelectorAll('.pet-type-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            document.querySelectorAll('.pet-type-btn').forEach(b => b.classList.remove('active'));
            e.target.classList.add('active');
            APP_STATE.currentPetType = e.target.dataset.type;
            generatePet();
        });
    });

    // Parameter sliders
    const params = ['bodySize', 'bodyLength', 'headSize', 'snoutLength', 'earSize', 'legLength', 'tailLength', 'eyeSize'];
    params.forEach(param => {
        const slider = document.getElementById(param);
        const valueDisplay = document.getElementById(param + 'Value');
        
        // Update slider track fill
        const updateSliderFill = (slider) => {
            const min = parseFloat(slider.min);
            const max = parseFloat(slider.max);
            const value = parseFloat(slider.value);
            const percentage = ((value - min) / (max - min)) * 100;
            slider.style.setProperty('--value', `${percentage}%`);
        };
        
        // Initial fill
        updateSliderFill(slider);
        
        slider.addEventListener('input', (e) => {
            const value = parseFloat(e.target.value);
            APP_STATE.parameters[param] = value;
            valueDisplay.textContent = value.toFixed(1);
            updateSliderFill(e.target);
            generatePet();
        });
    });

    // Color pickers
    const colors = ['bodyColor', 'accentColor', 'eyeColor'];
    colors.forEach(colorParam => {
        const picker = document.getElementById(colorParam);
        picker.addEventListener('input', (e) => {
            APP_STATE.parameters[colorParam] = e.target.value;
            generatePet();
        });
    });

    // Randomize button
    document.getElementById('randomizeBtn').addEventListener('click', () => {
        const seed = document.getElementById('seedInput').value;
        randomizePet(seed || null);
    });

    // Export GLB button
    document.getElementById('exportGlbBtn').addEventListener('click', exportGLB);

    // Save/Load preset buttons
    document.getElementById('savePresetBtn').addEventListener('click', savePreset);
    document.getElementById('loadPresetBtn').addEventListener('click', () => {
        document.getElementById('loadPresetFile').click();
    });
    document.getElementById('loadPresetFile').addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            loadPreset(e.target.files[0]);
        }
    });

    // Canvas controls
    document.getElementById('toggleGrid').addEventListener('click', () => {
        gridHelper.visible = !gridHelper.visible;
    });

    document.getElementById('toggleAxis').addEventListener('click', () => {
        axisHelper.visible = !axisHelper.visible;
    });

    document.getElementById('screenshotBtn').addEventListener('click', takeScreenshot);

    document.getElementById('resetCamera').addEventListener('click', () => {
        camera.position.set(5, 4, 8);
        controls.target.set(0, 0.8, 0);
        controls.update();
    });

    // Export locked overlay
    document.getElementById('unlockExportBtn').addEventListener('click', startCheckout);
    document.getElementById('closeOverlayBtn').addEventListener('click', hideExportLockedOverlay);

    // Initialize UI from state
    updateUIFromState();
}

function updateUIFromState() {
    // Update sliders and values
    Object.keys(APP_STATE.parameters).forEach(key => {
        const element = document.getElementById(key);
        const valueElement = document.getElementById(key + 'Value');
        if (element && element.type === 'range') {
            element.value = APP_STATE.parameters[key];
            // Update slider fill
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

    // Update pet type buttons
    document.querySelectorAll('.pet-type-btn').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.type === APP_STATE.currentPetType);
    });

    // Update tier badge
    updateTierBadge();
    updateExportCount();
}

function updateTierBadge() {
    const badge = document.getElementById('tier-badge');
    badge.textContent = APP_STATE.tier.toUpperCase();
    badge.classList.toggle('vip', APP_STATE.tier === 'vip');
}

function updateExportCount() {
    const countElement = document.getElementById('exports-remaining');
    if (APP_STATE.tier === 'free') {
        const remaining = APP_STATE.maxFreeExports - APP_STATE.exportsThisSession;
        countElement.textContent = `Exports: ${remaining}/${APP_STATE.maxFreeExports}`;
    } else {
        countElement.textContent = 'Exports: Unlimited';
    }
}

// ===================================
// SCREENSHOTS
// ===================================

function takeScreenshot() {
    renderer.render(scene, camera);
    const canvas = document.getElementById('canvas3d');
    canvas.toBlob((blob) => {
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `5xLiving_Pet_Screenshot_${Date.now()}.png`;
        link.click();
        URL.revokeObjectURL(url);
        addLog('Screenshot saved', 'success');
    });
}

// ===================================
// MONETIZATION
// ===================================

function showExportLockedOverlay() {
    document.getElementById('exportLockedOverlay').classList.remove('hidden');
}

function hideExportLockedOverlay() {
    document.getElementById('exportLockedOverlay').classList.add('hidden');
}

function startCheckout() {
    // Stub function for future Stripe/Shopify integration
    addLog('Checkout initiated (stub)', 'warning');
    alert('This is a demo. In production, this would redirect to Stripe checkout.');
    
    // For demo: simulate upgrade
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
}

// ===================================
// UI HELPERS - LOADING & PLACEHOLDER
// ===================================

function showLoadingState() {
    const skeleton = document.getElementById('loadingSkeleton');
    if (skeleton) skeleton.classList.add('visible');
}

function hideLoadingState() {
    const skeleton = document.getElementById('loadingSkeleton');
    if (skeleton) skeleton.classList.remove('visible');
}

function showPlaceholder() {
    const placeholder = document.getElementById('previewPlaceholder');
    if (placeholder) placeholder.classList.add('visible');
}

function hidePlaceholder() {
    const placeholder = document.getElementById('previewPlaceholder');
    if (placeholder) placeholder.classList.remove('visible');
}

function showImageDetectionOverlay() {
    const overlay = document.getElementById('imagePreviewOverlay');
    if (overlay) overlay.classList.remove('hidden');
}

function hideImageDetectionOverlay() {
    const overlay = document.getElementById('imagePreviewOverlay');
    if (overlay) overlay.classList.add('hidden');
}

// ===================================
// LOCAL STORAGE
// ===================================

function loadSettings() {
    const saved = localStorage.getItem('5xliving_pet_settings');
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
    localStorage.setItem('5xliving_pet_settings', JSON.stringify(settings));
}

// Save settings on unload
window.addEventListener('beforeunload', saveSettings);

// ===================================
// INITIALIZATION
// ===================================

function init() {
    loadSettings();
    initScene();
    setupUIControls();
    generatePet();
    addLog('Welcome to 5XLiving Universal 3D Model Maker!', 'success');
    addLog('Upload an image or select a preset to start', 'info');
}

// Start the app when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}
