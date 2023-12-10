from mech325.infrastructure import *

# 2023w - hw5 - q5

input_context = {
    "component_type": ComponentType.SPRINGS,
    "vars": {
        "unit system": "si",
        "spring end": "plain",
        "Material": "oil tempered",

        S("C"): 10,                 # []
        S("d"): 0.004,              # [m]
        S("L_f"): 0.08,             # [m]
        S("F_o"): 50,               # [N]
        S("y_o"): 0.015,            # [m]
    },
    "targets": [
        S("k"),
        S("D_{out}"),
        S("N_t"),
        S("L_s"),
        S("n_y"),
    ],
}

# list_vars(input_context)
logs = analyze(context=input_context)
compile_latex(logs)

# expected input, the unit of A typically doesn't need to
# G = 77200000000 [Pa]
# \frac{S_{sy}}{S_{ut}} = 0.50 [0-1]
# A = 1855000000 [Pa/mm^d]
# m = 0.187

# Expected Result
# \begin{tabular}{lll}
#     $k$ & : & 3330.00000000000\\
#     $D_{out}$ & : & 0.0440\\
#     $N_{t}$ & : & 11.6\\
#     $L_{s}$ & : & 0.0503\\
#     $n_{y}$ & : & 4.00000000000000\\
# \end{tabular}
