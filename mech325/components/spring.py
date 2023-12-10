from mech325.infrastructure import *


def retrieve_spring_information(knowns):
    print("Retrieving information for solving spring questions from Shigley.")
    print("Please note that the following code is not tested.")

    pathways = []

    if knowns["spring end"].lower() == "plain":
        pathways.append((PathType.EQUATION, "Shigley Table 10-1", Geqn(S("N_e"), 0)))
        pathways.append((PathType.EQUATION, "Shigley Table 10-1", Geqn(S("N_t"), S("N_a"))))
        pathways.append((PathType.EQUATION, "Shigley Table 10-1", Geqn(S("L_f"), S("p")*S("N_a")+S("d"))))
        pathways.append((PathType.EQUATION, "Shigley Table 10-1", Geqn(S("L_s"), S("d")*(S("N_t")+1))))
    elif knowns["spring end"].lower() == "plain and ground":
        pathways.append((PathType.EQUATION, "Shigley Table 10-1", Geqn(S("N_e"), 1)))
        pathways.append((PathType.EQUATION, "Shigley Table 10-1", Geqn(S("N_t"), S("N_a")+1)))
        pathways.append((PathType.EQUATION, "Shigley Table 10-1", Geqn(S("L_f"), S("p")*(S("N_a")+1))))
        pathways.append((PathType.EQUATION, "Shigley Table 10-1", Geqn(S("L_s"), S("d")*S("N_t"))))
    elif knowns["spring end"].lower() == "square":
        pathways.append((PathType.EQUATION, "Shigley Table 10-1", Geqn(S("N_e"), 2)))
        pathways.append((PathType.EQUATION, "Shigley Table 10-1", Geqn(S("N_t"), S("N_a")+2)))
        pathways.append((PathType.EQUATION, "Shigley Table 10-1", Geqn(S("L_f"), S("p")*S("N_a")+3*S("d"))))
        pathways.append((PathType.EQUATION, "Shigley Table 10-1", Geqn(S("L_s"), S("d")*(S("N_t")+1))))
    elif knowns["spring end"].lower() == "square and ground":
        pathways.append((PathType.EQUATION, "Shigley Table 10-1", Geqn(S("N_e"), 2)))
        pathways.append((PathType.EQUATION, "Shigley Table 10-1", Geqn(S("N_t"), S("N_a")+2)))
        pathways.append((PathType.EQUATION, "Shigley Table 10-1", Geqn(S("L_f"), S("p")*S("N_a")+2*S("d"))))
        pathways.append((PathType.EQUATION, "Shigley Table 10-1", Geqn(S("L_s"), S("d")*S("N_t"))))
    else:
        raise Exception("spring end is not expected value, choose between [Plain, Plain and Ground, Square, Square and Ground]")

    # random exponentials that are unit dependent is annoying.
    if knowns["unit system"].lower() == "si":
        pathways.append((PathType.EQUATION, "Shigley Table 10-4", Geqn(S("S_{ut}"), S("A")/(S("d")*1000)**S("m"))))
    elif knowns["unit system"].lower() == "imperial":
        pathways.append((PathType.EQUATION, "Shigley Table 10-4", Geqn(S("S_{ut}"), S("A")/(S("d"))**S("m"))))
    else:
        raise Exception("unit system is not expected value, choose between [si, imperial]")

    pathways += [
        (PathType.EQUATION, "Geometry", Geqn(S("D"), S("D_{in}")+S("d"))),
        (PathType.EQUATION, "Geometry", Geqn(S("D"), S("D_{out}")-S("d"))),
        (PathType.EQUATION, "Geometry", Geqn(S("C"), S("D")/S("d"))),

        (PathType.TABLE_OR_FIGURE, "Shigley Table 10-4", [[S("A"), S("m")], ["Material"]]),
        (PathType.TABLE_OR_FIGURE, "Shigley Table 10-5", [[S("G")], ["Material", S("d")]]),
        (PathType.TABLE_OR_FIGURE, "Shigley Table 10-6", [[S("\\frac{S_{sy}}{S_{ut}}")], ["Material"]]),
        (PathType.EQUATION, "Shigley Table 10-6", Geqn(S("S_{sy}"), S("\\frac{S_{sy}}{S_{ut}}")*S("S_{ut}"))),

        (PathType.EQUATION, "Shigley Equation 10-5", Geqn(S("K_B"), (4*S("C")+2)/(4*S("C")-3))),

        (PathType.EQUATION, "Shigley Eqaution 10-7", Geqn(S("\\tau"), S("K_B")*(8*S("F")*S("D"))/(sym.pi*S("d")**3))),

        (PathType.EQUATION, "Shigley Eqaution 10-7", Geqn(S("\\tau_s"), S("K_B")*(8*S("F_s")*S("D"))/(sym.pi*S("d")**3))),

        (PathType.EQUATION, "Shigley Equation yield safety", Geqn(S("n_y"), S("S_{sy}")/S("\\tau_s"))),

        (PathType.EQUATION, "Hooke's law", Geqn(S("k"), S("F_o")/S("y_o"))),
        (PathType.EQUATION, "Shigley Eqaution 10-9", Geqn(S("k"), S("d")**4*S("G")/(8*S("D")**3*S("N_a")))),

        (PathType.EQUATION, "Hooke's law", Geqn(S("F_s"), S("k")*(S("L_f")-S("L_s")))),

        (PathType.EQUATION, "Shigley Equation 10-17", Geqn(S("F_s"), (1+S("\\chi"))*S("F_{max}"))),

        (PathType.TABLE_OR_FIGURE, "Shigley Eqaution 10-2", [[S("\\alpha")], ["end condition"]]),
        (PathType.EQUATION, "Shigley Eqaution 10-13", Geqn(S("L_{f|crit}"), 2.63*S("D")/S("\\alpha"))),

    ]

    return pathways
