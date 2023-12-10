from mech325.infrastructure import *

# 2023w - hw5 - q2

input_context = {
    "component_type": ComponentType.BOLTS,
    "vars": {
        "series": "UNC",
        "grade": "grade 8",
        "bolt material": "steel",
        "bolt condition": "lubricated",

        S("P_{tot}"): 80000,
        S("N_{bolt}"): 6,
        S("k_b"): 3000000,
        S("k_m"): 12000000,

        S("N"): 13,
        S("p"): 1/13,
        S("\\text{Percent\\,Preload}"): 0.75,
        S("d"): 1/2,

        S("P_{max}"): 80000/6,
        S("P_{min}"): 0,
    },
    "targets": [
        S("F_i"),
        S("T_i"),
        S("d_w"),
        S("n_{load}"),
        S("n_{separation}"),
        S("n_{fatigue}"),
    ],
}

# list_vars(input_context)
logs = analyze(context=input_context)
compile_latex(logs)

# Expected terminal
#     d = 0.5
# what is Aₜ?
#   > 0.1419
#     grade = grade 8
# what is Sₚ?
#   > 120000
# what is S_{ut}?
#   > 150000
#     bolt condition = lubricated
# what is K?
#   > 0.18
# what is Sₑ?
#   > 23200


# Expected Results
# \begin{tabular}{lll}
#     $F_{i}$ & : & 12771\\
#     $T_{i}$ & : & 1149.4\\
#     $d_{w}$ & : & 0.75000\\
#     $n_{load}$ & : & 1.5964\\
#     $n_{separation}$ & : & 1.1973\\
#     $n_{fatigue}$ & : & 0.85533\\
# \end{tabular}
