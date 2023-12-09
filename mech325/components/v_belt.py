from mech325.infrastructure import *

def retrieve_vbelt_information():
    print("Retrieving information for solving vbelt questions from Mott.")
    print("Please note that it only solves upper operation limit due to stress but not lower operation limit from friction.")

    def sheave_selection(knowns):
        logs = []
        if knowns["belt type"] == "3V" or knowns["belt type"] == "3v":
            logs += solve_pathway((PathType.TABLE_OR_FIGURE, "Mott Figure 7-14", [[S("D_{in}"), S("D_{out}"), S("H_{tab}")], [S("VR_{rough}"), S("D_{in\\,rough}")]]), knowns)
        elif knowns["belt type"] == "5V" or knowns["belt type"] == "5v":
            logs += solve_pathway((PathType.TABLE_OR_FIGURE, "Mott Figure 7-15", [[S("D_{in}"), S("D_{out}"), S("H_{tab}")], [S("VR_{rough}"), S("D_{in\\,rough}")]]), knowns)
        elif knowns["belt type"] == "8V" or knowns["belt type"] == "8v":
            logs += solve_pathway((PathType.TABLE_OR_FIGURE, "Mott Figure 7-16", [[S("D_{in}"), S("D_{out}"), S("H_{tab}")], [S("VR_{rough}"), S("D_{in\\,rough}")]]), knowns)
        else:
            raise Exception("unacceptable belt type")
        return logs

    def extra_power(knowns):
        logs = []
        if knowns["belt type"] == "3V" or knowns["belt type"] == "3v":
            logs += solve_pathway((PathType.TABLE_OR_FIGURE, "Mott Figure 7-14", [[S("H_{ext}")], [S("VR")]]), knowns)
        elif knowns["belt type"] == "5V" or knowns["belt type"] == "5v":
            logs += solve_pathway((PathType.TABLE_OR_FIGURE, "Mott Figure 7-17", [[S("H_{ext}")], [S("VR")]]), knowns)
        elif knowns["belt type"] == "8V" or knowns["belt type"] == "8v":
            logs += solve_pathway((PathType.TABLE_OR_FIGURE, "Mott Figure 7-16", [[S("H_{ext}")], [S("VR")]]), knowns)
        else:
            raise Exception("unacceptable belt type")
        return logs

    pathways = [

        # Tangential Speed and Input Output Ratio
        (PathType.EQUATION, "Mott Equation pg 255",             Geqn(S("V_{rough}"),        S("n_{in}")*S("D_{in\\,rough}")*sym.pi/12)),
        (PathType.EQUATION, "Mott Equation pg 255",             Geqn(S("V"),                S("n_{in}")*S("D_{in}")*sym.pi/12)),
        (PathType.EQUATION, "General Equation VR",              Geqn(S("VR_{rough}"),       S("n_{in}")/S("n_{out\\,rough}"))),
        (PathType.EQUATION, "General Equation VR",              Geqn(S("VR"),               S("D_{out}")/S("D_{in}"))),
        (PathType.EQUATION, "General Equation VR",              Geqn(S("VR"),               S("n_{in}")/S("n_{out}"))),

        # Geometry
        (PathType.EQUATION, "Mott Equation 7-17",               Geqn(S("CD_{rough}"),       2*S("D_{out}")+1.5*S("D_{in}"))),
        (PathType.EQUATION, "Mott Equation 7-12",               Geqn(S("L_{rough}"),        2*S("CD_{rough}")+1.57*(S("D_{out}")+S("D_{in}"))+(S("D_{out}")-S("D_{in}"))**2/(4*S("CD_{rough}")))),
        (PathType.TABLE_OR_FIGURE, "Mott Table 7-2",            [[S("L")], [S("L_{rough}")]]),
        (PathType.EQUATION, "Mott Equation 7-13-sub",           Geqn(S("B"),                4*S("L")-2*sym.pi*(S("D_{out}")+S("D_{in}")))),
        (PathType.EQUATION, "Mott Equation 7-13",               Geqn(S("CD"),               (S("B") + sym.sqrt(S("B")**2 - 32*(S("D_{out}") - S("D_{in}"))**2))/16)),
        (PathType.EQUATION, "Mott Equation 7-16",               Geqn(S("d"),                (S("CD")**2-((S("D_{out}")-S("D_{in}"))/2)**2)**0.5)),
        (PathType.EQUATION, "Mott Equation 17-14",              Geqn(S("\\theta_{in}"),     sym.pi-2*sym.asin((S("D_{out}")-S("D_{in}"))/S("CD")))),
        (PathType.EQUATION, "Mott Equation 17-15",              Geqn(S("\\theta_{out}"),    sym.pi+2*sym.asin((S("D_{out}")-S("D_{in}"))/S("CD")))),

        # Correction Factor
        (PathType.TABLE_OR_FIGURE, "Mott Table 7-1", [[S("K_s")], ["driven", "driver", "duty time"]]),  # overload factor
        (PathType.TABLE_OR_FIGURE, "Mott Figure 7-18", [[S("C_{\\theta}")], [S("\\theta_{in}")]]),  # angle correction factor
        (PathType.TABLE_OR_FIGURE, "Mott Figure 7-19", [[S("C_L")], ["belt type", S("L")]]),  # length correction factor

        # Torque and Forces
        # (PathType.EQUATION, "Shigley Equation pg 892",                  Geqn(S("T_{in}"),       63025*S("H_{des}")/S("n_{in}"))),  # torque on the input side
        # (PathType.EQUATION, "Shigley Equation section 17-2 (i)",        Geqn(S("F_i"),          (S("F_{1a}") + S("F_2"))/2-S("F_c"))),
        # (PathType.EQUATION, "Shigley Equation section 17-2 (e)",        Geqn(S("F_c"),          (S("V")/60)**2*(S("w")/32.17))),
        # (PathType.EQUATION, "Shigley Equation 17-12",                   Geqn(S("F_{1a}"),       S("b") * S("F_a") * S("C_p")*S("C_v"))),
        # (PathType.EQUATION, "Shigley Equation section 17-2 (h)",        Geqn(S("F_2"),          S("F_{1a}") - 2*S("T_{in}")/S("D_{in}"))),
        # (PathType.EQUATION, "General Equation F1-F2",                   Geqn(S("\\Delta F"),    S("F_{1a}")-S("F_2"))),

        # Power and Selection
        (PathType.TABLE_OR_FIGURE, "Mott Figure 7-13",          [["belt type"], [S("H_{des}"), S("n_{in}")]]),
        (PathType.EQUATION, "General Equation service factor",  Geqn(S("H_{des}"),          S("H_{nom}") * S("K_s"))),
        (PathType.EQUATION, "Mott Equation pg 262",             Geqn(S("H_{all}"),          S("C_{\\theta}")*S("C_L")*(S("H_{tab}")+S("H_{ext}")))),
        (PathType.CUSTOM, "Mott Text pg 257",                   [[S("H_{ext}")], ["belt type", S("VR")]], extra_power),
        (PathType.EQUATION, "Mott Equation pg 262",             Geqn(S("N_{belt}"),         sym.ceiling(S("H_{des}")/S("H_{all}")))),
        (PathType.CUSTOM, "Mott Text pg 257", [[S("D_{in}"), S("D_{out}"), S("H_{tab}")], ["belt type", S("VR_{rough}"), S("D_{in\\,rough}")]], sheave_selection),
        (PathType.EQUATION, "General Equation safety factor",   Geqn(S("n_{sf}"),           S("H_{des}")/(S("N_{belt}")*S("H_{all}")))),
    ]

    return pathways

