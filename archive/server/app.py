"""
Flask backend for 5XLiving 3D Maker
MVP implementation with job queue and placeholder responses
"""
import os
import threading
import time
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

# Import services
from services import (
    get_plan_from_token,
    get_remaining_quota,
    consume_quota,
    cleanup_old_dates,
    get_usage_stats,
    create_job,
    get_job,
    cleanup_old_jobs,
    JobStatus
)

# Initialize Flask app
app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max upload

# Enable CORS for local development
CORS(app, origins=[
    'http://localhost:8000',
    'http://127.0.0.1:8000',
    'http://localhost:5500',
    'http://127.0.0.1:5500',
    'http://localhost:3000',
    'http://127.0.0.1:3000'
])

# Create necessary directories
os.makedirs('static', exist_ok=True)
os.makedirs('uploads', exist_ok=True)


# ============================================================
# CLEANUP BACKGROUND THREAD
# ============================================================
def cleanup_worker():
    """Background thread to clean up old data periodically"""
    while True:
        time.sleep(3600)  # Run every hour
        cleanup_old_dates()  # Clean quota data
        cleanup_old_jobs(24)  # Clean jobs older than 24 hours


# Start cleanup thread
cleanup_thread = threading.Thread(target=cleanup_worker, daemon=True)
cleanup_thread.start()


# ============================================================
# STATIC FILE SERVING
# ============================================================
@app.route('/static/<path:filename>')
def serve_static(filename):
    """Serve static files (placeholder assets)"""
    return send_from_directory('static', filename)


# ============================================================
# HEALTH CHECK
# ============================================================
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'service': '5XLiving 3D Maker API',
        'version': '2.0.0-mvp'
    })


# ============================================================
# 1) POST /api/auth/verify
# ============================================================
@app.route('/api/auth/verify', methods=['POST'])
def verify_token():
    """
    Verify token and return plan + quota info
    
    Request: { "token": "FREE" | "YEAR" | "VIP" }
    Response: { "ok": bool, "plan": str, "dailyRemaining": {...} }
    """
    data = request.get_json()
    
    if not data or 'token' not in data:
        return jsonify({
            'ok': False,
            'error': 'Missing token field'
        }), 400
    
    token = data['token']
    
    # Get plan from token
    plan = get_plan_from_token(token)
    
    # Get remaining quota
    remaining = get_remaining_quota(token, plan)
    
    return jsonify({
        'ok': True,
        'plan': plan,
        'dailyRemaining': remaining
    })


# ============================================================
# 2) POST /api/image/generate
# ============================================================
@app.route('/api/image/generate', methods=['POST'])
def generate_image():
    """
    Generate image from prompt (AI stub)
    
    Request: { "token": str, "prompt": str, "style": str, "aspect": str }
    Response: { "jobId": str, "status": "queued" }
    """
    data = request.get_json()
    
    if not data or 'token' not in data:
        return jsonify({'error': 'Missing token'}), 400
    
    token = data['token']
    prompt = data.get('prompt', 'a 3D character')
    style = data.get('style', 'realistic')
    aspect = data.get('aspect', '1:1')
    
    # Check quota
    success, error_msg = consume_quota(token, 'image')
    if not success:
        return jsonify({
            'error': error_msg,
            'quotaExceeded': True
        }), 429
    
    # Create job
    job_id = create_job('image', {
        'token': token,
        'prompt': prompt,
        'style': style,
        'aspect': aspect
    })
    
    return jsonify({
        'jobId': job_id,
        'status': 'queued'
    })


