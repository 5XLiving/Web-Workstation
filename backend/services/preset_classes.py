"""
Preset class definitions for image-to-3D inference.

Each class provides prior assumptions about structure, depth ratio,
symmetry, and topology that guide the reconstruction pipeline.
"""

from copy import deepcopy

PRESET_CLASSES = {
    "generic_object": {
        "label": "Generic Object",
        "depth_ratio": 0.35,
        "symmetry": "none",
        "topology_hint": "closed_shell",
        "default_height": 1.0,
        "thickness_multiplier": 1.0,
        "description": "General-purpose object. No structural assumptions.",
    },
    "humanoid": {
        "label": "Humanoid",
        "depth_ratio": 0.30,
        "symmetry": "bilateral",
        "topology_hint": "articulated_biped",
        "default_height": 1.75,
        "thickness_multiplier": 0.85,
        "description": "Standard human proportions. Bilateral symmetry assumed.",
    },
    "chibi_humanoid": {
        "label": "Chibi Humanoid",
        "depth_ratio": 0.45,
        "symmetry": "bilateral",
        "topology_hint": "articulated_biped",
        "default_height": 1.0,
        "thickness_multiplier": 1.2,
        "description": "Stylized short proportions. Large head, compact body.",
    },
    "armored_biped": {
        "label": "Armored Biped",
        "depth_ratio": 0.42,
        "symmetry": "bilateral",
        "topology_hint": "articulated_biped",
        "default_height": 1.6,
        "thickness_multiplier": 1.15,
        "description": "Bipedal character with armor/plating. Higher depth and thickness.",
    },
    "mascot_biped": {
        "label": "Mascot Biped",
        "depth_ratio": 0.50,
        "symmetry": "bilateral",
        "topology_hint": "soft_body",
        "default_height": 1.2,
        "thickness_multiplier": 1.3,
        "description": "Round, friendly mascot character. Maximum depth ratio.",
    },
}

DEFAULT_PRESET = "armored_biped"


def get_preset(name: str) -> dict:
    """Return a deep copy of the preset, falling back to generic_object."""
    key = name if name in PRESET_CLASSES else "generic_object"
    return deepcopy(PRESET_CLASSES[key])


def list_presets() -> list[dict]:
    """Return all presets as a list with keys included."""
    result = []
    for key, data in PRESET_CLASSES.items():
        result.append({"key": key, **deepcopy(data)})
    return result
