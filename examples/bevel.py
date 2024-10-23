from mech325.infrastructure import *
from math import radians

input_context = {
    "component_type": ComponentType.BEVEL_GEAR,
    "vars": {
        "driver": "AC (normal torque)",
        "driven": "Pump (Reciprocating)",
        S("n_{in}"): 1750,
        S("n_{out\\,rough}"): 580,
        S("N_{in}"): 20,
        S("F"): 1,
        S("P_d"): 10,
        S("H_{nom}"): 10,
        S("\\phi"): radians(20),
        S("A_v"): 8,
        S("K_o"): 1.5,
        S("L_{hr}"): 1500,

        "is crowned": 0,
        "straddle mount count": 1,

        S("N_{out}"): 60,
        S("J_{in}"): 0.247,
        S("J_{out}"): 0.202,

        "Reliability": 0.9,
    },
    "targets": [
        S("N_{out}"),
        S("VR"),
        S("D_{in}"),
        S("D_{out}"),
        S("V"),
        S("\\gamma"),
        S("\\Gamma"),
        S("W_{x\\,in\\,force}"),
        S("W_{x\\,out\\,force}"),
        S("W_{t\\,in\\,force}"),
        S("W_{t\\,out\\,force}"),
        S("W_{r\\,in\\,force}"),
        S("W_{r\\,out\\,force}"),
        S("s_{b\\,in}"),
        "SAE",
    ]
}

# list_vars(input_context)
logs = analyze(context=input_context)
compile_latex(logs)
