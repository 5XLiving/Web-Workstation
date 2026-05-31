def choose_preset(ai_result: dict) -> dict:
    object_type = ai_result.get("object_type", "generic_prop")
    avg_color = ai_result.get("avg_color", [180, 180, 180])

    base_material = {
        "base_color": avg_color,
        "roughness": 0.85,
        "metallic": 0.0
    }

    if object_type == "transport_ground":
        return {
            "preset_name": "auto_ground_vehicle",
            "asset_type": "transport_ground",
            "parts": [
                {
                    "name": "main_chassis",
                    "shape": "box",
                    "position": [0, 0.7, 0],
                    "scale": [3.2, 0.6, 1.4],
                    "material": base_material
                },
                {
                    "name": "cabin",
                    "shape": "box",
                    "position": [0.4, 1.25, 0],
                    "scale": [1.4, 0.8, 1.1],
                    "material": base_material
                },
                {
                    "name": "wheel_fl",
                    "shape": "cylinder",
                    "position": [1.0, 0.25, 0.8],
                    "scale": [0.35, 0.35, 0.25],
                    "material": {"base_color": [20, 20, 20]}
                },
                {
                    "name": "wheel_fr",
                    "shape": "cylinder",
                    "position": [1.0, 0.25, -0.8],
                    "scale": [0.35, 0.35, 0.25],
                    "material": {"base_color": [20, 20, 20]}
                },
                {
                    "name": "wheel_bl",
                    "shape": "cylinder",
                    "position": [-1.0, 0.25, 0.8],
                    "scale": [0.35, 0.35, 0.25],
                    "material": {"base_color": [20, 20, 20]}
                },
                {
                    "name": "wheel_br",
                    "shape": "cylinder",
                    "position": [-1.0, 0.25, -0.8],
                    "scale": [0.35, 0.35, 0.25],
                    "material": {"base_color": [20, 20, 20]}
                }
            ]
        }

    if object_type == "tree":
        return {
            "preset_name": "auto_tree",
            "asset_type": "tree",
            "parts": [
                {
                    "name": "trunk",
                    "shape": "cylinder",
                    "position": [0, 0.8, 0],
                    "scale": [0.25, 1.2, 0.25],
                    "material": {"base_color": [110, 70, 35]}
                },
                {
                    "name": "leaf_mass",
                    "shape": "sphere",
                    "position": [0, 2.0, 0],
                    "scale": [1.0, 1.0, 1.0],
                    "material": base_material
                }
            ]
        }

    if object_type in ["building", "building_tower"]:
        h = 3.2 if object_type == "building_tower" else 1.8
        return {
            "preset_name": "auto_building",
            "asset_type": "building",
            "parts": [
                {
                    "name": "main_block",
                    "shape": "box",
                    "position": [0, h / 2, 0],
                    "scale": [1.8, h, 1.8],
                    "material": base_material
                },
                {
                    "name": "roof",
                    "shape": "cone",
                    "position": [0, h + 0.45, 0],
                    "scale": [1.35, 0.7, 1.35],
                    "material": {"base_color": [90, 60, 45]}
                }
            ]
        }

    return {
        "preset_name": "auto_generic_prop",
        "asset_type": "generic_prop",
        "parts": [
            {
                "name": "main_body",
                "shape": "box",
                "position": [0, 0.6, 0],
                "scale": [1.2, 1.2, 1.2],
                "material": base_material
            }
        ]
    }