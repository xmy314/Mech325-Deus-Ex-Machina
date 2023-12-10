from mech325.infrastructure import *

# 2023w - hw5 - q1

input_context = {
    "component_type": ComponentType.BOLTS,
    "vars": {
        "series": "UNC",
        "grade": "grade 8",
        "bolt material": "steel",

        "material layers": [
            {
                S("t"): 0.095,              # [inch]
                S("d_{hole}"): 0.531,       # [inch]
                "material": "steel",
            },
            {
                S("t"): 2,                  # [inch]
                S("d_{hole}"): 0.531,       # [inch]
                S("E"): 10300000,           # [psi]
                S("S_u"): 47000,            # [psi]
                S("S_y"): 25000,            # [psi]
                "material": "aluminmum",
            },
            {
                S("t"): 2,                  # [inch]
                S("d_{hole}"): 0.531,       # [inch]
                S("E"): 10300000,           # [psi]
                S("S_u"): 47000,            # [psi]
                S("S_y"): 25000,            # [psi]
                "material": "aluminmum",
            },
            {
                S("t"): 0.095,              # [inch]
                S("d_{hole}"): 0.531,       # [inch]
                "material": "steel",
            },
        ],

        S('l'): 0.095*2+2*2,                # [inch]
        S("H"): 7/16,                       # [inch]
        S("d"): 1/2,                        # [inch]

    },
    "targets": [
        S("L"),
        S("k_b"),
        S("k_m"),
    ],
}

# list_vars(input_context)
logs = analyze(context=input_context)
compile_latex(logs)

# expected terminal
#     d = 0.5
# what is N?
#   > 13
# what is Aₜ?
#   > 0.1419
#     L_{min} = 4.858
# what is L?
#   > 5
#     bolt material = steel
# what is E?
#   > 30000000
#     material = steel
# what is E?
#   > 30000000
# what is A?
#   > 30000000
# what is B?
#   > 0.62873
#     material = aluminmum
# what is A?
#   > 0.79670
# what is B?
#   > 0.63816
#     material = aluminmum
# what is A?
#   > 0.79670
# what is B?
#   > 0.63816
#     material = steel
# what is E?
#   > 30000000
# what is A?
#   > 0.78715
# what is B?
#   > 0.62873

# Expected Result
# Final Design Parameters:\\
# \begin{tabular}{lll}
#     $L$ & : & 5\\
#     $k_{b}$ & : & 1.3514e+6\\
#     $k_{m}$ & : & 4.0813e+6\\
# \end{tabular}
