from backend.services.humanoid_skeleton import build_model_from_socket_form

def build_tree_from_form(build_form: dict):
    build_form["sockets"] = {
        "trunk": {"x": 0, "y": 0.55, "z": 0},
        "crown": {"x": 0, "y": 1.35, "z": 0},
        "crown_left": {"x": -0.35, "y": 1.2, "z": 0},
        "crown_right": {"x": 0.35, "y": 1.2, "z": 0}
    }

    build_form["parts"] = [
        {"part_id":"trunk","socket":"trunk","exists":True,"primitive":"cylinder","size":{"width":0.25,"height":1.1,"depth":0.25},"color":"#6b3f22","material":"bark"},
        {"part_id":"crown","socket":"crown","exists":True,"primitive":"sphere","size":{"width":1.0,"height":0.9,"depth":1.0},"color":"#2f7a3b","material":"leaves"},
        {"part_id":"crown_left","socket":"crown_left","exists":True,"primitive":"sphere","size":{"width":0.65,"height":0.55,"depth":0.65},"color":"#3d8a45","material":"leaves"},
        {"part_id":"crown_right","socket":"crown_right","exists":True,"primitive":"sphere","size":{"width":0.65,"height":0.55,"depth":0.65},"color":"#3d8a45","material":"leaves"}
    ]

    return build_model_from_socket_form(build_form)
