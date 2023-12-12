from mech325.infrastructure import *


def retrieve_shaft_point_information_mott():
    print("Retrieving information for selecting shaft diameter from Mott.")
    print("Please note that this only solves for one point on the shaft.")

    def diameter_iteration(knowns):

        logs = []
        if 1.2*knowns[S("D_{iter}")] > knowns[S("D_{min}")]:
            logs.append(f'Since $D_{{iter}} = {knowns[S("D_{iter}")]:7.2f} \\gtrapprox {knowns[S("D_{min}")]:7.2f} = D_{{min}}$, the current selected diameter is good.')
            knowns[S("D_{req}")] = knowns[S("D_{min}")]
        else:
            logs.append(f'Since $D_{{iter}} = {knowns[S("D_{iter}")]:7.2f} < {knowns[S("D_{min}")]:7.2f} = D_{{min}}$, let {knowns[S("D_{min}")]:7.2f} be the new $D_{{iter}}$ to continue iteration.')
            knowns[S("D_{iter}")] = knowns[S("D_{min}")]
            discards = [S("C_s"), S("s_n'"), S("D_{min\\,s}"), S("D_{min\\,t}"), S("D_{min}")]
            for discard in discards:
                if discard in knowns:
                    knowns.pop(discard)
        return logs

    def cs_mock(knowns):
        knowns[S("C_s")] = round(1.88003**(knowns[S("D_{iter}")]**(-0.0846996))-1.00099, 2)

    def shear_wrapper(knowns):
        logs = []
        if knowns[S("V")] != 0:
            logs += solve_pathway((PathType.EQUATION, "Mott 12-16", Geqn(S("D_{min\\,s}"), sym.sqrt(2.94*S("K_t")*S("V")*S("N")/S("s_n'")))), knowns)
        else:
            knowns[S("D_{min\\,s}")] = 0
        return logs

    def moment_wrapper(knowns):
        logs = []
        if knowns[S("M")] != 0 or knowns[S("T")] != 0:
            logs += solve_pathway((PathType.EQUATION, "Mott 12-24", Geqn(
                S("D_{min\\,t}"),
                sym.cbrt(
                    32*S("N")/sym.pi *
                    sym.sqrt(
                        (S("K_t")*S("M")/S("s_n'"))**2 +
                        3/4*(S("T")/S("s_y"))**2
                    )
                )
            )), knowns)
        else:
            knowns[S("D_{min\\,t}")] = 0
        return logs

    pathways = [
        (PathType.EQUATION, "Make a Guess", Geqn(S("D_{iter}"), 2)),
        (PathType.TABLE_OR_FIGURE, "Mott Table Appendix-3", [[S("s_u"), S("s_y")], ["SAE"]]),
        (PathType.TABLE_OR_FIGURE, "Mott Figure 5-11", [[S("s_n")], [S("s_u"), "surface condition"]]),
        (PathType.EQUATION, "Mott Equation pg-178", Geqn(S("C_m"), 1)),
        (PathType.EQUATION, "Mott Equation pg-178", Geqn(S("C_{st}"), 1)),
        (PathType.TABLE_OR_FIGURE, "Mott Table 5-3", [[S("C_R")], ["Reliability"]]),
        (PathType.MOCK_TABLE_OR_FIGURE, "Mott Figure 5-12", [[S("C_s")], [S("D_{iter}")]], cs_mock),
        (PathType.EQUATION, "Mott Equation 5-21", Geqn(S("s_n'"), S("s_n")*S("C_m")*S("C_{st}")*S("C_R")*S("C_s"))),

        (PathType.CUSTOM, "Shear Wrapper", [[S("D_{min\\,s}")], [S("K_t"), S("V"), S("N"), S("s_n'")]], shear_wrapper),
        (PathType.CUSTOM, "Moment Wrapper", [[S("D_{min\\,t}")], [S("K_t"), S("M"), S("T"), S("N"), S("s_n'"), S("s_y")]], moment_wrapper),

        (PathType.EQUATION, "Pick Maximum", Geqn(
            S("D_{min}"),
            sym.Max(S("D_{min\\,s}"), S("D_{min\\,t}"))
        )),

        (PathType.CUSTOM, "Diameter Iteration", [[S("D_{req}")], [S("D_{iter}"), S("D_{min}")]], diameter_iteration)
    ]

    return pathways
