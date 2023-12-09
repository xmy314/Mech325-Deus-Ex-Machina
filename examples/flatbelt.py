from mech325.infrastructure import *

input_context = {
    "component_type": ComponentType.FLAT_BELT,
    "vars": {
        "belt": "Polyamide F-1",        # text description []

        S("b"): 12,                     # width [inch]
        S("CD"): 18*12,                 # center line distance [inch]
        S("VR"): 2,                     # velocity ratio, n input/ n output []

        S("D_{in}"): 4,                 # input diameter [inch]
        S("n_{in}"): 1750,              # inpur angular speed [rpm]
        S("H_{nom}"): 2,                # nominal power [hp]
        S("K_s"): 1.25,                 # service factor []
        S("n_d"): 1,                    # design factor []
    },
    "targets": [                                    # in reverse direction as logical direction.
        S("L"),
        S("n_{sf}"),
        S("dip"),
    ],
}

analyze(context=input_context)
