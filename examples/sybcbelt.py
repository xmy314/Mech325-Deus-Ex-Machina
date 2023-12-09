from mech325.infrastructure import *

input_context = {
    "component_type": ComponentType.SYNCHRONOUS_BELT,
    "vars": {
        # text description []
        "driven": "gear pump",
        "driver": "normal torque electric motor",
        "duty time": "16 hours/day",
        "input shaft diameter": 1.65,
        "maximum input flange size": -1,
        "output shaft diameter": 1.375,
        "maximum output flange size": 14,

        S("n_{in}"): 1750,              # inpur angular speed [rpm]
        S("CD_{nom}"): 22,              # inpur angular speed [rpm]
        S("n_{out\\,rough}"): 875,      # nominal output angular speed [rpm]
        S("H_{nom}"): 20,                # nominal power [hp]
    },
    "targets": [                                    # in reverse direction as logical direction.
        S("N_{in}"),
        "input bushing size",
        S("N_{out}"),
        "output bushing size",
        "belt number",
        S("W"),
    ],
}

analyze(context=input_context)
