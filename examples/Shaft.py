from mech325.infrastructure import *
from shaft_selection import *
context = {
    "components": [
        {
            "component_type": ComponentType.V_BELT,
            "name": "A",
            "z": 0,  # [inch]
            "theta": radians(-90),
            "is driver": 1,
            "power": 10,  # [hp]
            "diameter": 12,
            "left feature": "ring",
            "center feature": "sled runner",
            "right feature": "ring",
            "secured by": ComponentType.KEY,
        },
        {
            "component_type": ComponentType.BALL_AND_CYLINDRICAL_BEARING_RADIAL,
            "name": "B",
            "z": 6,
            "theta": 0,
            "is driver": 0,
            "power": 0,
            "diameter": 0,
            "left feature": "large fillet",
            "right feature": "sharp fillet",
            "secured by": ComponentType.KEY,
        },
        {
            "component_type": ComponentType.BALL_AND_CYLINDRICAL_BEARING_RADIAL,
            "name": "C",
            "z": 36,
            "theta": 0,
            "is driver": 0,
            "power": 0,
            "diameter": 0,
            "left feature": "sharp fillet",
            "right feature": "large fillet",
        },
        {
            "component_type": ComponentType.SPUR_GEAR,
            "name": "D",
            "z": 42,
            "theta": radians(210),
            "is driver": -1,
            # "power": sym.Integer(15),  # This is passed to avoid over constraining and floating point error.
            "power": S("P_g"),
            "diameter": 8,
            "pressure angle": radians(20),
            "left feature": "ring",
            "center feature": "sled runner",
            "right feature": "ring",
        },
        {
            "component_type": ComponentType.CHAIN,
            "name": "E",
            "z": 52,
            "theta": radians(30),
            "is driver": 1,
            "power": sym.Integer(5),
            "diameter": 6,
            "left feature": "ring",
            "center feature": "sled runner",
            "right feature": "ring",
            "secured by": ComponentType.KEY,
        },
    ],
    "vars": {
        S("n"): 240,  # Shaft Rotation Rate [RPM]
        S("N"): 3,  # Safety Factor typically between 2.5 to 3
        "rotation direction": -1,
        "SAE": "1137 cold drawn",
        "Reliability": "0.99",
        "surface condition": "Machined or Cold Drawn",  # assumed typical case
    },
}

logs = []
logs.append(convert_component_to_load(context))
logs.append(solve_reaction_force(context))
logs.append(fbd3d(context))
logs.append(shaft_analysis(context))
logs += divide_and_conquer(context)

compile_latex(logs)
