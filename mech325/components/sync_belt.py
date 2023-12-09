from mech325.infrastructure import *


def retrieve_syncbelt_information():
    print("Retrieving information for solving syncronous belt questions from Mott.")

    def width_selection(knowns):
        logs = []
        # return path to follow if ready, else return what is needed.
        if knowns[S("H_{tab\\,30}")]*knowns[S("C_L")] > knowns[S("H_{des}")]:
            logs += solve_pathway((PathType.EQUATION, "Through comparison", Geqn(S("H_{tab}"), S("H_{tab\\,30}"))), knowns)
            logs += solve_pathway((PathType.EQUATION, "Through comparison", Geqn(S("W"), 30)), knowns)
        elif knowns[S("H_{tab\\,50}")]*knowns[S("C_L")] > knowns[S("H_{des}")]:
            logs += solve_pathway((PathType.EQUATION, "Through comparison ", Geqn(S("H_{tab}"), S("H_{tab\\,50}"))), knowns)
            logs += solve_pathway((PathType.EQUATION, "Through comparison", Geqn(S("W"), 50)), knowns)
        else:
            raise Exception("no_valid_width_table")
        return logs

    pathways = [

        # Input Output Ratio
        (PathType.EQUATION, "General Equation VR",              Geqn(S("VR_{rough}"),       S("n_{in}")/S("n_{out\\,rough}"))),
        (PathType.EQUATION, "General Equation VR",              Geqn(S("VR"),               S("N_{out}")/S("N_{in}"))),
        (PathType.EQUATION, "General Equation VR",              Geqn(S("VR"),               S("D_{out}")/S("D_{in}"))),
        (PathType.EQUATION, "General Equation VR",              Geqn(S("VR"),               S("n_{in}")/S("n_{out}"))),

        # Geometry
        (PathType.TABLE_OR_FIGURE, "Mott Table 7-5",  [["minimum input bushing size", "maximum input bushing size"], ["input shaft diameter"]]),
        (PathType.TABLE_OR_FIGURE, "Mott Table 7-5",  [["minimum output bushing size", "maximum output bushing size"], ["output shaft diameter"]]),
        (PathType.TABLE_OR_FIGURE, "Mott Table 7-4",  [[S("N_{in\\,min}"), S("N_{in\\,max}")], ["minimum input bushing size", "maximum input bushing size", "maximum input flange size"]]),
        (PathType.TABLE_OR_FIGURE, "Mott Table 7-4",  [[S("N_{out\\,min}"), S("N_{out\\,max}")], ["minimum output bushing size", "maximum output bushing size", "maximum output flange size"]]),
        (PathType.TABLE_OR_FIGURE, "Mott Table 7-4",  [["input bushing size"], [S("N_{in}"), S("W")]]),
        (PathType.TABLE_OR_FIGURE, "Mott Table 7-4",  [["output bushing size"], [S("N_{out}"), S("W")]]),
        (PathType.TABLE_OR_FIGURE, "Mott Table 7-7",  [[S("N_{in}"), S("N_{out}"), S("CD"), "belt number"], [S("VR_{rough}"), S("N_{in\\,min}"), S("N_{in\\,max}"), S("N_{out\\,min}"), S("N_{out\\,max}"), S("CD_{nom}")]]),

        # Correction Factors
        (PathType.TABLE_OR_FIGURE, "Mott Table 7-8",  [[S("K_s")], ["driven", "driver", "duty time"]]),
        (PathType.TABLE_OR_FIGURE, "Mott Table 7-11", [[S("C_L")], ["belt number"]]),

        # Torque and Forces
        (PathType.EQUATION, "General Equation Torque",  Geqn(S("T_{in}"),           63025*S("H_{des}")/S("n_{in}"))),
        (PathType.EQUATION, "General Equation Torque",  Geqn(S("T_{out}"),          63025*S("H_{des}")/S("n_{out}"))),
        (PathType.EQUATION, "General Equation Torque",  Geqn(S("F"),                2*S("T_{in}")/S("D_{in}"))),

        # Power and Selection
        (PathType.TABLE_OR_FIGURE, "Mott Table 7-9",    [[S("H_{tab\\,30}")], [S("N_{in}"), S("n_{in}")]]),
        (PathType.TABLE_OR_FIGURE, "Mott Table 7-10",   [[S("H_{tab\\,50}")], [S("N_{in}"), S("n_{in}")]]),
        (PathType.EQUATION, "General Equation service factor",  Geqn(S("H_{des}"),          S("H_{nom}") * S("K_s"))),
        (PathType.TABLE_OR_FIGURE, "Mott Figure 7-27",  [["pitch"], [S("n_{in}"), S("H_{des}")]]),
        (PathType.CUSTOM, "Mott Text pg 275",           [[S("H_{tab}"), S("W")], [S("H_{tab\\,30}"), S("H_{tab\\,50}"), S("C_L"), S("H_{des}")]], width_selection),
        (PathType.EQUATION, "Mott Equation pg 272",             Geqn(S("H_{all}"),          S("H_{tab}")*S("C_L"))),

        (PathType.EQUATION, "General Equation safety factor",   Geqn(S("n_{sf}"),           S("H_{des}")/S("H_{all}"))),
    ]

    return pathways
