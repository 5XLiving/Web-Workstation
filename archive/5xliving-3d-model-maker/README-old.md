# 5XLiving • Universal 3D Model Maker

> **AI-Powered 3D Model Generator** — Upload any image to detect objects and generate procedural 3D models, or choose from 12+ presets. Export as .glb for Unity, Unreal, Blender, and more.

---

## ✨ Features

### 🤖 **AI Image Detection**
- Upload any photo and auto-detect objects (animals, vehicles, buildings, etc.)
- Color analysis identifies dominant tones
- Edge detection recognizes geometric vs organic shapes
- Confidence scoring shows detection accuracy (50-80% typical)

### 🎨 **12 Model Presets**
🐕 Dog • 🐈 Cat • 🦊 Fox • 🐦 Bird • 🐟 Fish • 🐰 Rabbit • 🚗 Car • 🏠 House • 🌲 Tree • 🧍 Human • 🤖 Robot • ✨ Custom

---

## 🚀 Quick Start

### **Upload Image (AI Detection)**
1. Click **"📷 Upload Image to Detect"**
2. Select photo from device
3. Review AI detection result
4. Click **"✨ Generate Model"**

### **Manual Preset**
1. Click any preset button
2. Model generates instantly
3. Fine-tune with sliders

---

## 🎛️ Controls

- **Core Shape** - Body scale, length, height
- **Detail Parts** - Head, extensions, side parts
- **Colors** - Body, accent, details
- **Randomize** - Seeded random generation

---

## 📦 Export

- **Download .glb** - Universal 3D format
- **Save Preset** - Export settings as JSON
- **Screenshot** - Capture PNG image

Compatible with Unity, Unreal Engine, Blender, Three.js

---

## 🧠 How AI Works

Browser-based computer vision (no server):
- **Color Analysis** - RGB pattern matching
- **Edge Detection** - Geometric structure
- **Brightness** - Lighting distribution
- **Scoring** - Multi-factor confidence

Examples:
- Brown/tan → Dog
- Green → Tree
- High edges → Vehicles
- Skin tones → Human

---

## 🛠️ Tech Stack

- Three.js 0.160.0
- OrbitControls
- GLTFExporter
- Canvas API for image analysis
- Pure vanilla JS (no frameworks)

---

Made with ❤️ by **5XLiving**
