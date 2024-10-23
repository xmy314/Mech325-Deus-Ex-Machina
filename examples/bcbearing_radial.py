from mech325.infrastructure import *


input_context = {
    "component_type": ComponentType.BALL_AND_CYLINDRICAL_BEARING_RADIAL,
    "vars": {
        # text description []
        "rolling element type": "02-series deep-groove ball bearing",
        "rolling race": "inner",
        S("a_f"): 1.2,

        S("n"): 300,                    # inpur angular speed [rpm]
        S("L_{hr}"): 30000,             # design life [hour]
        S("F"): 1.898,                   # redial load [kN]
        S("R_d"): 0.9,                  # design reliability.

        # the following are skf parameters which are mostly the case
        S("x_0"): 0.02,
        S("\\theta"): 4.459,
        S("b"): 1.483,
        S("L_{10}"): 1000000,
    },
    "targets": [
        # in order that solution comes, else the order of solution is weird.

        S("x_d"),
        S("C_{10}"),

        S("Bore"),
        S("R"),
    ],
}

# list_vars(input_context)
logs = analyze(context=input_context)
compile_latex(logs)
