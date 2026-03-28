"""
Placeholder asset generators for MVP testing
Generates simple PNG images and GLB meshes
"""
import os
import struct
import base64
from io import BytesIO
from typing import Tuple

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    Image = None
    ImageDraw = None
    ImageFont = None


def generate_placeholder_image(prompt: str = "placeholder", size: Tuple[int, int] = (512, 512)) -> bytes:
    """
    Generate a simple placeholder image with text
    
    Args:
        prompt: Text to display on image
        size: (width, height)
    
    Returns:
        PNG image bytes
    """
    if Image is None:
        # Fallback: return 1x1 pink pixel PNG
        return base64.b64decode(
            b'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8DwHwAFBQIAX8jx0gAAAABJRU5ErkJggg=='
        )
    
    # Create image with gradient
    img = Image.new('RGB', size, color=(240, 240, 240))
    draw = ImageDraw.Draw(img)
    
    # Draw gradient background
    for y in range(size[1]):
        brightness = int(200 + (y / size[1]) * 55)
        color = (brightness, brightness - 20, brightness + 20)
        draw.line([(0, y), (size[0], y)], fill=color)
    
    # Draw border
    border_color = (100, 100, 150)
    draw.rectangle([0, 0, size[0]-1, size[1]-1], outline=border_color, width=3)
    
    # Draw text
    try:
        # Try to load a font (may fail on some systems)
        font = ImageFont.truetype("arial.ttf", 30)
    except:
        font = ImageFont.load_default()
    
    text = f"Placeholder\n{prompt[:30]}"
    
    # Get text bounding box
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    # Center text
    x = (size[0] - text_width) // 2
    y = (size[1] - text_height) // 2
    
    draw.text((x, y), text, fill=(50, 50, 100), font=font)
    
    # Save to bytes
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    return buffer.getvalue()


def generate_placeholder_glb() -> bytes:
    """
    Generate a minimal GLB file (cube mesh)
    
    Returns:
        GLB binary data
    """
    # Minimal GLB with a cube
    # This is a simplified cube in glTF 2.0 binary format
    
    # Vertices for a unit cube
    vertices = [
        -0.5, -0.5, -0.5,  # 0
         0.5, -0.5, -0.5,  # 1
         0.5,  0.5, -0.5,  # 2
        -0.5,  0.5, -0.5,  # 3
        -0.5, -0.5,  0.5,  # 4
         0.5, -0.5,  0.5,  # 5
         0.5,  0.5,  0.5,  # 6
        -0.5,  0.5,  0.5,  # 7
    ]
    
    # Triangle indices
    indices = [
        0, 1, 2,  0, 2, 3,  # back
        4, 6, 5,  4, 7, 6,  # front
        0, 4, 5,  0, 5, 1,  # bottom
        2, 6, 7,  2, 7, 3,  # top
        0, 3, 7,  0, 7, 4,  # left
        1, 5, 6,  1, 6, 2,  # right
    ]
    
    # Convert to binary
    vertex_bytes = struct.pack(f'{len(vertices)}f', *vertices)
    index_bytes = struct.pack(f'{len(indices)}H', *indices)
    
    # Calculate buffer sizes
    vertex_buffer_size = len(vertex_bytes)
    index_buffer_size = len(index_bytes)
    
    # Align to 4-byte boundary
    def align4(size):
        return (size + 3) & ~3
    
    vertex_buffer_size_aligned = align4(vertex_buffer_size)
    index_buffer_size_aligned = align4(index_buffer_size)
    
    # Pad buffers
    vertex_bytes += b'\x00' * (vertex_buffer_size_aligned - vertex_buffer_size)
    index_bytes += b'\x00' * (index_buffer_size_aligned - index_buffer_size)
    
    # JSON chunk (glTF structure)
    gltf_json = {
        "asset": {"version": "2.0", "generator": "5XLiving Placeholder"},
        "scene": 0,
        "scenes": [{"nodes": [0]}],
        "nodes": [{"mesh": 0}],
        "meshes": [{
            "primitives": [{
                "attributes": {"POSITION": 0},
                "indices": 1,
                "mode": 4
            }]
        }],
        "accessors": [
            {
                "bufferView": 0,
                "componentType": 5126,
                "count": 8,
                "type": "VEC3",
                "max": [0.5, 0.5, 0.5],
                "min": [-0.5, -0.5, -0.5]
            },
            {
                "bufferView": 1,
                "componentType": 5123,
                "count": 36,
                "type": "SCALAR"
            }
        ],
        "bufferViews": [
            {
                "buffer": 0,
                "byteOffset": 0,
                "byteLength": vertex_buffer_size,
                "target": 34962
            },
            {
                "buffer": 0,
                "byteOffset": vertex_buffer_size_aligned,
                "byteLength": index_buffer_size,
                "target": 34963
            }
        ],
        "buffers": [{
            "byteLength": vertex_buffer_size_aligned + index_buffer_size_aligned
        }]
    }
    
    import json
    json_str = json.dumps(gltf_json, separators=(',', ':'))
    json_bytes = json_str.encode('utf-8')
    json_length = len(json_bytes)
    json_length_aligned = align4(json_length)
    json_bytes += b' ' * (json_length_aligned - json_length)
    
    # Binary buffer (BIN chunk)
    bin_data = vertex_bytes + index_bytes
    bin_length = len(bin_data)
    
    # GLB header
    magic = 0x46546C67  # "glTF"
    version = 2
    total_length = 12 + 8 + json_length_aligned + 8 + bin_length
    
    # Assemble GLB
    glb = struct.pack('<III', magic, version, total_length)
    
    # JSON chunk
    json_chunk_length = json_length_aligned
    json_chunk_type = 0x4E4F534A  # "JSON"
    glb += struct.pack('<II', json_chunk_length, json_chunk_type)
    glb += json_bytes
    
    # BIN chunk
    bin_chunk_length = bin_length
    bin_chunk_type = 0x004E4942  # "BIN\0"
    glb += struct.pack('<II', bin_chunk_length, bin_chunk_type)
    glb += bin_data
    
    return glb


def save_placeholder_image(filepath: str, prompt: str = "placeholder"):
    """Save placeholder image to file"""
    img_bytes = generate_placeholder_image(prompt)
    with open(filepath, 'wb') as f:
        f.write(img_bytes)


def save_placeholder_glb(filepath: str):
    """Save placeholder GLB to file"""
    glb_bytes = generate_placeholder_glb()
    with open(filepath, 'wb') as f:
        f.write(glb_bytes)


if __name__ == "__main__":
    # Test generation
    print("Generating placeholder assets...")
    
    os.makedirs("../static", exist_ok=True)
    
    save_placeholder_image("../static/placeholder_image.png", "Test Image")
    print("✓ Generated placeholder_image.png")
    
    save_placeholder_glb("../static/placeholder_mesh.glb")
    print("✓ Generated placeholder_mesh.glb")
    
    print("Done!")
