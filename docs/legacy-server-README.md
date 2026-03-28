# 5XLiving 3D Maker - Flask Backend (MVP)

Simple Flask API for 3D character generation with job queue and placeholder responses.

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd server
pip install -r requirements.txt
```

### 2. Run Server

```bash
python app.py
```

Server runs on `http://localhost:5000`

## 📡 API Endpoints

### Authentication

#### `POST /api/auth/verify`
Verify token and get plan quota information.

**Request:**
```json
{
  "token": "FREE" | "YEAR" | "VIP"
}
```

**Response:**
```json
{
  "ok": true,
  "plan": "free",
  "dailyRemaining": {
    "image": 1,
    "v1": 1,
    "v2": 0
  }
}
```

**Token Types (MVP):**
- `"FREE"` → free plan
- `"YEAR"` → year plan
- `"VIP"` → vip plan

---

### Image Generation

#### `POST /api/image/generate`
Generate AI image from text prompt (returns placeholder in MVP).

**Request:**
```json
{
  "token": "FREE",
  "prompt": "cute dog sitting",
  "style": "realistic",
  "aspect": "1:1"
}
```

**Response:**
```json
{
  "jobId": "a1b2c3d4-...",
  "status": "queued"
}
```

---

### Mesh Generation

#### `POST /api/mesh/generate`
Generate mesh V1 from image.

**Request:**
```json
{
  "token": "FREE",
  "imageDataUrl": "data:image/png;base64,...",
  "species": "dog",
  "meshTier": "v1",
  "options": {}
}
```

**Response:**
```json
{
  "jobId": "e5f6g7h8-...",
  "status": "queued"
}
```

---

### Mesh Refinement

#### `POST /api/mesh/refine`
Refine mesh V1 to V2 (higher quality).

**Request:**
```json
{
  "token": "YEAR",
  "meshUrl": "http://localhost:5000/static/placeholder_mesh.glb",
  "refine": {
    "smoothness": 0.7,
    "removeNoise": true,
    "preserveSilhouette": true
  }
}
```

**Response:**
```json
{
  "jobId": "i9j0k1l2-...",
  "status": "queued"
}
```

---

### Job Status

#### `GET /api/jobs/<jobId>`
Get job progress and result.

**Response:**
```json
{
  "status": "done",
  "progress": 100,
  "result": {
    "imageUrl": "/static/placeholder_image.png",
    "meshUrl": "/static/placeholder_mesh.glb"
  }
}
```

**Status Values:**
- `"queued"` - Job waiting to start
- `"running"` - Job in progress
- `"done"` - Job completed successfully
- `"error"` - Job failed

---

## 📊 Quota Limits

| Plan | Image/Day | V1 Mesh/Day | V2 Mesh/Day |
|------|-----------|-------------|-------------|
| Free | 1 | 1 | 0 |
| Year | 10 | 10 | 5 |
| VIP | 50 | 50 | 25 |

Quotas reset daily at midnight UTC.

---

## 🔧 Development

### Project Structure

```
server/
├── app.py                   # Main Flask application
├── requirements.txt         # Python dependencies
├── services/
│   ├── __init__.py
│   ├── quota.py            # Quota management
│   ├── jobs.py             # Job queue system
│   └── placeholders.py     # Placeholder generators
├── static/
│   ├── placeholder_image.png   # Placeholder image
│   └── placeholder_mesh.glb    # Placeholder mesh (cube)
└── uploads/                # Temporary upload storage
```

### Testing with cURL

**Verify Token:**
```bash
curl -X POST http://localhost:5000/api/auth/verify \
  -H "Content-Type: application/json" \
  -d '{"token":"FREE"}'
```

**Generate Image:**
```bash
curl -X POST http://localhost:5000/api/image/generate \
  -H "Content-Type: application/json" \
  -d '{"token":"FREE","prompt":"a cute dog"}'
```

**Check Job Status:**
```bash
curl http://localhost:5000/api/jobs/<jobId>
```

### Admin Endpoints (Debug)

- `GET /api/admin/quota/<token>` - View quota usage
- `GET /api/admin/jobs` - List all jobs

### Background Tasks

- **Cleanup Thread**: Runs hourly to remove old quota data and completed jobs

---

## 🏗️ MVP Implementation Notes

### Current Status

✅ **Implemented:**
- Token-based auth (FREE/YEAR/VIP)
- Quota system with daily limits
- Job queue with progress simulation
- Placeholder image/mesh generation
- CORS enabled for local dev

⏸️ **Production TODO:**
- Replace placeholders with real AI models:
  - Image: Stable Diffusion API
  - Mesh V1: PIFu or NeRF
  - Mesh V2: Laplacian smoothing + remeshing
- Add database (PostgreSQL) for persistent storage
- Add Redis for job queue
- Add Celery for async processing
- Add authentication system (OAuth/JWT)
- Add payment integration (Stripe)
- Add rate limiting middleware
- Add logging and monitoring

### Placeholder Behavior

**Image Generation:**
- Returns gradient PNG with text overlay
- Simulates 2-second processing time

**Mesh Generation:**
- Returns simple cube GLB (8 vertices, 12 triangles)
- Simulates 2-second processing time
- V1 and V2 return same mesh (different in production)

**Job Processing:**
- Jobs complete in ~2 seconds
- Progress updates: 10% → 30% → 60% → 90% → 100%
- Jobs stored in memory (cleared after 24 hours)

---

## 🐛 Troubleshooting

### Server won't start
```bash
# Check Python version (3.8+)
python --version

# Reinstall dependencies
pip install -r requirements.txt

# Check port 5000 is available
netstat -ano | findstr :5000
```

### CORS errors
- Ensure frontend runs on allowed origins (localhost:8000, localhost:5500)
- Check browser console for details
- Use `http://` not `file://` for local testing

### Quota exceeded
- Use admin endpoint to check usage: `/api/admin/quota/FREE`
- Quotas reset daily at midnight UTC
- For testing, restart server to clear in-memory data

---

## 📝 License

MIT

---

## 🔗 Related Docs

- [API Integration Guide](../API_INTEGRATION_GUIDE.md)
- [Implementation Status](../IMPLEMENTATION_STATUS.md)
- [Quick Reference](../QUICK_REFERENCE.md)
