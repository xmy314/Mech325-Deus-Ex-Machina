
from mech325.infrastructure import *


def retrieve_singlebolt_information():
    print("Retrieving information for solving bolts questions from Shigley.")
    print("Please note that the following code is not tested.")

    def lookup_geometry(knowns):
        logs = []
        if knowns["series"] == "metric":
            logs += solve_pathway((PathType.TABLE_OR_FIGURE, "Shigley Table 8-1", [[S("p"), S("A_t")], [S("d")]]), knowns)
            if not S("N") in knowns or not S("p") in knowns:
                logs += solve_pathway((PathType.EQUATION, "Geometry", Geqn(S("N"), 1/S("p"))), knowns)
        else:
            logs += solve_pathway((PathType.TABLE_OR_FIGURE, "Shigley Table 8-2", [[S("N"), S("A_t")], [S("d")]]), knowns)
            if not S("N") in knowns or not S("p") in knowns:
                logs += solve_pathway((PathType.EQUATION, "Geometry", Geqn(S("p"), 1/S("N"))), knowns)
        return logs

    def round_L(knowns):
        logs = []
        solve_pathway((PathType.TABLE_OR_FIGURE, "General Figure round", [[S("L")], [S("L_{min}")]]), knowns)
        logs.append(f'Rounding up $L = {knowns[S("L")]}$')
        return logs

    def get_LT(knowns):
        logs = []
        if knowns["series"] == "UNC" or knowns["series"] == "UNF":
            if knowns[S("d")] <= 6:
                logs += solve_pathway((PathType.EQUATION, "Shigley Equation 8-13 a", Geqn(S("L_T"), 2*S("d")+0.25)), knowns)
            else:
                logs += solve_pathway((PathType.EQUATION, "Shigley Equation 8-13 b", Geqn(S("L_T"), 2*S("d")+0.5)), knowns)
        elif knowns["series"] == "Metric":
            if knowns[S("d")] <= 125:
                logs += solve_pathway((PathType.EQUATION, "Shigley Equation 8-14 a", Geqn(S("L_T"), 2*S("d")+6)), knowns)
            elif knowns[S("d")] <= 200:
                logs += solve_pathway((PathType.EQUATION, "Shigley Equation 8-14 a", Geqn(S("L_T"), 2*S("d")+12)), knowns)
            else:
                logs += solve_pathway((PathType.EQUATION, "Shigley Equation 8-14 a", Geqn(S("L_T"), 2*S("d")+25)), knowns)
        else:
            raise Exception("series need to be a value within [UNC, UNF, Metric]")
        return logs

    def get_km(knowns):
        # each material layer is a "knowns" structure
        logs = []
        raw_material_layers = knowns["material layers"]

        total_thickness = 0
        for raw_material_layer in raw_material_layers:
            if not S("d_{hole}") in raw_material_layer:
                raw_material_layer[S("d_{hole}")] = knowns[S("d")]
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
        entry += "\\\\\n" + r"    t_{total}&="+f"{total_thickness:.5g}"+"\n"
        entry += r"\end{align*}"
        logs.append(entry)

        pathmp = (PathType.TABLE_OR_FIGURE,
                  "Shigley Table 8-8",
                  [[S("E"), S("A"), S("B")], ["material"]])

        path20 = (PathType.EQUATION, "Shigley Equation 8-20", Geqn(
            S("k"),
            (
                0.5774*sym.pi*S("E")*S("d_{hole}")
            )/(
                sym.ln(
                    ((1.155*S("t")+S("D")-S("d_{hole}"))*(S("D")+S("d_{hole}"))) /
                    ((1.155*S("t")+S("D")+S("d_{hole}"))*(S("D")-S("d_{hole}")))
                )
            )
        ))

        pathgeo = (
            PathType.EQUATION,
            "Shigley Equation 8-20",
            Geqn(S("D"), 1.5*S("d")+2*S("h_s")*sym.tan(0.523599))
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
            entry += f'+\\frac{{1}}{{{material_layer[S("k")]:.5g}}}'
        knowns[S("k_m")] = 1/total_spring_constant_inverse
        entry += "\\\\\n" + r"    k_m&="+f"{knowns[S('k_m')]:.3g}"+"\n"
        entry += r"\end{align*}"
        logs.append(entry)

        return logs

    def get_strength(knowns):
        logs = []
        if "SAE" in knowns["grade"] or "grade" in knowns["grade"]:
            logs += solve_pathway((PathType.TABLE_OR_FIGURE, "Shigley Table 8-9", [[S("S_p"), S("S_{ut}")], ["grade"]]), knowns)
        elif "ASTM" in knowns["grade"] or "designation" in knowns["grade"]:
            logs += solve_pathway((PathType.TABLE_OR_FIGURE, "Shigley Table 8-10", [[S("S_p"), S("S_{ut}")], ["grade"]]), knowns)
        elif "Metric" in knowns["grade"] or "class" in knowns["grade"]:
            logs += solve_pathway((PathType.TABLE_OR_FIGURE, "Shigley Table 8-11", [[S("S_p"), S("S_{ut}")], ["grade"]]), knowns)
        else:
            raise Exception("Unable to determine standard, please include one and only one of the following in \"grade\":\n    [SAE, ASTM, Metric, grade, designation, class]")
        return logs

    pathways = [
        (PathType.TABLE_OR_FIGURE, "Shigley Figure instruction-8-l", [[S("l")], []]),
        (PathType.CUSTOM, "Geometry of Various Standard", [[S("p"), S("N"), S("A_t")], ["series", S("d")]], lookup_geometry),
        (PathType.EQUATION, "Tutorial", Geqn(S("L_{min}"), S("l")+S("H")+3*S("p"))),
        (PathType.CUSTOM, "round to standard", [[S("L")], [S("L_{min}")]], round_L),
        (PathType.CUSTOM, "Shigley Equation 8-13/14", [[S("L_T")], ["series", S("d")]], get_LT),
        (PathType.EQUATION, "Shigley Equation TODO", Geqn(S("l_d"), S("L")-S("L_T"))),
        (PathType.EQUATION, "Shigley Equation TODO", Geqn(S("l_t"), S("l")-S("l_d"))),
        (PathType.EQUATION, "Shigley Equation TODO", Geqn(S("A_d"), sym.pi*S("d")**2/4)),
        (PathType.EQUATION, "General rule", Geqn(S("d_w"), 1.5*S("d"))),

        (PathType.TABLE_OR_FIGURE, "Shigley Table 8-8", [[S("E")], ["bolt material"]]),
        (PathType.EQUATION, "Shigley Eqaution 8-16", Geqn(S("k_t"), S("A_t")*S("E")/S("l_t"))),
        (PathType.EQUATION, "Shigley Eqaution 8-16", Geqn(S("k_d"), S("A_d")*S("E")/S("l_d"))),
        (PathType.EQUATION, "Shigley Eqaution 8-17", Geqn(S("k_b"), S("A_d")*S("A_t")*S("E")/(S("A_d")*S("l_t")+S("A_t")*S("l_d")))),
        (PathType.CUSTOM, "equvilent spring constant of material", [[S("k_m")], ["material layers"]], get_km),

        (PathType.CUSTOM, "Shigley proof and ultimate strength", [[S("S_p"), S("S_{ut}")], ["grade"]], get_strength),
        (PathType.TABLE_OR_FIGURE, "Shigley Table 8-17", [[S("S_e")], []]),

        (PathType.EQUATION, "Shigley Eqaution TODO", Geqn(S("P"), S("P_{tot}")/S("N_{bolt}"))),
        (PathType.EQUATION, "Shigley Equation TODO", Geqn(S("F_i"), S("\\text{Percent\\,Preload}")*S("A_t")*S("S_p"))),

        (PathType.EQUATION, "Joint Costant", Geqn(S("C"), S("k_b")/(S("k_b")+S("k_m")))),
        (PathType.EQUATION, "Shigley Equation 8-24", Geqn(S("F_b"), (S("C"))*S("P")+S("F_i"))),
        (PathType.EQUATION, "Shigley Equation 8-25", Geqn(S("F_m"), (1-S("C"))*S("P")-S("F_i"))),

        (PathType.EQUATION, "Shigley Equation 8-27", Geqn(S("T_i"), S("K")*S("F_i")*S("d"))),
        (PathType.EQUATION, "average diameter", Geqn(S("d_m"), (S("d")+S("d_r"))/2)),
        (PathType.EQUATION, "lead angle", Geqn(sym.tan(S("\\lambda")), S("p")/(sym.pi * S("d_m")))),
        (PathType.EQUATION, "Shigley Equation 8-26", Geqn(
            S("K"),
            S("d_m")/(2*S("d")) *
            (sym.tan(S("\\lambda")) + S("f")*sym.sec(S("\\alpha"))) /
            (1-S("f")*sym.tan(S("\\lambda"))*sym.sec(S("\\alpha")))
            + 0.625*S("f_c")
        )),
        (PathType.TABLE_OR_FIGURE, "Shigley Table 8-15", [[S("K")], ["bolt condition"]]),

        (PathType.EQUATION, "Shigley Equation TODO", Geqn(S("n_{load}"), (S("S_p")*S("A_t")-S("F_i"))/(S("C")*S("P")))),
        (PathType.EQUATION, "Shigley Equation TODO", Geqn(S("n_{yield\\,tensile}"), (S("C")*S("P")+S("F_i"))/S("A_t"))),
        (PathType.EQUATION, "Shigley Equation TODO", Geqn(S("n_{yield\\,static}"), S("S_p")*S("A_t")/(S("C")*S("P")+S("F_i")))),
        (PathType.EQUATION, "Shigley Equation TODO", Geqn(S("n_{separation}"), S("F_i")/(S("P")*(1-S("C"))))),
        (PathType.EQUATION, "Shigley Equation TODO", Geqn(S("\\sigma_i"), S("F_i")/S("A_t"))),
        (PathType.EQUATION, "Shigley Equation TODO", Geqn(S("\\sigma_a"), S("C")*(S("P_{max}")-S("P_{min}"))/(2*S("A_t")))),
        (PathType.EQUATION, "Shigley Equation TODO", Geqn(S("\\sigma_m"), S("C")*(S("P_{max}")+S("P_{min}"))/(2*S("A_t"))+S("\\sigma_i"))),
        (PathType.EQUATION, "Shigley Equation TODO", Geqn(
            S("n_{fatigue}"),
            (S("S_e")*(S("S_{ut}")-S("\\sigma_i"))) /
            (S("S_{ut}")*S("\\sigma_a")+S("S_e")*(S("\\sigma_m")-S("\\sigma_i")))
        )),
    ]

    return pathways
