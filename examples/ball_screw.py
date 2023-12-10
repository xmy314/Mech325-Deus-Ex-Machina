from mech325.infrastructure import *

input_context = {
    "component_type": ComponentType.BALL_SCREWS,
    "vars": {
        S("L_d"): 36*12*24*365*10,           # life time in travel distance [inch]
        S("F"): 900,                         # load [lbf]
        S("V"): 2,                         # load [inch / sec]
    },
    "targets": [
        S("d"),
        S("T_u"),
        S("P"),

    ],
}

# list_vars(input_context)
logs = analyze(context=input_context)
compile_latex(logs)
