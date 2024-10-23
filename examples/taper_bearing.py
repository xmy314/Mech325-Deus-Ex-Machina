from mech325.infrastructure import *


input_context = {
    "component_type": ComponentType.TAPERED_ROLLER_BEARING,
    "vars": {
        S("a_f"): 1.4,  # service factor,

        S("n"): 400,                    # angular speed [rpm]
        S("L_{hr}"): 40000,              # design life [hour]
        S("F_{rA}"): 560*4.45/1000,     # radial load [kN]
        S("F_{rB}"): 1095*4.45/1000,    # radial load [kN]
        S("F_{ae}"): 200*4.45/1000,     # axial load [kN]
        S("R_d"): 0.9,                  # design reliability.

        # the following are timken parameters which are mostly the case for taper bearings.
        S("x_0"): 0.0,
        S("\\theta"): 4.48,
        S("b"): 1.5,
        S("L_{10}"): 90_000_000,
    },
    "targets": [
        # in order that solution comes, else the order of solution is weird.

        "A cone number",
        "A cup number",
        "B cone number",
        "B cup number",
    ],
}

# list_vars(input_context)

# list_vars(input_context)
logs = analyze(context=input_context)
compile_latex(logs)
