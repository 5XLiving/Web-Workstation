"""
AI image generation routes (optional)
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
import base64
import io
import os
from PIL import Image
import numpy as np

bp = Blueprint('ai', __name__)

# Import user management
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from routes.auth import load_users

def generate_placeholder_image(prompt, size=(512, 512)):
    """
    Generate placeholder image for AI generation
    In production, integrate with:
    - Stable Diffusion
    - DALL-E API
    - Midjourney API
    - Custom diffusion model
    """
    
    # Create random colored image as placeholder
    np.random.seed(hash(prompt) % (2**32))
    
    # Generate gradient based on prompt
    img_array = np.zeros((size[1], size[0], 3), dtype=np.uint8)
    
    # Extract color hint from prompt
    colors = {
        'red': [255, 100, 100],
        'blue': [100, 100, 255],
        'green': [100, 255, 100],
        'yellow': [255, 255, 100],
        'orange': [255, 165, 0],
        'purple': [200, 100, 255],
        'pink': [255, 150, 200],
        'brown': [165, 100, 50]
    }
    
    # Default color
    base_color = [150, 150, 150]
    
    # Check for color keywords
    prompt_lower = prompt.lower()
    for color_name, color_value in colors.items():
        if color_name in prompt_lower:
            base_color = color_value
            break
    
    # Generate gradient
    for y in range(size[1]):
        for x in range(size[0]):
            brightness = 0.5 + 0.5 * (y / size[1])
            img_array[y, x] = [
                int(base_color[0] * brightness),
                int(base_color[1] * brightness),
                int(base_color[2] * brightness)
            ]
    
    # Add some noise for texture
    noise = np.random.randint(-30, 30, img_array.shape, dtype=np.int16)
    img_array = np.clip(img_array + noise, 0, 255).astype(np.uint8)
    
    img = Image.fromarray(img_array)
    
    return img

@bp.route('/generate-image', methods=['POST'])
@jwt_required()
def generate_image():
    """Generate image from text prompt (AI)"""
    email = get_jwt_identity()
    users = load_users()
    
    if email not in users:
        return jsonify({'error': 'User not found'}), 404
    
    data = request.get_json()
    
    if not data or 'prompt' not in data:
        return jsonify({'error': 'Prompt required'}), 400
    
    prompt = data['prompt']
    
    # Size based on membership
    if users[email]['membership'] == 'paid':
        size = (512, 512)
    else:
        size = (256, 256)
    
    try:
        # Generate image (placeholder for now)
        img = generate_placeholder_image(prompt, size=size)
        
        # Convert to base64
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        img_base64 = base64.b64encode(buffer.read()).decode('utf-8')
        
        return jsonify({
            'success': True,
            'image': f'data:image/png;base64,{img_base64}',
            'prompt': prompt,
            'size': size,
            'note': 'This is a placeholder. Integrate with Stable Diffusion or DALL-E for production.'
        })
        
    except Exception as e:
        return jsonify({'error': f'Image generation failed: {str(e)}'}), 500

@bp.route('/status', methods=['GET'])
def status():
    """Check AI service status"""
    return jsonify({
        'available': True,
        'status': 'placeholder',
        'note': 'Integrate with Stable Diffusion or DALL-E API for production',
        'supported_models': ['placeholder', 'stable-diffusion (TODO)', 'dall-e (TODO)']
    })
