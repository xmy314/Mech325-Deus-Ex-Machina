from mech325.infrastructure import *


def retrieve_ballscrew_information():
    print("Retrieving information for solving bolts questions from Shigley.")
    print("Please note that the following code is not tested.")

    pathways = [
        (PathType.TABLE_OR_FIGURE, "Mott Figure 17-8", [[S("d"), S("L")], [S("F"), S("L_d")]]),
        (PathType.EQUATION, "Mott Equation 17-13", Geqn(S("T_u"), 0.177*S("F")*S("L"))),
        (PathType.EQUATION, "Mott Equation 17-14", Geqn(S("T_b"), 0.143*S("F")*S("L"))),
        (PathType.EQUATION, "Mott Equation TODO", Geqn(S("n"), S("V")/S("L")*60)),
        (PathType.EQUATION, "Mott Equation TODO", Geqn(S("P"), S("T_u")*S("n")/63025)),


        (PathType.TABLE_OR_FIGURE, "Thomson_Ball_Screw life", [[S("L_{d\\expected}")], [S("d"), S("l"), S("F")]]),

        (PathType.EQUATION, "Mott Equation TODO", Geqn(S("F_{des}"), S("N")*S("F"))),
        (PathType.TABLE_OR_FIGURE, "Thomson_Ball_Screw buckle", [[S("L_{length\\,max}")], [S("d"), S("l"), S("F_{des}")]]),

        (PathType.TABLE_OR_FIGURE, "Thomson_Ball_Screw speed", [[S("V_{max}")], [S("d"), S("l"), S("F")]]),
    ]

    return pathways
