from mech325.infrastructure import *


def retrieve_shaft_point_information_shigley():
    print("Retrieving information for solving shaft stresses with mixed loading questions from Shigley.")
    print("Please note that it only solves for stresses and doesn't do selection or iteration yet.")

    def find_kb(knowns):
        # unit is in inches
        logs = []
        if 0.3 <= knowns[S("d")] and knowns[S("d")] < 2:
            logs += solve_pathway(PathType.EQUATION, "Shigley Equation 6-19", Geqn(S("K_b"), 0.879*(knowns[S("d")])**(-0.107)))
        elif knowns[S("d")] < 10:
            logs += solve_pathway(PathType.EQUATION, "Shigley Equation 6-19", Geqn(S("K_b"), 0.91*(knowns[S("d")])**(-0.157)))
        return logs

    pathways = [
        # get design power is not necessary as there is no table or figure that can be used to selectct diametrical pitch.
        (PathType.TABLE_OR_FIGURE, "Shigley Figure 6-26", [[S("q_b")], [S("r_{notch}"), S("S_{ut}")]]),
        (PathType.TABLE_OR_FIGURE, "Shigley Figure 6-27", [[S("q_s")], [S("r_{notch}"), S("S_{ut}")]]),
        (PathType.EQUATION, "Shigle Equation 6-31a", Geqn(S("K_{fb}"), 1+S("q_b")*(S("K_{tb}")-1))),
        (PathType.EQUATION, "Shigle Equation 6-31b", Geqn(S("K_{fs}"), 1+S("q_s")*(S("K_{ts}")-1))),

        (PathType.EQUATION, "Shigley Equation 6-10", Geqn(S("S_e'"), sym.Min(100, S("S_{ut}")/2))),  # unit is in ksi
        (PathType.TABLE_OR_FIGURE, "Shigley Figure 6-24", [[S("K_a")], [S("S_{ut}")]]),
        (PathType.CUSTOM, "Shigley Figure 6-19", [[S("K_b")], [S("d")]], find_kb),
        (PathType.EQUATION, "Shigley Equation 6-25", Geqn(S("K_c"), 1)),  # for vast majority of the time, the alternating load is the bending moment.
        (PathType.EQUATION, "Assumed At Room Temperature", Geqn(S("K_d"), 1)),  # assume room temperature
        (PathType.TABLE_OR_FIGURE, "Shigley Table 6-4", [[S("K_e")], [S("R")]]),
        (PathType.EQUATION, "Assumed", Geqn(S("K_f"), 1)),

        (PathType.EQUATION, "Shigley Equation 6-10", Geqn(S("S_e"), S("K_a")*S("K_b")*S("K_c")*S("K_d")*S("K_e")*S("K_f")*S("S_e'"))),  # unit is in ksi
        (PathType.EQUATION, "Shigley Equation 7-6a", Geqn(
            S("A"),
            sym.sqrt(
                (8*S("K_{fb}")*S("M_a"))**2 +
                48*(S("K_{fs}")*S("T_a"))**2
            )/1000
        )),
        (PathType.EQUATION, "Shigley Equation 7-6b", Geqn(
            S("B"),
            sym.sqrt(
                (8*S("K_{fb}")*S("M_m"))**2 +
                48*(S("K_{fs}")*S("T_m"))**2
            )/1000
        )),

        # The commented out pathes are a variation of the above two lines but including axial loads.
        # (PathType.EQUATION, "Shigley Equation 7-6a", Geqn(
        #     S("A"),
        #     sym.sqrt(
        #         (8*S("K_{fb}")*S("M_a")+S("K_{fa}")*S("F_a")*S("d"))**2 +
        #         48*(S("K_{fs}")*S("T_a"))**2
        #     )/1000
        # )),
        # (PathType.EQUATION, "Shigley Equation 7-6b", Geqn(
        #     S("B"),
        #     sym.sqrt(
        #         (8*S("K_{fb}")*S("M_m")+S("K_{fa}")*S("F_m")*S("d"))**2 +
        #         48*(S("K_{fs}")*S("T_m"))**2
        #     )/1000
        # )),

        (PathType.EQUATION, "DE-Goodman", Geqn(
            S("n_{f\\,Goodman}"),
            (sym.pi/4)
            * S("d")**3
            * (S("A")/S("S_e")+S("B")/S("S_{ut}"))**-1
        )),

        # # The commented out Pathways Below are different Fatigue Failure Criteria.
        (PathType.EQUATION, "Shigley Equation 6-44", Geqn(S("\\tilde{\\sigma_f}"), S("S_{ut}")+50)),  # unit is in ksi
        (PathType.EQUATION, "DE-Morrow", Geqn(
            S("n_{f\\,Morrow}"),
            (sym.pi/4)
            * S("d")**3
            * (S("A")/S("S_e")+S("B")/S("\\tilde{\\sigma_f}"))**-1
        )),

        (PathType.EQUATION, "DE-Gerber", Geqn(
            S("n_{f\\,Gerber}"),
            (sym.pi/8)
            * S("d")**3
            * S("S_e")/S("A")
            * (
                1
                + sym.sqrt(
                    1
                    + (2*S("B")*S("S_e")/(S("A")*S("S_{ut}")))**2
                )**(1/2)
            )**-1
        )),

        (PathType.EQUATION, "DE-SWT", Geqn(
            S("n_{f\\,SWT}"),
            (sym.pi/16)
            * S("d")**3
            * S("S_e")/(S("A")**2+S("A")*S("B"))**(1/2)
        )),

        (PathType.EQUATION, "von Mises", Geqn(
            S("n_y"),
            (
                (
                    32*S("K_f")*(S("M_m")+S("M_a"))
                    / (sym.pi*S("d")**3)
                )**2
                + 3*(
                    32*S("K_{fs}")*(S("T_m")+S("T_a"))
                    / (sym.pi*S("d")**3)
                )**2
            )**(1/2)
        )),
    ]

    return pathways
