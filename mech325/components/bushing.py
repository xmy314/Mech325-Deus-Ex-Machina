from mech325.infrastructure import *


def retrieve_bushing_information():
    print("Retrieving information for solving Bushing questions from Shigley.")
    print("Please note that this program only knows how to solve for one kind of bushing.")

    def get_full_design_parameter(knowns):
        logs = []
        if "Oiles SP 500" == knowns["bushing material"]:
            logs += solve_pathway((PathType.TABLE_OR_FIGURE, "Shigley Table 12-11", [[S("P_{max}"), S("V_{max}"), S("PV_{max}"), S("T_{max}")], ["bushing material"]]), knowns)
        else:
            logs += solve_pathway((PathType.TABLE_OR_FIGURE, "Shigley Table 12-8", [[S("P_{max}"), S("V_{max}"), S("PV_{max}"), S("T_{max}")], ["bushing material"]]), knowns)
        return logs

    def brute_force_selection(knowns):
        logs = []
        bushing_lengths = [
            1/2,
            5/8,
            3/4,
            7/8,
            1,
            1+1/4,
            1+1/2,
            1+3/4,
            2,
            2+1/2,
            3,
            3+1/2,
            4,
            5,]

        bushing_diameters = [
            (1/2,     3/4),
            (5/8,     7/8),
            (3/4,   1+1/8),
            (7/8,   1+1/4),
            (1,     1+3/8),
            (1,     1+1/2),
            (1+1/4, 1+5/8),
            (1+1/2, 2),
            (1+3/4, 2+1/4),
            (2,     2+1/2),
            (2+1/4, 2+3/4),
            (2+1/2, 3),
            (2+3/4, 3+3/8),
            (3,     3+5/8),
            (3+1/2, 4+1/8),
            (4,     4+3/4),
            (4+1/2, 5+3/8),
            (5,     6),
        ]

        # the following is the exact replica of table 12-12
        bushing_combinations = [
            [1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0,],
            [0, 1, 1, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0,],
            [0, 1, 1, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0,],
            [0, 0, 1, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0,],
            [0, 0, 1, 0, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0,],
            [0, 0, 1, 0, 1, 0, 1, 0, 1, 0, 0, 0, 0, 0,],
            [0, 0, 0, 0, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0,],
            [0, 0, 0, 0, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0,],
            [0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0,],
            [0, 0, 0, 0, 0, 0, 1, 0, 1, 1, 1, 0, 0, 0,],
            [0, 0, 0, 0, 0, 0, 1, 0, 1, 1, 1, 0, 0, 0,],
            [0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 0, 0, 0,],
            [0, 0, 0, 0, 0, 0, 1, 0, 1, 1, 1, 0, 0, 0,],
            [0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0,],
            [0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 0,],
            [0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 0,],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 1,],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 1,],
        ]

        valid_combinations = []
        for dia_i in range(len(bushing_diameters)):
            for len_i in range(len(bushing_lengths)):
                if (bushing_combinations[dia_i][len_i] == 0):
                    continue
                if (S("D_{constrained}") in knowns and knowns[S("D_{constrained}")] != bushing_diameters[dia_i][0]):
                    continue
                if (S("L_{constrained}") in knowns and knowns[S("L_{constrained}")] != bushing_length[len_i]):
                    continue
                valid_combinations.append((dia_i, len_i))

        # sort combinations by L/D
        valid_combinations.sort(key=lambda x:  abs(bushing_lengths[x[1]]/bushing_diameters[x[0]][0]-1))

        for dia_i, len_i in valid_combinations:

            bushing_diameter = bushing_diameters[dia_i]
            bushing_length = bushing_lengths[len_i]

            logs.append(f"Try $D={bushing_diameter[0]}$, $L={bushing_length}$.")

            # 4 operating values and wear from set upper bounds
            sub_pathways = [
                (PathType.EQUATION, "Shigley Equation 12-42", Geqn(S("P_{peak}"), (4*S("n_d")*S("F"))/(sym.pi*S("D")*S("L")))),
                (PathType.EQUATION, "Shigley Equation 12-40", Geqn(S("V"), sym.pi*S("D")*S("n")/12)),
                (PathType.EQUATION, "Shigley Equation 12-41", Geqn(S("PV"), sym.pi*S("n_d")*S("F")*S("n")/(12*S("L")))),
                (PathType.EQUATION, "Shigley Equation 12-49", Geqn(S("L"), 720*S("f_s")*S("n_d")*S("F")*S("n")/(S("J")*S("\\hbar_{cr}")*(S("T")-S("T_{\\infty}"))))),
                (PathType.EQUATION, "Shigley Equation 12-43", Geqn(S("w"), (S("K")*S("n_d")*S("F")*S("n")*S("t"))/(3*S("L")))),
            ]

            knowns[S("D")] = bushing_diameter[0]
            knowns[S("L")] = bushing_length
            for sub_pathway in sub_pathways:
                solve_pathway(sub_pathway, knowns)

            if (
                knowns[S("P_{peak}")] < knowns[S("P_{max}")] and
                knowns[S("V")] < knowns[S("V_{max}")] and
                knowns[S("PV")] < knowns[S("PV_{max}")] and
                knowns[S("T")] < knowns[S("T_{max}")] and
                knowns[S("w")] < knowns[S("w_{max}")]
            ):
                break
            else:
                logs.append(f"Fails at least one Requirement.")
                del knowns[S("P_{peak}")], knowns[S("V")], knowns[S("PV")], knowns[S("T")], knowns[S("w")]

        del knowns[S("P_{peak}")], knowns[S("V")], knowns[S("PV")], knowns[S("T")], knowns[S("w")]
        for sub_pathway in sub_pathways:
            logs += solve_pathway(sub_pathway, knowns)

        logs.append(f'Since all 4 operational variables and the wear are within design specifications, D={knowns[S("D")]} and L={knowns[S("L")]} is chosen.')
        return logs

    pathways = [
        # some bearing lookups
        (PathType.TABLE_OR_FIGURE, "Shigley Table 12-9", [[S("K")], ["bushing material"]]),
        (PathType.TABLE_OR_FIGURE, "Shigley Table 12-10", [[S("f_s")], ["bushing material"]]),
        (PathType.CUSTOM, "Shigley Tables", [[S("P_{max}"), S("V_{max}"), S("PV_{max}"), S("T_{max}")], ["bushing material"]], get_full_design_parameter),

        # a constant that for some reason have its own symbol
        (PathType.EQUATION, "Shigley Equation In-Text pg-675", Geqn(S("J"), 778)),

        # some default values.
        (PathType.EQUATION, "Shigley Equation In-Text pg-675", Geqn(S("\\hbar_{cr}"), 2.7)),
        (PathType.EQUATION, "Shigley Equation In-Text pg-675", Geqn(S("T_{\\infty}"), 70)),

        # The core solving function that just brute forces until a combination is found.
        # Not my proudest work and only deals with one specific type of problem.
        (
            PathType.CUSTOM,
            "Shigley Table 12-12",
            [
                [
                    S("D"), S("L")
                ], [
                    S("n"), S("F"), S("n_d"), S("t"),                                                                                                   # human input
                    S("P_{max}"), S("V_{max}"), S("PV_{max}"), S("f_s"), S("\\hbar_{cr}"), S("T_{\\infty}"), S("T_{max}"), S("K"), S("w_{max}"),        # operational limits related based on bushing material.
                    S("J")                                                                                                                              # a random constant
                ]
            ],
            brute_force_selection
        ),

        (PathType.EQUATION, "Shigley Equation 12-42", Geqn(S("P_{peak}"), (4*S("n_d")*S("F"))/(sym.pi*S("D")*S("L")))),
        (PathType.EQUATION, "Shigley Equation 12-40", Geqn(S("V"), sym.pi*S("D")*S("n")/12)),
        (PathType.EQUATION, "Shigley Equation 12-41", Geqn(S("PV"), sym.pi*S("n_d")*S("F")*S("n")/(12*S("L")))),
        (PathType.EQUATION, "Shigley Equation 12-49", Geqn(S("L"), 720*S("f_s")*S("n_d")*S("F")*S("n")/(S("J")*S("\\hbar_{cr}")*(S("T")-S("T_{\\infty}"))))),
        (PathType.EQUATION, "Shigley Equation 12-43", Geqn(S("w"), (S("K")*S("n_d")*S("F")*S("n")*S("t"))/(3*S("L")))),
    ]
    return pathways
