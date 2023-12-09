from mech325.infrastructure import *


def retrieve_key_information_mott():
    print("Retrieving information for key selection from mott.")
    print("Please note that this only solves for one point on the shaft.")

    def round_l_to_quarter(knowns):
        logs = []
        knowns[S("L")] = math.ceil(4*knowns[S("L_{min}")])/4
        logs.append(f'Round L up to the nearest quarter: $$L={touch(knowns[S("L")])}$$')
        return logs

    pathways = [
        (PathType.TABLE_OR_FIGURE, "Mott Table 11-1", [[S("W"), S("H")], [S("D")]]),
        (PathType.TABLE_OR_FIGURE, "Mott Table 11-4", [["SAE", S("s_y")], []]),
        (PathType.EQUATION, "Mott Equation 11-2", Geqn(S("L_{min\\,s}"), 2*sym.sqrt(3)*S("T")*S("N")/sym.Min(S("s_y"))/S("D")/S("W"))),
        (PathType.EQUATION, "Mott Equation 11-4", Geqn(S("L_{min\\,c}"), 4 * S("T")*S("N")/sym.Min(S("s_y"))/S("D")/S("H"))),
        (PathType.EQUATION, "Pick Maximum", Geqn(S("L_{min}"), sym.Max(S("L_{min\\,s}"), S("L_{min\\,c}")))),
        (PathType.CUSTOM, "Round to nearest quarter", [[S("L")], [S("L_{min}")]], round_l_to_quarter),
    ]

    return pathways
