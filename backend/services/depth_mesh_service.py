from pathlib import Path
from PIL import Image


def generate_depth_mesh(image_path: str, output_dir: str, size: int = 160, depth: float = 0.9):
    image_path = Path(image_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    img = Image.open(image_path).convert("RGBA")
    img.thumbnail((size, size), Image.LANCZOS)

    w, h = img.size
    pixels = img.load()

    obj_path = output_dir / "mesh.obj"
    mtl_path = output_dir / "mesh.mtl"
    tex_path = output_dir / "texture.png"

    img.save(tex_path)

    vertices = []
    uvs = []
    faces = []
    index_map = {}

    def alpha_at(x, y):
        return pixels[x, y][3] / 255.0

    for y in range(h):
        for x in range(w):
            if alpha_at(x, y) > 0.05:
                z = alpha_at(x, y) * depth
                vx = (x / max(1, w - 1)) - 0.5
                vy = 0.5 - (y / max(1, h - 1))
                vertices.append((vx, vy, z))
                uvs.append((x / max(1, w - 1), 1 - y / max(1, h - 1)))
                index_map[(x, y)] = len(vertices)

    for y in range(h - 1):
        for x in range(w - 1):
            keys = [(x, y), (x + 1, y), (x + 1, y + 1), (x, y + 1)]
            if all(k in index_map for k in keys):
                faces.append(tuple(index_map[k] for k in keys))

    with open(mtl_path, "w", encoding="utf-8") as f:
        f.write("newmtl material0\n")
        f.write("Ka 1.000 1.000 1.000\n")
        f.write("Kd 1.000 1.000 1.000\n")
        f.write("Ks 0.000 0.000 0.000\n")
        f.write("d 1.0\n")
        f.write("illum 2\n")
        f.write("map_Kd texture.png\n")

    with open(obj_path, "w", encoding="utf-8") as f:
        f.write("mtllib mesh.mtl\n")
        f.write("usemtl material0\n")

        for v in vertices:
            f.write(f"v {v[0]} {v[1]} {v[2]}\n")

        for uv in uvs:
            f.write(f"vt {uv[0]} {uv[1]}\n")

        for face in faces:
            a, b, c, d = face
            f.write(f"f {a}/{a} {b}/{b} {c}/{c}\n")
            f.write(f"f {a}/{a} {c}/{c} {d}/{d}\n")

    return {
        "obj": str(obj_path),
        "mtl": str(mtl_path),
        "texture": str(tex_path),
        "vertices": len(vertices),
        "faces": len(faces) * 2,
    }
