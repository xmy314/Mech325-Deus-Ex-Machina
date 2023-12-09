from mech325.bolt_joint_analysis import *

# When reading tables, if metric, input in base SI unit, else based on lbf, in, s

context = {
    "vars": {
    },
    "bolts": [
        {
            S("d"): 0.012,                      # m or in
            S("x"): 0,                          # m or in
            S("y"): 0.032,                      # m or in
            "grade": "ISO 5.8",
        },
        {
            S("d"): 0.012,
            S("x"): 0,
            S("y"): 0,
            "grade": "ISO 5.8",
        },
        {
            S("d"): 0.012,
            S("x"): 0,
            S("y"): -0.032,
            "grade": "ISO 5.8",
        },
    ],
    "bracket": {
        "grade": "AISI 1020 hot rolled",
        S("t"): 0.008,                          # m or in
        "weak point": {
            S("M"): 2400,                       # Nm or lbf in
            S("I"):                             # Calculate this manually.
            (1/12*8*136**3
             - 3*(1/12*8*12**3)
             - 2*(12*8*32**2))/(1000**4),       # m^4 or in^4
            S("y"): 0.068,                      # top edge of the bracket, relative to neutral plane
        },
    },
    "loads": [
        {
            "x": 0.200,                         # m or in
            "y": 0,                             # m or in
            "fx": 0,                            # N or in
            "fy": -12000,                       # N or in
        },
    ]
}

logs = []
logs += geometry(context)
logs += force_analysis(context)
logs += stress_analysis(context)
compile_latex(logs)

# expected result:

# \begin{align*}
#     n_{\text{bolt shear}}      & = 0.727
#     n_{\text{bolt bearing}}    & = 1.07
#     n_{\text{bracket bearing}} & = 0.535
#     n_{\text{bracket bending}} & = 1.9
# \end{align*}