# ============================================================
# 3) POST /api/mesh/generate
# ============================================================
@app.route('/api/mesh/generate', methods=['POST'])
def generate_mesh():
    """
    Generate mesh V1 from image
    
    Request: { 
        "token": str,
        "imageDataUrl": str OR "imageUrl": str,
        "species": str,
        "meshTier": "v1",
        "options": {}
    }
    Response: { "jobId": str, "status": "queued" }
    """
    data = request.get_json()
    
    if not data or 'token' not in data:
        return jsonify({'error': 'Missing token'}), 400
    
    token = data['token']
    image_data = data.get('imageDataUrl') or data.get('imageUrl')
    species = data.get('species', 'dog')
    mesh_tier = data.get('meshTier', 'v1')
    options = data.get('options', {})
    
    if not image_data:
        return jsonify({'error': 'Missing imageDataUrl or imageUrl'}), 400
    
    # Check quota (v1)
    success, error_msg = consume_quota(token, 'v1')
    if not success:
        return jsonify({
            'error': error_msg,
            'quotaExceeded': True
        }), 429
    
    # Create job
    job_id = create_job('mesh_v1', {
        'token': token,
        'imageData': image_data[:100] + '...',  # Store truncated for memory
        'species': species,
        'meshTier': mesh_tier,
        'options': options
    })
    
    return jsonify({
        'jobId': job_id,
        'status': 'queued'
    })


# ============================================================
# 4) POST /api/mesh/refine
# ============================================================
@app.route('/api/mesh/refine', methods=['POST'])
def refine_mesh():
    """
    Refine mesh V1 -> V2
    
    Request: {
        "token": str,
        "meshUrl": str,
        "refine": {
            "smoothness": float,
            "removeNoise": bool,
            "preserveSilhouette": bool
        }
    }
    Response: { "jobId": str, "status": "queued" }
    """
    data = request.get_json()
    
    if not data or 'token' not in data:
        return jsonify({'error': 'Missing token'}), 400
    
    token = data['token']
    mesh_url = data.get('meshUrl')
    refine_options = data.get('refine', {})
    
    if not mesh_url:
        return jsonify({'error': 'Missing meshUrl'}), 400
    
    # Check quota (v2)
    success, error_msg = consume_quota(token, 'v2')
    if not success:
        return jsonify({
            'error': error_msg,
            'quotaExceeded': True
        }), 429
    
    # Create job
    job_id = create_job('mesh_v2', {
        'token': token,
        'meshUrl': mesh_url,
        'refine': refine_options
    })
    
    return jsonify({
        'jobId': job_id,
        'status': 'queued'
    })


# ============================================================
# 5) GET /api/jobs/<jobId>
# ============================================================
@app.route('/api/jobs/<job_id>', methods=['GET'])
def get_job_status(job_id):
    """
    Get job status and result
    
    Response: {
        "status": "queued" | "running" | "done" | "error",
        "progress": 0-100,
        "result": { "imageUrl"?: str, "meshUrl"?: str },
        "error"?: str
    }
    """
    job = get_job(job_id)
    
    if not job:
        return jsonify({'error': 'Job not found'}), 404
    
    # Return job data (exclude internal params)
    response = {
        'status': job['status'],
        'progress': job['progress'],
        'result': job.get('result', {}),
    }
    
    if job.get('error'):
        response['error'] = job['error']
    
    return jsonify(response)


# ============================================================
# ADMIN/DEBUG ENDPOINTS (optional)
# ============================================================
@app.route('/api/admin/quota/<token>', methods=['GET'])
def get_quota_info(token):
    """Get quota usage stats for a token (debug)"""
    stats = get_usage_stats(token)
    return jsonify(stats)


@app.route('/api/admin/jobs', methods=['GET'])
def list_all_jobs():
    """List all jobs (debug)"""
    from services.jobs import get_all_jobs
    jobs = get_all_jobs()
    return jsonify({'jobs': jobs, 'count': len(jobs)})


# ============================================================
# ERROR HANDLERS
# ============================================================
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500


# ============================================================
# MAIN
# ============================================================
if __name__ == '__main__':
    print('=' * 50)
    print('>> 5XLiving 3D Maker API (MVP)')
    print('=' * 50)
    print('Server: http://localhost:5000')
    print('Health: http://localhost:5000/health')
    print()
    print('Endpoints:')
    print('  POST /api/auth/verify')
    print('  POST /api/image/generate')
    print('  POST /api/mesh/generate')
    print('  POST /api/mesh/refine')
    print('  GET  /api/jobs/<jobId>')
    print()
    print('Test tokens: FREE, YEAR, VIP')
    print('Press Ctrl+C to stop')
    print('=' * 50)
    app.run(debug=True, host='0.0.0.0', port=5000)
