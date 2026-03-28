# 5XLiving Universal 3D Model Maker

**Create custom 3D models of pets, characters, vehicles, and objects - powered by AI**

A browser-based 3D model creator with AI-powered object detection. Upload a photo and get an instant 3D model, or customize every detail manually with intuitive sliders.

---

## ✨ Features

### 🤖 AI-Powered Detection (FULLY WORKING)
- Upload any image with working file picker
- Automatically detects object type using TensorFlow.js MobileNet
- Maps 40+ object classes to 12 model presets
- Real-time preview with confidence percentage
- Works entirely in your browser (no server needed)
- Graceful fallback if AI unavailable

### 🎨 12 Model Presets (ALL FUNCTIONAL)
1. **Dog** - Floppy ears, medium snout, long tail (animal generator)
2. **Cat** - Pointy ears, short snout, very long tail (animal generator)
3. **Fox** - Large pointy ears, long snout, bushy tail (animal generator)
4. **Bird** - Wings (earSize), beak (snoutLength), short legs (animal generator)
5. **Fish** - Fins (earSize), no legs, curved tail (animal generator)
6. **Rabbit** - Huge ears, tiny tail, short legs (animal generator)
7. **Human** - ✨ NEW: Humanoid with torso, head, arms, legs (humanoid generator)
8. **Car** - ✨ NEW: Body + 4 wheels + headlights (car generator)
9. **House** - ✨ NEW: Walls + pyramid roof + door/windows (house generator)
10. **Tree** - ✨ NEW: Trunk + foliage canopy + clusters (tree generator)
11. **Robot** - ✨ NEW: Metallic humanoid with antenna + glowing eyes (robot generator)
12. **Custom** - Start from scratch with default parameters

### 🎛️ Full Customization
- **8 adjustment sliders**: Body size, length, head size, snout length, ear size, leg length, tail length, eye size
- **3 color pickers**: Body color, accent color, eye color
- **Real-time preview**: See changes instantly in the 3D viewport (NO DISAPPEARING)
- **Randomize button**: Generate surprising combinations
- **Stable rendering**: Model NEVER disappears after generation

### 📦 Export & Save
- Export to GLB format (compatible with Blender, Unity, Unreal Engine)
- Accurate stats: Triangle count, mesh count, bounding box dimensions
- Save/load custom presets as JSON
- Take screenshots (preserveDrawingBuffer enabled)
- Free tier: 1 export per session
- VIP tier: Unlimited exports

---

## 🚀 Quick Start

1. **Open `index.html` in a modern browser**
2. **Upload an image** or **select a preset**
3. **Customize** with sliders and colors
4. **Export** your 3D model as GLB

No installation, no account, no backend server required!

---

## 🧠 How AI Detection Works

The app uses **TensorFlow.js 4.20.0** with the **MobileNet 2.1.1** model:

### Detection Flow
1. Click "Upload Image" → File picker opens
2. Select image → Preview displays in overlay
3. MobileNet analyzes image (lazy-loads on first upload)
4. Shows result: "AI detected: [className] (XX% confidence)"
5. Maps result to preset via comprehensive keyword matching
6. Click "Generate Model" → Creates 3D model from detected type

### Mapping Examples
- **Dogs**: "Labrador retriever", "German shepherd", "poodle" → `dog` preset
- **Cats**: "tabby cat", "Persian cat", "kitten" → `cat` preset
- **People**: "person", "human", "man", "woman" → `human` preset
- **Vehicles**: "sports car", "truck", "van" → `car` preset
- **Buildings**: "house", "cottage", "mansion" → `house` preset
- **Plants**: "oak tree", "pine tree", "palm" → `tree` preset
- **Unknown**: Falls back to `custom` preset with manual selection prompt

**All processing happens in your browser** - your images never leave your device!

---

## 🎮 Controls

### Camera
- **Left mouse drag**: Rotate view (OrbitControls)
- **Right mouse drag**: Pan
- **Mouse wheel**: Zoom in/out
- **Reset Camera button**: Return to default position
- **Damping enabled**: Smooth camera movement

### Model Editing
- Adjust sliders to change proportions (instant updates)
- Pick colors for different parts (body, accent, eyes)
- Click preset buttons to load templates
- Use randomize for creative inspiration
- Toggle grid/axis helpers for precision

---

## 💾 Tech Stack

### Core Technologies
- **Three.js 0.160.0** - 3D rendering engine
- **TensorFlow.js 4.20.0** - Machine learning runtime
- **MobileNet 2.1.1** - Image classification model
- **OrbitControls** - Camera interaction
- **GLTFExporter** - Binary GLB export

### Architecture
- **Vanilla JavaScript** (no frameworks, no build tools)
- **CSS Variables** (Bazi.html matching theme)
- **FileReader API** (client-side image upload)
- **LocalStorage** (settings persistence)
- **Canvas API** (screenshot capture)

