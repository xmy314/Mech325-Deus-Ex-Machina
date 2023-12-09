from mech325.infrastructure import *


def retrieve_bcbearingradial_information():
    print("Retrieving information for solving ball and cylinderical bearing with radial loading only questions from Shigley.")

    def find_v(knowns):
        logs = []
        if "inner" in knowns["rolling race"]:
            knowns[S("v")] = 1
            logs.append("Since inner race is rotating, $v=1$.")
        elif "outer" in knowns["rolling race"]:
            knowns[S("v")] = 1.2
            logs.append("Since outer race is rotating, $v=1.2$.")
        else:
            raise Exception("invalid \"rolling race\"")
        return logs

    def find_a(knowns):
        logs = []
        if "ball" in knowns["rolling element type"]:
            knowns[S("a")] = 3
            logs.append("Since this is a ball bearing, $a=3$.")
        elif "cylinder" in knowns["rolling element type"]:
            knowns[S("a")] = 3.3
            logs.append("Since this is a ball bearing, $a=3.3$.")
        else:
            raise Exception("invalid \"rolling element type\"")
        return logs

    def find_bore(knowns):
        logs = []
        if "ball" in knowns["rolling element type"]:
            logs += solve_pathway((PathType.TABLE_OR_FIGURE, "Shigley Table 11-2", [[S("Bore"), S("C_{10}")], [S("C_{10\\,min}")]]), knowns)
        elif "cylinder" in knowns["rolling element type"]:
            logs += solve_pathway((PathType.TABLE_OR_FIGURE, "Shigley Table 11-3", [[S("Bore"), S("C_{10}")], [S("C_{10\\,min}")]]), knowns)
        else:
            raise Exception("invalid \"rolling element type\"")
        return logs

    pathways = [
        # get design power is not necessary as there is no table or figure that can be used to selectct diametrical pitch.
        (PathType.EQUATION, "Shigely Equation 11-text-pg-581", Geqn(S("x_d"), S("L_d")/S("L_{10}"))),
        (PathType.EQUATION, "Shigley Equation 11-3 (b)", Geqn(S("L_d"), S("L_{hr}")*60*S("n"))),
        (PathType.TABLE_OR_FIGURE, "Shigley Table 11-5", [[S("a_f")], ["load type"]]),
        (PathType.CUSTOM, "Shigley text", [[S("v")], ["rolling race"]], find_v),
        (PathType.CUSTOM, "Shigley text", [[S("a")], ["rolling element type"]], find_a),
        (PathType.EQUATION, "Shigley Equation 11-9", Geqn(S("C_{10\\,min}"),  S("a_f")*S("v")*S("F")*((S("x_d")/(S("x_0")+(S("\\theta")-S("x_0"))*(sym.ln(1/S("R_d"))**(1/S("b")))))**(1/S("a"))))),
        (PathType.EQUATION, "Shigley Equation 11-9", Geqn(S("C_{10}"),        S("a_f")*S("v")*S("F")*((S("x_d")/(S("x_0")+(S("\\theta")-S("x_0"))*(sym.ln(1/S("R"))**(1/S("b")))))**(1/S("a"))))),
        (PathType.CUSTOM, "Find bore", [[S("Bore"), S("C_{10}")], [S("C_{10\\,min}"), "rolling element type"]], find_bore),
    ]

    return pathways

