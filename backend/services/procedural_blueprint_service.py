import random


def create_base_blueprint(asset_type="humanoid_mech"):
    if asset_type != "humanoid_mech":
        return {
            "asset_type": asset_type,
            "style": "generic",
            "parts": {}
        }

    return {
        "asset_type": "humanoid_mech",
        "style": "base_mech",
        "parts": {
            "torso": {
                "shape": "armor_box",
                "scale": [0.62, 0.34, 0.28],
                "position": [0, 1.18, 0],
                "material_zone": "dark_metal"
            },

            "waist": {
                "shape": "waist_ring",
                "scale": [0.34, 0.14, 0.22],
                "position": [0, 0.82, 0],
                "material_zone": "dark_metal"
            },

            "head": {
                "shape": "helmet_sphere",
                "scale": [0.20, 0.22, 0.18],
                "position": [0, 1.76, 0],
                "material_zone": "dark_metal"
            },

            "left_shoulder": {
                "shape": "shoulder_pad",
                "scale": [0.22, 0.16, 0.22],
                "position": [-0.52, 1.30, 0],
                "material_zone": "dark_metal"
            },

            "right_shoulder": {
                "shape": "shoulder_pad",
                "scale": [0.22, 0.16, 0.22],
                "position": [0.52, 1.30, 0],
                "material_zone": "dark_metal"
            }
        }
    }
