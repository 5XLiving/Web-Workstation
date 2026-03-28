"""
Mesh generation and refinement routes
"""

from flask import Blueprint, request, jsonify, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from PIL import Image
import numpy as np
import trimesh
import json
import os
import io
import base64
from datetime import datetime

bp = Blueprint('mesh', __name__)

# Import user management from auth
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from routes.auth import load_users, save_users

def use_quota(email):
    """Decrement user quota"""
    users = load_users()
    if email not in users:
        return False
    
    user = users[email]
    
    # Reset daily quota if needed
    today = datetime.utcnow().date().isoformat()
    if user['quota']['last_reset'] != today:
        user['quota']['used_today'] = 0
        user['quota']['last_reset'] = today
    
    # Check quota
    if user['quota']['used_today'] >= user['quota']['daily_generations']:
        return False
    
    # Use quota
    user['quota']['used_today'] += 1
    users[email] = user
    save_users(users)
    
    return True

def generate_mesh_from_image(image_data, quality='high'):
    """
    Generate 3D mesh from 2D image using depth estimation
    This is a stub - replace with actual mesh generation algorithm
    (e.g., PIFu, NeRF, or custom depth-to-mesh pipeline)
    """
    
    # Decode base64 image
    try:
        if isinstance(image_data, str) and image_data.startswith('data:image'):
            # Remove data URL prefix
            image_data = image_data.split(',')[1]
        
        img_bytes = base64.b64decode(image_data)
        img = Image.open(io.BytesIO(img_bytes))
        img = img.convert('RGB')
    except Exception as e:
        raise ValueError(f"Invalid image data: {str(e)}")
    
    # Resize based on quality
    if quality == 'low':
        max_size = 256
        tri_limit = 512
    else:
        max_size = 512
        tri_limit = 4096
    
    img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
    
    # Convert to numpy array
    img_array = np.array(img)
    height, width = img_array.shape[:2]
    
    # STUB: Generate simple depth map from brightness
    # In production, use a proper depth estimation model
    gray = np.mean(img_array, axis=2) / 255.0
    depth_map = (gray - gray.min()) / (gray.max() - gray.min() + 1e-6)
    depth_map = depth_map * 0.5  # Scale depth
    
    # Generate mesh from depth map
    vertices = []
    faces = []
    colors = []
    
    step = max(1, max(height, width) // 64)  # Adaptive resolution
    
    for y in range(0, height - step, step):
        for x in range(0, width - step, step):
            # Sample depth and color
            z = depth_map[y, x]
            color = img_array[y, x] / 255.0
            
            # Create vertex (normalized coordinates)
            vx = (x / width) - 0.5
            vy = 0.5 - (y / height)
            vertices.append([vx, vy, z])
            colors.append(color)
    
    # Generate faces (triangles)
    cols = (width // step)
    rows = (height // step)
    
    for row in range(rows - 1):
        for col in range(cols - 1):
            idx = row * cols + col
            
            # Two triangles per quad
            faces.append([idx, idx + 1, idx + cols])
            faces.append([idx + 1, idx + cols + 1, idx + cols])
    
    # Create trimesh object
    vertices = np.array(vertices)
    faces = np.array(faces)
    colors = np.array(colors)
    
    # Limit triangle count
    if len(faces) > tri_limit:
        # Simple decimation: skip every nth face
        skip = len(faces) // tri_limit
        faces = faces[::skip]
    
    mesh = trimesh.Trimesh(vertices=vertices, faces=faces, vertex_colors=colors)
    
    # Basic cleanup
    mesh.remove_duplicate_faces()
    mesh.remove_degenerate_faces()
    
    return mesh

def refine_mesh(mesh_data, refinement_level='medium'):
    """
    Refine mesh V2 - smooth rough edges, fix topology
    """
    
    # Load mesh from GLB bytes
    try:
        mesh = trimesh.load(io.BytesIO(mesh_data), file_type='glb')
        
        # Handle scene vs single mesh
        if isinstance(mesh, trimesh.Scene):
            # Extract first mesh from scene
            meshes = list(mesh.geometry.values())
            if not meshes:
                raise ValueError("No mesh found in scene")
            mesh = meshes[0]
    except Exception as e:
        raise ValueError(f"Invalid mesh data: {str(e)}")
    
    # Apply refinement based on level
    if refinement_level == 'low':
        iterations = 1
    elif refinement_level == 'medium':
        iterations = 3
    else:  # high
        iterations = 5
    
    # Smooth using Laplacian smoothing
    for _ in range(iterations):
        # Simple Laplacian smoothing
        adjacency = mesh.vertex_adjacency_graph
        for i in range(len(mesh.vertices)):
            neighbors = list(adjacency[i])
            if neighbors:
                mesh.vertices[i] = np.mean(mesh.vertices[neighbors], axis=0)
    
    # Remove degenerate faces
    mesh.remove_degenerate_faces()
    mesh.remove_duplicate_faces()
    
    # Fix normals
    mesh.fix_normals()
    
    return mesh

@bp.route('/generate', methods=['POST'])
@jwt_required()
def generate():
    """Generate mesh V1 from image"""
    email = get_jwt_identity()
    
    # Check quota
    if not use_quota(email):
        return jsonify({'error': 'Daily quota exceeded. Upgrade to paid membership for more.'}), 429
    
    data = request.get_json()
    
    if not data or 'image' not in data:
        return jsonify({'error': 'Image data required'}), 400
    
    # Get quality based on membership
    users = load_users()
    quality = 'high' if users[email]['membership'] == 'paid' else 'low'
    
    try:
        # Generate mesh
        mesh = generate_mesh_from_image(data['image'], quality=quality)
        
        # Export to GLB
        output = io.BytesIO()
        mesh.export(output, file_type='glb')
        output.seek(0)
        glb_data = output.read()
        
        # Encode to base64
        glb_base64 = base64.b64encode(glb_data).decode('utf-8')
        
        return jsonify({
            'success': True,
            'mesh': glb_base64,
            'stats': {
                'vertices': len(mesh.vertices),
                'faces': len(mesh.faces),
                'quality': quality
            },
            'quota_remaining': users[email]['quota']['daily_generations'] - users[email]['quota']['used_today']
        })
        
    except Exception as e:
        return jsonify({'error': f'Mesh generation failed: {str(e)}'}), 500

@bp.route('/refine', methods=['POST'])
@jwt_required()
def refine():
    """Refine mesh V2 - smooth and fix topology"""
    email = get_jwt_identity()
    
    # Check quota (refinement also uses quota)
    if not use_quota(email):
        return jsonify({'error': 'Daily quota exceeded. Upgrade to paid membership for more.'}), 429
    
    data = request.get_json()
    
    if not data or 'mesh' not in data:
        return jsonify({'error': 'Mesh data required'}), 400
    
    # Get refinement level based on membership
    users = load_users()
    refinement_level = 'high' if users[email]['membership'] == 'paid' else 'low'
    
    try:
        # Decode mesh data
        mesh_bytes = base64.b64decode(data['mesh'])
        
        # Refine mesh
        refined_mesh = refine_mesh(mesh_bytes, refinement_level=refinement_level)
        
        # Export refined mesh
        output = io.BytesIO()
        refined_mesh.export(output, file_type='glb')
        output.seek(0)
        glb_data = output.read()
        
        # Encode to base64
        glb_base64 = base64.b64encode(glb_data).decode('utf-8')
        
        return jsonify({
            'success': True,
            'mesh': glb_base64,
            'stats': {
                'vertices': len(refined_mesh.vertices),
                'faces': len(refined_mesh.faces),
                'refinement_level': refinement_level
            },
            'quota_remaining': users[email]['quota']['daily_generations'] - users[email]['quota']['used_today']
        })
        
    except Exception as e:
        return jsonify({'error': f'Mesh refinement failed: {str(e)}'}), 500

@bp.route('/quota', methods=['GET'])
@jwt_required()
def quota():
    """Check user quota"""
    email = get_jwt_identity()
    users = load_users()
    
    if email not in users:
        return jsonify({'error': 'User not found'}), 404
    
    user = users[email]
    
    # Reset daily quota if needed
    today = datetime.utcnow().date().isoformat()
    if user['quota']['last_reset'] != today:
        user['quota']['used_today'] = 0
        user['quota']['last_reset'] = today
        users[email] = user
        save_users(users)
    
    return jsonify({
        'quota': user['quota'],
        'remaining': user['quota']['daily_generations'] - user['quota']['used_today'],
        'membership': user['membership']
    })
