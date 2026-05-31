from backend.services.humanoid_skeleton import build_model_from_socket_form

def build_prop_from_form(build_form: dict):
    build_form["sockets"] = {
        "base": {"x": 0, "y": 0.35, "z": 0},
        "top": {"x": 0, "y": 0.9, "z": 0}
    }

    build_form["parts"] = [
        {"part_id":"prop_base","socket":"base","exists":True,"primitive":"rounded_box","size":{"width":0.9,"height":0.7,"depth":0.9},"color":"#777777","material":"prop_material"},
        {"part_id":"prop_top","socket":"top","exists":True,"primitive":"sphere","size":{"width":0.55,"height":0.55,"depth":0.55},"color":"#999999","material":"prop_detail"}
    ]

    return build_model_from_socket_form(build_form)
