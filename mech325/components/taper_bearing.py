from mech325.infrastructure import *


def retrieve_tbeaing_information():
    print("Retrieving information for solving taper bearing questions from shigley.")

    def iter_proc(knowns):

        logs = []

        logs.append(f'Set the K factor to be the assumed K value of ${round_nsig(knowns[S("K_{assume}")],3)}$ as a starting point.')

        knowns[S("K_A")] = knowns[S("K_{assume}")]
        knowns[S("K_B")] = knowns[S("K_{assume}")]

        logs += solve_pathway((PathType.EQUATION, "Shigley Equation 11-12",  Geqn(S("F_{iA}"), 0.47*S("F_{rA}")/S("K_A"))), knowns)
        logs += solve_pathway((PathType.EQUATION, "Shigley Equation 11-12",  Geqn(S("F_{iB}"), 0.47*S("F_{rB}")/S("K_B"))), knowns)

        if (knowns[S("F_{iA}")] <= knowns[S("F_{iB}")]+knowns[S("F_{ae}")]):
            logs.append(f'Since $F_{{iA}}$({round_nsig(knowns[S("F_{iA}")],3)}) $\\leq$ $F_{{iB}} + F_{{ae}}$({round_nsig(knowns[S("F_{iB}")]+knowns[S("F_{ae}")],3)}), used 11-19')
            logs += solve_pathway((PathType.EQUATION, "Shigley Equation 11-19a",  Geqn(S("F_{eA}"), 0.4*S("F_{rA}")+S("K_A")*(S("F_{iB}")+S("F_{ae}")))), knowns)
            logs += solve_pathway((PathType.EQUATION, "Shigley Equation 11-19b",  Geqn(S("F_{eB}"), S("F_{rB}"))), knowns)
        elif (knowns[S("F_{iA}")] > knowns[S("F_{iB}")]+knowns[S("F_{ae}")]):
            logs.append(f'Since $F_{{iA}}$({round_nsig(knowns[S("F_{iA}")],3)}) $>$ $F_{{iB}} + F_{{ae}}$({round_nsig(knowns[S("F_{iB}")]+knowns[S("F_{ae}")],3)}), used 11-20')
            logs += solve_pathway((PathType.EQUATION, "Shigley Equation 11-20a",  Geqn(S("F_{eB}"), 0.4*S("F_{rB}")+S("K_B")*(S("F_{iA}")-S("F_{ae}")))), knowns)
            logs += solve_pathway((PathType.EQUATION, "Shigley Equation 11-20b",  Geqn(S("F_{eA}"), S("F_{rA}"))), knowns)

        logs += solve_pathway((PathType.EQUATION, "Shigley Equation 11-9-sub", Geqn(S("G_A"), ((S("x_d")/(S("x_0")+(S("\\theta")-S("x_0"))*(sym.ln(1/S("R_{dA}"))**(1/S("b")))))**(1/S("a"))))), knowns)
        logs += solve_pathway((PathType.EQUATION, "Shigley Equation 11-9-sub", Geqn(S("G_B"), ((S("x_d")/(S("x_0")+(S("\\theta")-S("x_0"))*(sym.ln(1/S("R_{dB}"))**(1/S("b")))))**(1/S("a"))))), knowns)

        logs += solve_pathway((PathType.EQUATION, "Shigley Equation 11-9", Geqn(S("C_{10\\,A\\,min}"),  S("a_f")*S("F_{eA}")*S("G_A"))), knowns)
        logs += solve_pathway((PathType.EQUATION, "Shigley Equation 11-9", Geqn(S("C_{10\\,B\\,min}"),  S("a_f")*S("F_{eB}")*S("G_B"))), knowns)

        del knowns[S("K_A")], knowns[S("K_B")],

        logs += solve_pathway((PathType.TABLE_OR_FIGURE, "Shigley Table 11-15", [[S("C_{10\\,A}"), S("K_A"), "A cone number", "A cup number"], [S("C_{10\\,A\\,min}")]],), knowns)
        logs += solve_pathway((PathType.TABLE_OR_FIGURE, "Shigley Table 11-15", [[S("C_{10\\,B}"), S("K_B"), "B cone number", "B cup number"], [S("C_{10\\,B\\,min}")]],), knowns)

        logs.append("Start Iterating.")
        while True:
            # store information from previous iteration by shifting name space.
            knowns[S("C_{10\\,A\\,prior}")] = knowns[S("C_{10\\,A}")]
            knowns[S("C_{10\\,B\\,prior}")] = knowns[S("C_{10\\,B}")]

            # delete information that needs to be recalculated this iteration.
            knowns.pop(S("C_{10\\,A}"))
            knowns.pop(S("C_{10\\,B}"))
            knowns.pop(S("F_{iA}"))
            knowns.pop(S("F_{iB}"))
            knowns.pop(S("F_{eA}"))
            knowns.pop(S("F_{eB}"))
            knowns.pop(S("C_{10\\,A\\,min}"))
            knowns.pop(S("C_{10\\,B\\,min}"))

            logs += solve_pathway((PathType.EQUATION, "Shigley Equation 11-12",  Geqn(S("F_{iA}"), 0.47*S("F_{rA}")/S("K_A"))), knowns)
            logs += solve_pathway((PathType.EQUATION, "Shigley Equation 11-12",  Geqn(S("F_{iB}"), 0.47*S("F_{rB}")/S("K_B"))), knowns)

            if (knowns[S("F_{iA}")] <= knowns[S("F_{iB}")]+knowns[S("F_{ae}")]):
                logs.append(f'Since $F_{{iA}}$({round_nsig(knowns[S("F_{iA}")],3)}) $\\leq$ $F_{{iB}} + F_{{ae}}$({round_nsig(knowns[S("F_{iB}")]+knowns[S("F_{ae}")],3)}), used 11-19')
                logs += solve_pathway((PathType.EQUATION, "Shigley Equation 11-19a",  Geqn(S("F_{eA}"), 0.4*S("F_{rA}")+S("K_A")*(S("F_{iB}")+S("F_{ae}")))), knowns)
                logs += solve_pathway((PathType.EQUATION, "Shigley Equation 11-19b",  Geqn(S("F_{eB}"), S("F_{rB}"))), knowns)
            elif (knowns[S("F_{iA}")] > knowns[S("F_{iB}")]+knowns[S("F_{ae}")]):
                logs.append(f'Since $F_{{iA}}$({round_nsig(knowns[S("F_{iA}")],3)}) $>$ $F_{{iB}} + F_{{ae}}$({round_nsig(knowns[S("F_{iB}")]+knowns[S("F_{ae}")],3)}), used 11-20')
                logs += solve_pathway((PathType.EQUATION, "Shigley Equation 11-20a",  Geqn(S("F_{eB}"), 0.4*S("F_{rB}")+S("K_B")*(S("F_{iA}")-S("F_{ae}")))), knowns)
                logs += solve_pathway((PathType.EQUATION, "Shigley Equation 11-20b",  Geqn(S("F_{eA}"), S("F_{rA}"))), knowns)

            logs += solve_pathway((PathType.EQUATION, "Shigley Equation 11-9", Geqn(S("C_{10\\,A\\,min}"),  S("a_f")*S("F_{eA}")*S("G_A"))), knowns)
            logs += solve_pathway((PathType.EQUATION, "Shigley Equation 11-9", Geqn(S("C_{10\\,B\\,min}"),  S("a_f")*S("F_{eB}")*S("G_B"))), knowns)

            if (knowns[S("C_{10\\,A\\,prior}")] >= knowns[S("C_{10\\,A\\,min}")] and
                    knowns[S("C_{10\\,B\\,prior}")] >= knowns[S("C_{10\\,B\\,min}")]):
                logs.append("The latest choice satisify the requirement. Stop iteration.")
                return logs

            logs.append("The latest choice didn't satisify the requirement. Choose a new set of bearings.")

            del knowns[S("K_A")], knowns[S("K_B")], knowns["A cone number"], knowns["A cup number"], knowns["B cone number"], knowns["B cup number"]

            logs += solve_pathway((PathType.TABLE_OR_FIGURE, "Shigley Table 11-15a", [[S("Bore A"), S("C_{10\\,A}"), S("K_A"), "A cone number", "A cup number"], [S("C_{10\\,A\\,min}")]],), knowns)
            logs += solve_pathway((PathType.TABLE_OR_FIGURE, "Shigley Table 11-15a", [[S("Bore B"), S("C_{10\\,B}"), S("K_B"), "B cone number", "B cup number"], [S("C_{10\\,B\\,min}")]],), knowns)
            logs.append("Iterate again to verify.")

    pathways = [
        # get design power is not necessary as there is no table or figure that can be used to selectct diametrical pitch.
        (PathType.TABLE_OR_FIGURE, "Shigley Table 11-5", [[S("a_f")], ["load type"]]),
        (PathType.EQUATION, "Shigely Equation 11-text-pg-580:", Geqn(S("a"),  10/3)),

        (PathType.EQUATION, "Shigley Equation 11-3 (b):", Geqn(S("L_d"), S("L_{hr}")*60*S("n"))),
        (PathType.EQUATION, "Shigely Equation 11-text-pg-581:", Geqn(S("x_d"),  S("L_d")/S("L_{10}"))),

        (PathType.EQUATION, "General Statistics Equation", Geqn(S("R_{dA}"), S("R_d")**(1/2))),
        (PathType.EQUATION, "General Statistics Equation", Geqn(S("R_{dB}"), S("R_d")**(1/2))),

        (PathType.EQUATION, "Shigley Example Value", Geqn(S("K_{assume}"), 1.5)),

        (PathType.CUSTOM, "Iterative Elimination", [
            [
                S("Bore A"), S("C_{10\\,A}"), S("K_A"), "A cone number", "A cup number",
                S("Bore B"), S("C_{10\\,B}"), S("K_B"), "B cone number", "B cup number",
            ], [
                S("F_{rA}"), S("F_{rB}"), S("F_{ae}"),
                S("x_d"), S("R_{dA}"), S("R_{dB}"), S("K_{assume}"), S("a_f"),
                S("a"), S("b"), S("\\theta"), S("x_0")
            ]], iter_proc),


        (PathType.EQUATION, "Shigley Equation 11-9", Geqn(S("C_{10\\,A}"), S("a_f")*S("F_{eA}")*((S("x_d")/(S("x_0")+(S("\\theta")-S("x_0"))*(sym.ln(1/S("R_A"))**(1/S("b")))))**(1/S("a"))))),
        (PathType.EQUATION, "Shigley Equation 11-9", Geqn(S("C_{10\\,B}"), S("a_f")*S("F_{eB}")*((S("x_d")/(S("x_0")+(S("\\theta")-S("x_0"))*(sym.ln(1/S("R_B"))**(1/S("b")))))**(1/S("a"))))),

        (PathType.EQUATION, "General Statistics Equation", Geqn(S("R"), S("R_A")*S("R_B"))),
    ]

    return pathways