### Design
- Dark theme (#0b0f14 background)
- Gold accents (#d4af37)
- Noto Serif SC fonts
- Responsive grid layout
- Floating cards with backdrop blur

---

## 🔧 Technical Details

### Stable Render Loop (FIXED)
```javascript
function startAnimationLoop() {
    function animate() {
        animationFrameId = requestAnimationFrame(animate);
        resizeRendererToDisplaySize(); // ← Prevents disappearing models
        controls.update();
        renderer.render(scene, camera);
    }
    animate();
}
```

### Safe Model Rebuild
```javascript
function clearModelGroup() {
    // Dispose geometries and materials properly
    while (modelGroup.children.length > 0) {
        const child = modelGroup.children[0];
        if (child.geometry) child.geometry.dispose();
        if (child.material) child.material.dispose();
        modelGroup.remove(child);
    }
}
```

### Generator Dispatch
- `human` → `generateHumanoid()` (torso, head, 2 arms, 2 legs)
- `car` → `generateCar()` (body, cabin, 4 wheels, headlights)
- `house` → `generateHouse()` (walls, roof, door, windows)
- `tree` → `generateTree()` (trunk, foliage, clusters)
- `robot` → `generateRobot()` (metallic body, glowing eyes, antenna)
- Others → `generateAnimal()` (body, head, ears, legs, tail)

---

## 📱 Browser Support

### Minimum Requirements
- WebGL support (required for Three.js)
- ES6 support (arrow functions, classes, const/let)
- FileReader API (for image upload)

### Tested Browsers
- ✅ Chrome/Edge 90+ (recommended)
- ✅ Firefox 88+
- ✅ Safari 14+
- ✅ Mobile Chrome/Safari (WebGL enabled)

### Known Issues
- Safari may require HTTPS for TensorFlow.js
- Older browsers need WebGL 1.0 minimum

---

## 🔒 Privacy & Security

- **100% client-side**: No data sent to servers
- **No tracking**: No analytics, cookies, or fingerprinting
- **No account required**: Use immediately without registration
- **Your images stay local**: AI runs entirely in your browser
- **No telemetry**: Zero data collection

---

## 📊 Stats & Export

### Real-Time Stats
- **Triangle count**: Calculated from geometry.index.count / 3
- **Mesh count**: Number of THREE.Mesh objects in modelGroup
- **Bounding box**: Width × Height × Depth in meters
- Updates automatically after each generation

### GLB Export
- Binary format (.glb)
- Includes all meshes, materials, and colors
- Compatible with: Blender, Unity, Unreal Engine, Sketchfab, etc.
- Timestamped filenames: `5xLiving_[type]_[timestamp].glb`

---

## 🧪 Testing

Open `TEST.html` in your browser to run automated tests:
- ✅ Dependency check (Three.js, TensorFlow.js, MobileNet)
- ✅ Scene initialization
- ✅ Generator validation
- ✅ AI detection simulation
- ✅ Browser compatibility

---

## 📝 Files

- `index.html` - Main application page
- `app.js` - **FULLY REWRITTEN** - Core application logic (1043 lines)
- `styles.css` - Bazi.html matching styles (873 lines)
- `README.md` - This documentation
- `FIXES_AND_UPGRADES.md` - Detailed changelog
- `TEST.html` - Automated test suite

---

## 🆕 What's New (Latest Version)

### ✅ FIXED
1. **Render loop crash** - Models no longer disappear after 1 frame
2. **Image upload** - File picker now opens and previews images correctly
3. **AI detection** - TensorFlow.js MobileNet fully integrated
4. **Stats calculation** - Accurate triangle/mesh counts
5. **Memory leaks** - Proper geometry/material disposal

### ✨ NEW FEATURES
1. **Humanoid generator** - Creates people with arms, legs, torso, head
2. **Car generator** - Body + 4 wheels + headlights
3. **House generator** - Walls + pyramid roof + door/windows
4. **Tree generator** - Trunk + foliage with clusters
5. **Robot generator** - Metallic humanoid with antenna + glowing eyes

### 🔄 REFACTORED
- Renamed `petGroup` → `modelGroup` (universal naming)
- Implemented safe `clearModelGroup()` disposal pattern
- Added `resizeRendererToDisplaySize()` stability fix
- Comprehensive error logging in animation loop

---

## 🛠️ Development

Built with love using modern web technologies. Pure vanilla JavaScript - no build tools or frameworks required.

**Want to contribute?**  
The codebase is clean and well-commented. Feel free to fork and enhance!

---

## 📄 License

Free to use for personal and commercial projects. Attribution appreciated but not required.

---

**Made with ❤️ by 5XLiving**  
**v2.0 - Universal Model Maker with AI Detection**
