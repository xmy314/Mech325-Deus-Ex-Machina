from infrastructure import *
import sympy as sym

input_context = {
    "component_type": ComponentType.BOUNDARY_LUBRICATED_BEARING,
    "vars": {
        "bushing material": "Oiles SP 500",

        S("n_d"): 2,
        S("f_s"): 0.03,
        S("\\hbar_{cr}"): 2.7,
        S("J"): 778,
        S("T_{\\infty}"): 70,
        S("T_{max}"): 300,
        S("t"): 1000,
        S("w_{max}"): 0.002,

        S("F"): 100,
        S("N"): 200,                    # angular speed [rpm]

        S("D_{constrained}"): 1.25,
    },
    "targets": [
        # in order that solution comes, else the order of solution is weird.
        S("D"),
        S("L"),
    ],
}

analyze(context=input_context)

compile_latex()
