# transport.py

TRANSPORT_BODY_WIDTH = {
    "bike": 0.75,
    "car": 1.6,
    "tank": 2.2,
    "drone": 1.2,
    "helicopter": 1.8,
    "airplane": 2.6,
}

TRANSPORT_BODY_HEIGHT = {
    "bike": 0.9,
    "car": 1.1,
    "tank": 1.3,
    "drone": 0.35,
    "helicopter": 0.9,
    "airplane": 0.8,
}

def get_transport_profile(
    wheel_count=4,
    transport_mode="ground",
    body_type="car",
):
    """
    transport_mode: ground / flying
    body_type:
      ground: bike / car / tank
      flying: drone / helicopter / airplane

    wheel_count controls length.
    body_type controls width + height.
    ground = vertical wheels.
    flying = horizontal rotors.
    """

    wheel_count = max(2, int(wheel_count))

    width = TRANSPORT_BODY_WIDTH.get(body_type, 1.5)
    height = TRANSPORT_BODY_HEIGHT.get(body_type, 1.0)

    # auto length by wheel count
    length = 1.4 + (wheel_count * 0.65)

    if body_type == "bike":
        length *= 0.75
    elif body_type == "tank":
        length *= 1.25
    elif body_type == "airplane":
        length *= 1.5

    if transport_mode == "ground":
        mover_type = "vertical_wheel"
        wheel_rotation = "vertical"
    else:
        mover_type = "horizontal_rotor"
        wheel_rotation = "horizontal"

    return {
        "wheel_count": wheel_count,
        "transport_mode": transport_mode,
        "body_type": body_type,
        "length": length,
        "width": width,
        "height": height,
        "mover_type": mover_type,
        "wheel_rotation": wheel_rotation,
    }


# presets
BIKE = get_transport_profile(2, "ground", "bike")
CAR = get_transport_profile(4, "ground", "car")
LORRY_TANK = get_transport_profile(6, "ground", "tank")

DRONE = get_transport_profile(2, "flying", "drone")
HELICOPTER = get_transport_profile(4, "flying", "helicopter")
AIRPLANE = get_transport_profile(6, "flying", "airplane")