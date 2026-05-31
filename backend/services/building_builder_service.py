from backend.services.humanoid_skeleton import build_model_from_socket_form

def build_building_from_form(build_form: dict):
    build_form["sockets"] = {
        "base": {"x": 0, "y": 0.6, "z": 0},
        "roof": {"x": 0, "y": 1.28, "z": 0},
        "door": {"x": 0, "y": 0.35, "z": 0.51}
    }

    build_form["parts"] = [
        {"part_id":"building_body","socket":"base","exists":True,"primitive":"box","size":{"width":1.5,"height":1.2,"depth":1.0},"color":"#8a7a66","material":"wall"},
        {"part_id":"roof","socket":"roof","exists":True,"primitive":"cone","size":{"width":1.25,"height":0.55,"depth":1.25},"color":"#7a2f2f","material":"roof"},
        {"part_id":"door","socket":"door","exists":True,"primitive":"box","size":{"width":0.35,"height":0.55,"depth":0.06},"color":"#3a2418","material":"door"}
    ]

    return build_model_from_socket_form(build_form)
