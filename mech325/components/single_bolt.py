from mech325.infrastructure import *


def retrieve_singlebolt_information():
    print("Retrieving information for solving bolts questions from Shigley.")
    print("Please note that the following code is not tested.")

    def get_At(knowns):
        logs = []
        if knowns["series"] == "metric":
            logs += solve_pathway((PathType.TABLE_OR_FIGURE, "Shigley Table 8-1", [[S("A_t")], ["d"]]), knowns)
        else:
            logs += solve_pathway((PathType.TABLE_OR_FIGURE, "Shigley Table 8-1", [[S("A_t")], ["d"]]), knowns)
        return logs

    def get_LT(knowns):
        logs = []
        if knowns["series"] == "inch":
            if knowns[S("L")] <= 6:
                logs += solve_pathway((PathType.EQUATION, "Shigley Equation 8-13 a", Geqn(S("L_T"), S("L")+0.25)), knowns)
            else:
                logs += solve_pathway((PathType.EQUATION, "Shigley Equation 8-13 b", Geqn(S("L_T"), S("L")+0.5)), knowns)
        else:
            if knowns[S("L")] <= 125:
                logs += solve_pathway((PathType.EQUATION, "Shigley Equation 8-14 a", Geqn(S("L_T"), S("L")+6)), knowns)
            elif knowns[S("L")] <= 200:
                logs += solve_pathway((PathType.EQUATION, "Shigley Equation 8-14 a", Geqn(S("L_T"), S("L")+12)), knowns)
            else:
                logs += solve_pathway((PathType.EQUATION, "Shigley Equation 8-14 a", Geqn(S("L_T"), S("L")+25)), knowns)
        return logs

    def get_km(knowns):
        # each material layer is a "knowns" structure
        logs = []
        raw_material_layers = knowns["material layers"]

        total_thickness = 0
        for raw_material_layer in raw_material_layers:
            raw_material_layer[S("d")] = knowns[S("d")]
            raw_material_layer[S('h_s')] = total_thickness
            total_thickness += raw_material_layer[S("t")]
            raw_material_layer[S('h_e')] = total_thickness

        material_layers = []
        for raw_material_layer in raw_material_layers:
            if raw_material_layer[S("h_s")] < total_thickness/2 and raw_material_layer[S("h_e")] <= total_thickness/2:
                material_layers.append(raw_material_layer)
            elif raw_material_layer[S("h_s")] < total_thickness/2 and raw_material_layer[S("h_e")] > total_thickness/2:
                mid_1 = raw_material_layer.copy()
                mid_1[S("h_s")] = raw_material_layer[S("h_s")]
                mid_1[S("h_e")] = total_thickness/2
                mid_2 = raw_material_layer.copy()
                mid_2[S("h_s")] = total_thickness-raw_material_layer[S("h_e")]
                mid_2[S("h_e")] = total_thickness/2
                material_layers.append(mid_1)
                material_layers.append(mid_2)
            else:
                inverted = raw_material_layer.copy()
                inverted[S("h_s")] = total_thickness-raw_material_layer[S("h_e")]
                inverted[S("h_e")] = total_thickness-raw_material_layer[S("h_s")]
                material_layers.append(inverted)

        entry = r"\begin{align*}"+"\n"
        entry += "    t_{total}&="
        for material_layer in material_layers:
            entry += f'+{material_layer[S("t")]:.5g}'
        entry += "\n" + r"    t_{total}&="+f"{total_thickness:.5g}"+"\n"
        entry = r"\end{align*}"
        logs.append(entry)

        pathmp = (PathType.TABLE_OR_FIGURE,
                  "Shigley Table 8-8",
                  [[S("E"), S("A"), S("B")], ["material"]])

        path20 = (PathType.EQUATION, "Shigley Equation 8-20", Geqn(
            S("k"),
            (
                0.5774*sym.pi*S("E")*S("d")
            )/(
                sym.ln(
                    ((1.155*S("t")+S("D")-S("d"))*(S("D")+S("d"))) /
                    ((1.155*S("t")+S("D")+S("d"))*(S("D")-S("d")))
                )
            )
        ))

        pathgeo = (
            PathType.EQUATION,
            "Shigley Equation 8-20",
            Geqn(S("D"), 1.5*S("d")+S("h_s")*sym.tan(0.523599))
        )

        for i, material_layer in enumerate(material_layers):
            logs.append(f"Solve spring constant for layer {i}")

            logs.append(f"$$h_s={material_layer[S('h_s')]:.3g}$$")
            logs.append(f"$$h_e={material_layer[S('h_e')]:.3g}$$")

            logs += solve_pathway(pathmp, material_layer)
            logs += solve_pathway(pathgeo, material_layer)
            logs += solve_pathway(path20, material_layer)

        total_spring_constant_inverse = 0
        entry = r"\begin{align*}"+"\n"
        entry += r"    \frac{1}{k_m}&="
        for material_layer in material_layers:
            total_spring_constant_inverse += 1/material_layer[S("k")]
            entry += f'+\frac{1}{material_layer[S("t")]:.5g}'
        knowns[S("k_m")] = 1/total_spring_constant_inverse
        entry += "\n" + r"    k_m&="+f"{knowns[S('k_m')]:.3g}"+"\n"
        entry = r"\end{align*}"
        logs.append(entry)

        return logs

    def get_strength(knowns):
        logs = []
        if knowns["specification standard"] == "SAE":
            logs += solve_pathway((PathType.TABLE_OR_FIGURE, "Shigley Equation 8-9", [[S("S_p"), S("S_{ut}")], ["specification NO"]]), knowns)
        elif knowns["specification standard"] == "ASTM":
            logs += solve_pathway((PathType.TABLE_OR_FIGURE, "Shigley Equation 8-10", [[S("S_p"), S("S_{ut}")], ["specification NO"]]), knowns)
        elif knowns["specification standard"] == "metric":
            logs += solve_pathway((PathType.TABLE_OR_FIGURE, "Shigley Equation 8-11", [[S("S_p"), S("S_{ut}")], ["specification NO"]]), knowns)
        return logs

    pathways = [
        (PathType.CUSTOM, "Shigley Equation 8-13/14", [[S("L_T")], ["series", S("d")]], get_LT),
        (PathType.TABLE_OR_FIGURE, "Shigley Figure instruction-8-l", [["l"], []]),
        (PathType.EQUATION, "Shigley Equation TODO", Geqn(S("l_d"), S("L")-S("L_T"))),
        (PathType.EQUATION, "Shigley Equation TODO", Geqn(S("l_t"), S("l")-S("l_d"))),
        (PathType.EQUATION, "Shigley Equation TODO", Geqn(S("A_d"), sym.pi*S("d")**2/4)),
        (PathType.CUSTOM, "equvilent spring constant of material", [[S("A_t")], ["series", "d"]], get_At),

        (PathType.EQUATION, "Shigley Eqaution 8-16", Geqn(S("k_t"), S("A_t")*S("E")/S("l_t"))),
        (PathType.EQUATION, "Shigley Eqaution 8-16", Geqn(S("k_d"), S("A_d")*S("E")/S("l_d"))),
        (PathType.EQUATION, "Shigley Eqaution 8-17", Geqn(S("k_b"), S("A_d")*S("A_t")*S("E")/(S("A_d")*S("l_t")+S("A_t")*S("l_d")))),
        (PathType.CUSTOM, "equvilent spring constant of material", [[S("k_m")], ["material layers"]], get_km),

        (PathType.TABLE_OR_FIGURE, "Shigley proof and ultimate strength", [[S("S_p"), S("S_{ut}")], ["specification NO"]], get_strength),
        (PathType.TABLE_OR_FIGURE, "Shigley Equation 8-17", [[S("S_{e}")], ["specification NO"]]),

        (PathType.EQUATION, "Shigley Eqaution TODO", Geqn(S("P"), S("P_{tot}")/S("N"))),
        (PathType.EQUATION, "Shigley Equation TODO", Geqn(S("F_i"), S("\\text{Percent\\,Preload}")*S("A_t")*S("S_p"))),

        (PathType.EQUATION, "Joint Costant", Geqn(S("C"), S("k_b")/(S("k_b")+S("k_m")))),
        (PathType.EQUATION, "Shigley Equation 8-24", Geqn(S("F_b"), (S("C"))*S("P")+S("F_i"))),
        (PathType.EQUATION, "Shigley Equation 8-25", Geqn(S("F_m"), (1-S("C"))*S("P")-S("F_i"))),

        (PathType.EQUATION, "Shigley Equation 8-27", Geqn(S("T"), S("K")*S("F_i")*S("d"))),
        (PathType.EQUATION, "average diameter", Geqn(S("d_m"), (S("d")+S("d_r"))/2)),
        (PathType.EQUATION, "lead angle", Geqn(sym.tan(S("\\lambda")), S("p")/(sym.pi * S("d_m")))),
        (PathType.EQUATION, "Shigley Equation 8-26", Geqn(
            S("K"),
            S("d_m")/(2*S("d")) *
            (sym.tan(S("\\lambda")) + S("f")*sym.sec("\\alpha")) /
            (1-S("f")*sym.tan(S("\\lambda"))*sym.sec("\\alpha"))
            + 0.625*S("f_c")
        )),
        (PathType.TABLE_OR_FIGURE, "Shigley Table 8-15", [[S("K")], ["bolt condition"]]),

        (PathType.EQUATION, "Shigley Equation TODO", Geqn(S("n_L"), (S("S_p")*S("A_t")-S("F_i"))/(S("C")*S("P")))),
        (PathType.EQUATION, "Shigley Equation TODO", Geqn(S("n_y"), S("S_p")*S("A_t")/(S("C")*S("P")+S("F_i")))),
        (PathType.EQUATION, "Shigley Equation TODO", Geqn(S("n_0"), S("F_i")/(S("P")*(1-S("C"))))),
        (PathType.EQUATION, "Shigley Equation TODO", Geqn(S("\\sigma_i"), S("F_i")/S("A_t"))),
        (PathType.EQUATION, "Shigley Equation TODO", Geqn(S("\\sigma_a"), S("C")*(S("P_{max}")-S("P_{min}"))/(2*S("A_t")))),
        (PathType.EQUATION, "Shigley Equation TODO", Geqn(S("\\sigma_m"), S("C")*(S("P_{max}")+S("P_{min}"))/(2*S("A_t"))+S("\\sigma_i"))),
        (PathType.EQUATION, "Shigley Equation TODO", Geqn(
            S("n_f"),
            (S("S_e")*(S("S_{ut}")-S("\\sigma_i"))) /
            (S("S_{ut}")*S("\\sigma_a")+S("S_e")*(S("\\sigma_m")-S("\\sigma_i")))
        )),
    ]
