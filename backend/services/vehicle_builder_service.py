from backend.services.humanoid_skeleton import build_model_from_socket_form

def build_vehicle_from_form(build_form: dict):
    build_form["sockets"] = {
        "body": {"x": 0, "y": 0.8, "z": 0},
        "front": {"x": 0, "y": 0.8, "z": 1.0},
        "back": {"x": 0, "y": 0.8, "z": -1.0},
        "left_front_wheel": {"x": -0.75, "y": 0.35, "z": 0.75},
        "right_front_wheel": {"x": 0.75, "y": 0.35, "z": 0.75},
        "left_back_wheel": {"x": -0.75, "y": 0.35, "z": -0.75},
        "right_back_wheel": {"x": 0.75, "y": 0.35, "z": -0.75}
    }

    build_form["parts"] = [
        {"part_id":"vehicle_body","socket":"body","exists":True,"primitive":"rounded_box","size":{"width":1.5,"height":0.55,"depth":2.2},"color":"#555555","material":"vehicle_body"},
        {"part_id":"cockpit","socket":"front","exists":True,"primitive":"rounded_box","size":{"width":0.9,"height":0.45,"depth":0.7},"color":"#222222","material":"glass_dark"},
        {"part_id":"wheels","socket":"left_front_wheel","exists":True,"primitive":"cylinder","size":{"width":0.35,"height":0.25,"depth":0.35},"color":"#111111","material":"rubber"},
        {"part_id":"wheels","socket":"right_front_wheel","exists":True,"primitive":"cylinder","size":{"width":0.35,"height":0.25,"depth":0.35},"color":"#111111","material":"rubber"},
        {"part_id":"wheels","socket":"left_back_wheel","exists":True,"primitive":"cylinder","size":{"width":0.35,"height":0.25,"depth":0.35},"color":"#111111","material":"rubber"},
        {"part_id":"wheels","socket":"right_back_wheel","exists":True,"primitive":"cylinder","size":{"width":0.35,"height":0.25,"depth":0.35},"color":"#111111","material":"rubber"}
    ]

    return build_model_from_socket_form(build_form)
