from mech325.infrastructure import *


def retrieve_flatbelt_information():
    print("Retrieving information for solving flat belt questions from Shigley.")
    print("Please note that it only solves upper operation limit due to stress but not lower operation limit from friction.")

    def compute_cv(knowns):
        logs = []
        # return path to follow if ready, else return what is needed.
        if not "leather" in knowns["belt"]:
            pathway =(PathType.EQUATION, "Shigley Text pg 891", Geqn(S("C_v"), 1))
        else:
            pathway =(PathType.TABLE_OR_FIGURE, "Shigley Figure 17-9", [[S("C_v")], [S("V")]])
        logs += solve_pathway(pathway, knowns)
        return logs

    # type, name, (output,input)
    pathways = [
        # Component Property
        (PathType.TABLE_OR_FIGURE, "Shigley Table 17-2", [[S("t"), S("D_{in\\,min}"), S("F_a"), S("\\gamma"), S("f")], ["belt"]]),
        (PathType.EQUATION, "General Equation lbf/ft",                  Geqn(S("w"),            12*S("\\gamma")*S("b")*S("t"))),  # weight per length [lbs/feet]

        # Tangential Speed and Input Output Ratio
        (PathType.EQUATION, "Shigley Equation pg 887",         Geqn(S("V"),            S("n_{in}")*S("D_{in}")*sym.pi/12)),
        (PathType.EQUATION, "General Equation VR",             Geqn(S("VR"),           S("D_{out}")/S("D_{in}"))),
        (PathType.EQUATION, "General Equation VR",             Geqn(S("VR"),           S("n_{in}")/S("n_{out}"))),

        # Geometry
        (PathType.EQUATION, "Shigley Equation 17-1",           Geqn(S("\\phi_{in}"),   sym.pi-2*sym.asin((S("D_{out}")-S("D_{in}"))/S("CD")))),
        (PathType.EQUATION, "Shigley Equation 17-1",           Geqn(S("\\phi_{out}"),  sym.pi+2*sym.asin((S("D_{out}")-S("D_{in}"))/S("CD")))),
        (PathType.EQUATION, "Shigley Equation 17-2",           Geqn(S("L"),            (4*S("CD")**2 - (S("D_{out}") - S("D_{in}"))**2)**(1/2) + (S("D_{in}")*S("\\phi_{in}")+S("D_{out}")*S("\\phi_{out}"))/2)),
        (PathType.EQUATION, "Shigley Equation 17-13",          Geqn(S("dip"),          S("CD")**2*S("w")/(96*S("F_i")))),

        # Correction Factors
        (PathType.TABLE_OR_FIGURE, "Shigley Table 17-4", [[S("C_p")], ["belt", S("D_{in}")]]),  # based on pulley diameter
        (PathType.CUSTOM, "Shigley Text pg 891", [[S("C_v")], ["belt", S("V")]], compute_cv),  # based on material

        # Torque and Forces
        (PathType.EQUATION, "Shigley Equation pg 892",                  Geqn(S("T_{in}"),       63025*S("H_{des}")/S("n_{in}"))),  # torque on the input side
        (PathType.EQUATION, "Shigley Equation section 17-2 (i)",        Geqn(S("F_i"),          (S("F_{1a}") + S("F_2"))/2-S("F_c"))),
        (PathType.EQUATION, "Shigley Equation section 17-2 (e)",        Geqn(S("F_c"),          (S("V")/60)**2*(S("w")/32.17))),
        (PathType.EQUATION, "Shigley Equation 17-12",                   Geqn(S("F_{1a}"),       S("b") * S("F_a") * S("C_p")*S("C_v"))),
        (PathType.EQUATION, "Shigley Equation section 17-2 (h)",        Geqn(S("F_2"),          S("F_{1a}") - 2*S("T_{in}")/S("D_{in}"))),
        (PathType.EQUATION, "General Equation F1-F2",                   Geqn(S("\\Delta F"),    S("F_{1a}")-S("F_2"))),

        # Power and Selection
        (PathType.EQUATION, "Shigley Equation section 17-2 (j)",        Geqn(S("H_{all}"),      (S("\\Delta F")*S("V"))/33000)),
        (PathType.EQUATION, "Shigley Equation pg 893",                  Geqn(S("H_{des}"),      S("H_{nom}") * S("K_s") * S("n_d"))),
        (PathType.EQUATION, "General Equation safety factor",           Geqn(S("n_{sf}"),       S("H_{all}")/S("H_{des}"))),
    ]

    return pathways
