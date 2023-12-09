from mech325.infrastructure import *


def retrieve_wormgeam_information():
    print("Retrieving information for solving bevel gear questions from Mott.")
    print("Please note that the following code is not tested.")

    def compute_friction_coefficient(knowns):
        logs = []
        # page 457
        if knowns[S("v_s")] == 0:
            logs.append("Static condition")
            logs += solve_pathway((PathType.EQUATION, "Mott Equation pg 457",  Geqn(S("\\mu"), 0.15)), knowns)
        elif knowns[S("v_s")] < 10:
            logs.append("Low speed")
            logs += solve_pathway((PathType.EQUATION, "Mott Equation 10-26",  Geqn(S("\\mu"), 0.124*sym.exp(-0.074*(S("v_s")**0.645)))), knowns)
        else:
            logs.append("High speed")
            logs += solve_pathway((PathType.EQUATION, "Mott Equation 10-26",  Geqn(S("\\mu"), 0.103*sym.exp(-0.110*(S("v_s")**0.450))+0.012)), knowns)
        return logs

    def compute_Cv(knowns):
        logs = []
        if (knowns[S("v_s")] < 700):
            logs += solve_pathway((PathType.EQUATION, "Mott Equation 10-49",  Geqn(S("C_v"), 0.659*sym.exp(-0.0011*S("v_s"))), knowns))
        elif (knowns[S("v_s")] < 3000):
            logs += solve_pathway((PathType.EQUATION, "Mott Equation 10-49",  Geqn(S("C_v"), 13.31*(S("v_s")**(-0.571))), knowns))
        else:
            logs += solve_pathway((PathType.EQUATION, "Mott Equation 10-49",  Geqn(S("C_v"), 65.52*(S("v_s")**(-0.774))), knowns))
        return logs

    def compute_Fe(knowns):
        logs = []
        if (knowns[S("F")] > 0.67 * knowns[S("D_{in}")]):
            logs.append("Wormgear face width is wider than 2/3 of worm diameter. As a result, the effective face width of 2/3 worm diameter is used.")
            knowns[S("F_e")] = 0.67 * knowns[S("D_{in}")]
        else:
            logs.append("Wormgear face width is thinned than 2/3 of worm diameter. As a result, the effective face is the face width.")
            knowns[S("F_e")] = knowns[S("F")]
        return logs

    pathways = [
        # get design power is not necessary as there is no table or figure that can be used to selectct diametrical pitch.

        # Speed and Input Output Ratio
        (PathType.EQUATION, "Mott Equation pg 333",             Geqn(sym.tan(S("v_{t\\,in}")), (sym.pi*S("D_{in}")*S("n_{in}")/12))),
        (PathType.EQUATION, "Mott Equation pg 334",             Geqn(sym.tan(S("v_{t\\,out}")), (sym.pi*S("D_{out}")*S("n_{out}")/12))),
        (PathType.EQUATION, "Mott Equation 10-24",              Geqn(sym.tan(S("v_s")), S("v_{t\\,out}")/sym.sin(S("\\lambda")))),

        (PathType.EQUATION, "General Equation VR",              Geqn(S("VR_{rough}"),       S("n_{in}")/S("n_{out\\,rough}"))),
        (PathType.EQUATION, "General Equation VR",              Geqn(S("VR"),               S("n_{in}")/S("n_{out}"))),
        (PathType.EQUATION, "General Equation VR",              Geqn(S("VR"),               S("N_{out}")/S("N_{in}"))),
        (PathType.EQUATION, "General Equation GR",              Geqn(S("GR"),               S("VR"))),
        (PathType.EQUATION, "General Equation GR",              Geqn(S("m_G"),              S("VR"))),

        # Geometry
        (PathType.EQUATION, "Mott Equation 8-20",               Geqn(S("p"), sym.pi*S("D_{out}")/S("N_{out}"))),
        (PathType.EQUATION, "Mott Equation 8-14",               Geqn(S("p_n"), S("p")*sym.cos("lambda"))),
        (PathType.EQUATION, "Mott Equation 8-21",               Geqn(S("P_d"), S("N_{out}")/S("D_{out}"))),
        (PathType.EQUATION, "Mott Equation 8-23",               Geqn(S("Lead"), S("N_{in}")*S("p"))),
        (PathType.EQUATION, "Mott Equation 8-23",               Geqn(sym.tan(S("\\lambda")), S("Lead")/(sym.pi*S("D_{in}")))),
        (PathType.EQUATION, "Mott Equation 8-26",               Geqn(sym.tan(S("\\phi_n")), sym.tan(S("\\phi_t"))*sym.cos(S("\\lambda")))),

        # Torque and Force

        (PathType.CUSTOM, "Mott Text pg 457",                          [[S("\\mu")], [S("v_s")]], compute_friction_coefficient),

        (PathType.EQUATION, "General Equation Torque input shaft",     Geqn(S("T_{in}"), 63025*S("H_{in}")/S("n_{in}"))),
        (PathType.EQUATION, "General Equation Torque input shaft",     Geqn(S("T_{out}"), 63025*S("H_{out}")/S("n_{out}"))),

        (PathType.EQUATION, "Mott Equation 10-29",                      Geqn(S("W_{t\\,out}"), 2*S("T_{out}")/S("D_{out}"))),
        (PathType.EQUATION, "Mott Equation 10-30",                      Geqn(S("W_{x\\,out}"), S("W_{t\\,out}") *
                                                                             (sym.cos(S("\\phi_n"))*sym.sin(S("\\lambda"))+S("\\mu")*sym.cos(S("\\lambda"))) /
                                                                             (sym.cos(S("\\phi_n"))*sym.cos(S("\\lambda"))-S("\\mu")*sym.sin(S("\\lambda")))
                                                                             )),
        (PathType.EQUATION, "Mott Equation 10-31",                      Geqn(S("W_{r\\,out}"), S("W_{t\\,out}") *
                                                                             (sym.sin(S("\\phi_n"))) /
                                                                             (sym.cos(S("\\phi_n"))*sym.cos(S("\\lambda"))-S("\\mu")*sym.sin(S("\\lambda")))
                                                                             )),
        (PathType.EQUATION, "Mott Equation 10-23",                       Geqn(S("W_{t\\,in}"), S("W_{x\\,out}"))),
        (PathType.EQUATION, "Mott Equation 10-23",                       Geqn(S("W_{x\\,in}"), S("W_{t\\,out}"))),
        (PathType.EQUATION, "Mott Equation 10-23",                       Geqn(S("W_{r\\,in}"), S("W_{r\\,out}"))),

        (PathType.EQUATION, "Mott Equation 10-32",                      Geqn(S("W_f"), S("W_{t\\,out}") *
                                                                             (S("\\mu")) /
                                                                             (sym.cos(S("\\phi_n"))*sym.cos(S("\\lambda"))-S("\\mu")*sym.sin(S("\\lambda")))
                                                                             )),

        # Stress (skipped for no use in the process of selection)

        # Power
        (PathType.EQUATION, "Mott Equation 10-33",                      Geqn(S("H_{loss}"), S("v_s") * sym.sin(S("W_f")) / 33000)),
        (PathType.EQUATION, "Mott Equation 10-34",                      Geqn(S("H_{out}"), S("H_{in}")-S("H_{loss}"))),
        (PathType.EQUATION, "Mott Equation 10-35",                      Geqn(S("\\eta"), S("H_{out}")/S("H_{in}"))),

        # Rated Load
        (PathType.TABLE_OR_FIGURE, "Mott Table 10-27",  [[S("C_s")], [S("P_d")]]),
        (PathType.TABLE_OR_FIGURE, "Mott Table 10-28",  [[S("C_m")], [S("m_G")]]),
        (PathType.CUSTOM, "Mott Text pg-461",      [[S("F_e")], [S("F"), S("D_{in}")]], compute_Fe),
        (PathType.CUSTOM, "Mott Text pg-463",      [[S("C_v")], [S("v_s")]], compute_Cv),
        (PathType.EQUATION, "Mott Equation 10-42",      Geqn(S("W_{tR}"), S("C_s")*(S("D_{out}")**0.8)*S("C_m")*S("F_e")*S("C_v"))),
    ]

    return pathways
