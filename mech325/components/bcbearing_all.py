from mech325.infrastructure import *


def retrieve_bcbearingall_information():
    print("Retrieving information for solving ball bearing with mixed loading questions from Shigley.")

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

    def iter_proc(knowns):
        if "cylinder" in knowns["rolling element type"]:
            raise Exception("Cylinderical roller cannot handle any thrust load.")

        table_11_1 = [
            [0.014, 0.19, 1.00, 0, 0.56, 2.30],
            [0.021, 0.21, 1.00, 0, 0.56, 2.15],
            [0.028, 0.22, 1.00, 0, 0.56, 1.99],
            [0.042, 0.24, 1.00, 0, 0.56, 1.85],
            [0.056, 0.26, 1.00, 0, 0.56, 1.71],
            [0.070, 0.27, 1.00, 0, 0.56, 1.63],
            [0.084, 0.28, 1.00, 0, 0.56, 1.55],
            [0.110, 0.30, 1.00, 0, 0.56, 1.45],
            [0.17,  0.34, 1.00, 0, 0.56, 1.31],
            [0.28,  0.38, 1.00, 0, 0.56, 1.15],
            [0.42,  0.42, 1.00, 0, 0.56, 1.04],
            [0.56,  0.44, 1.00, 0, 0.56, 1.00],
        ]

        logs = []
        logs.append("For first iteration, assume $X_i=1$ and $Y_i=0$")
        knowns[S("X_i")] = 1
        knowns[S("Y_i")] = 0
        logs += solve_pathway((PathType.EQUATION, "Shigley Equation 11-12",  Geqn(S("F_e"), S("X_i")*S("v")*S("F_r")+S("Y_i")*S("F_a"))), knowns)
        logs += solve_pathway((PathType.EQUATION, "Shigley Equation 11-9-sub", Geqn(S("G"), ((S("x_d")/(S("x_0")+(S("\\theta")-S("x_0"))*(sym.ln(1/S("R_d"))**(1/S("b")))))**(1/S("a"))))), knowns)

        logs += solve_pathway((PathType.EQUATION, "Shigley Equation 11-9", Geqn(S("C_{10\\,min}"),  S("a_f")*S("F_e")*S("G"))), knowns)

        logs += solve_pathway((PathType.TABLE_OR_FIGURE, "Shigley Table 11-2", [[S("Bore"), S("C_{10}"),  S("C_0")], [S("C_{10\\,min}"), "rolling element type"]]), knowns)

        logs += solve_pathway((PathType.EQUATION, "Shigley Equation In-Table 11-1", Geqn(S("\\frac{F_{a}}{C_{0}}"), S("F_a")/S("C_0"))), knowns)
        logs += solve_pathway((PathType.EQUATION, "Shigley Equation In-Table 11-1", Geqn(S("\\frac{F_{a}}{vF_{r}}"), S("F_a")/(S("v")*S("F_r")))), knowns)

        fa_c0 = knowns[S("\\frac{F_{a}}{C_{0}}")]
        favfr = knowns[S("\\frac{F_{a}}{vF_{r}}")]

        # Find the lines that this is in between of.
        row_id = -1
        for i in range(len(table_11_1)-1):
            if table_11_1[i][0] <= fa_c0 and fa_c0 <= table_11_1[i+1][0]:
                row_id = i
                break
        else:
            raise Exception("not neatly in table 11-1")

        # add in the text of why this line is chosen.
        logs.append(f'$${table_11_1[row_id][0]}\\leq{fa_c0}\\leq{table_11_1[row_id+1][0]}$$')

        # add in the text for the interpolation variable.
        t_interp = (fa_c0-table_11_1[row_id][0])/(table_11_1[row_id+1][0]-table_11_1[row_id][0])
        logs.append(f"$$t={t_interp}$$")

        # add in the text for interpolated e.
        e_interp = table_11_1[row_id][1]*(1-t_interp)+table_11_1[row_id+1][1]*t_interp
        logs.append(f"$e1={table_11_1[row_id][1]}$, $e2={table_11_1[row_id+1][1]}$, $e_{{interp}}={e_interp}$")

        # if thrust load effect haven't kicked in.
        if (favfr < e_interp):
            logs.append(f"Since $\\frac{{f_a}}{{vf_r}}={favfr}<{e_interp}=e$, $Y_i=0$")
            logs.append(f"Current selected bearing is Good")
            return logs

        # if thrust load effect kicked in.
        logs.append(f"Since $\\frac{{f_a}}{{vf_r}}={favfr}>{e_interp}=e$, $Y_i!=0$")
        y_interp = table_11_1[row_id][5]*(1-t_interp)+table_11_1[row_id+1][5]*t_interp
        logs.append(f"$e1={table_11_1[row_id][1]}$, $e2={table_11_1[row_id+1][1]}$, $Y_i={y_interp}$")
        while True:
            knowns[S("X_i")] = 0.56
            knowns[S("Y_i")] = y_interp
            knowns[S("Bore Prior")] = knowns[S("Bore")]

            knowns.pop(S("F_e"))
            knowns.pop(S("C_{10\\,min}"))
            knowns.pop(S("Bore"))
            knowns.pop(S("C_{10}"))
            knowns.pop(S("C_0"))
            knowns.pop(S("\\frac{F_{a}}{C_{0}}"))
            knowns.pop(S("\\frac{F_{a}}{vF_{r}}"))

            logs += solve_pathway((PathType.EQUATION, "Shigley Equation 11-12",  Geqn(S("F_e"), S("X_i")*S("v")*S("F_r")+S("Y_i")*S("F_a"))), knowns)

            logs += solve_pathway((PathType.EQUATION, "Shigley Equation 11-9", Geqn(S("C_{10\\,min}"),  S("a_f")*S("F_e")*S("G"))), knowns)

            logs += solve_pathway((PathType.TABLE_OR_FIGURE, "Shigley Table 11-2", [[S("Bore"), S("C_{10}"),  S("C_0")], [S("C_{10\\,min}"), "rolling element type"]]), knowns)

            if (knowns[S("Bore")] == knowns[S("Bore Prior")]):
                logs.append("The selected bore is the same as from the previous iteration")
                return logs

            logs += solve_pathway((PathType.EQUATION, "Shigley Equation In-Table 11-1", Geqn(S("\\frac{F_{a}}{C_{0}}"), S("F_a")/S("C_0"))), knowns)
            logs += solve_pathway((PathType.EQUATION, "Shigley Equation In-Table 11-1", Geqn(S("\\frac{F_{a}}{vF_{r}}"), S("F_a")/(S("v")*S("F_r")))), knowns)

            fa_c0 = knowns[S("\\frac{F_{a}}{C_{0}}")]
            favfr = knowns[S("\\frac{F_{a}}{vF_{r}}")]

            # Find the lines that this is in between of.
            row_id = -1
            for i in range(len(table_11_1)-1):
                if table_11_1[i][0] <= fa_c0 and fa_c0 <= table_11_1[i+1][0]:
                    row_id = i
                    break

            # add in the text of why this line is chosen.
            logs.append(f'$${table_11_1[row_id][0]}\\leq{round_nsig(fa_c0,3)}\\leq{table_11_1[row_id+1][0]}$$')

            # add in the text for the interpolation variable.
            t_interp = (fa_c0-table_11_1[row_id][0])/(table_11_1[row_id+1][0]-table_11_1[row_id][0])
            logs.append(f"$$t={round_nsig(t_interp,3)}$$")

            # add in the text for interpolated e.
            e_interp = table_11_1[row_id][1]*(1-t_interp)+table_11_1[row_id+1][1]*t_interp
            logs.append(f"$e1={table_11_1[row_id][1]}$, $e2={table_11_1[row_id+1][1]}$, $e_{{interp}}={round_nsig(e_interp,3)}$")

            if (favfr < e_interp):
                logs.append(f"${round_nsig(favfr,3)}\\leq{round_nsig(e_interp,3)}$")
                logs.append(f"Current selected bearing is Good")
                return logs

            logs.append(f"${favfr}>{e_interp}$")
            y_interp = table_11_1[row_id][5]*(1-t_interp)+table_11_1[row_id+1][5]*t_interp
            logs.append(f"$e1={table_11_1[row_id][1]}$, $e2={table_11_1[row_id+1][1]}$, $Y_i={round_nsig(y_interp,3)}$")
            knowns[S("X_i")] = 0.56
            knowns[S("Y_i")] = y_interp

    pathways = [
        # get design power is not necessary as there is no table or figure that can be used to selectct diametrical pitch.
        (PathType.EQUATION, "Shigley Equation 11-3 (b):", Geqn(S("L_d"), S("L_{hr}")*60*S("n"))),
        (PathType.EQUATION, "Shigely Equation 11-text-pg-581:", Geqn(S("x_d"),  S("L_d")/S("L_{10}"))),
        (PathType.TABLE_OR_FIGURE, "Shigley Table 11-5", [[S("a_f")], ["load type"]]),
        (PathType.EQUATION, "Shigely Equation 11-text-pg-580:", Geqn(S("a"),  3)),
        (PathType.CUSTOM, "Shigley text", [[S("v")], ["rolling race"]], find_v),
        (PathType.CUSTOM, "Iterative Elimination", [[S("Bore"), S("C_{10}"), S("F_e")], [S("x_d"), S("F_r"), S("F_a"), S("R_d"), "rolling element type", S("v"), S("a_f"), S("a"), S("b"), S("\\theta"), S("x_0")]], iter_proc),

        (PathType.EQUATION, "Shigley Equation 11-9", Geqn(S("C_{10\\,min}"),  S("a_f")*S("F_e")*((S("x_d")/(S("x_0")+(S("\\theta")-S("x_0"))*(sym.ln(1/S("R_d"))**(1/S("b")))))**(1/S("a"))))),
        (PathType.EQUATION, "Shigley Equation 11-9", Geqn(S("C_{10}"),        S("a_f")*S("F_e")*((S("x_d")/(S("x_0")+(S("\\theta")-S("x_0"))*(sym.ln(1/S("R"))**(1/S("b")))))**(1/S("a"))))),
        (PathType.TABLE_OR_FIGURE, "Shigley Table 11-2", [[S("C_{10}"),  S("C_0")], [S("Bore"), "rolling element type"]]),
    ]

    return pathways
