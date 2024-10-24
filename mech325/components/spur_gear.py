from mech325.infrastructure import *


def retrieve_spurgear_information():
    print("Retrieving information for solving spur gear questions from Mott.")

    def force_gear_combination(knowns):
        logs = []
        min_error = 100
        solution_set = (0, 0, 0)
        for nin in range(knowns[S("N_{in\\,min}")], knowns[S("N_{in\\,max}")]+1):
            error = (round(knowns[S("VR_{rough}")]*nin)/nin)-knowns[S("VR_{rough}")]
            if error <= min_error:
                min_error = error
                solution_set = (nin, round(knowns[S("VR_{rough}")]*nin), (round(knowns[S("VR_{rough}")]*nin)/nin))
        knowns[S("N_{in}")] = solution_set[0]
        knowns[S("N_{out}")] = solution_set[1]
        knowns[S("VR")] = solution_set[2]

        logs.append(f"By brute forcing, {solution_set[0]}:{solution_set[1]} is with in the allowed design constraints and is closest to the desired velocity ratio of {knowns['VR_{rough}']}")
        return logs

    def compute_J(knowns):
        logs = []
        if math.degrees(knowns[S("\\phi")]) == 20:
            logs += solve_pathway((PathType.TABLE_OR_FIGURE, "Mott Figure 9-10a",  [[S("J_{in}"), S("J_{out}")], [S("N_{in}"), S("N_{out}")]]), knowns)
        elif math.degrees(knowns[S("\\phi")]) == 25:
            logs += solve_pathway((PathType.TABLE_OR_FIGURE, "Mott Figure 9-10b",  [[S("J_{in}"), S("J_{out}")], [S("N_{in}"), S("N_{out}")]]), knowns)
        else:
            raise Exception("weird pressure angle")
        return logs

    def compute_Cpf(knowns):
        logs = []
        ratio = knowns[S("F")]/knowns[S("D_{in}")]
        if ratio < 0.5:
            ratio = 0.5
            logs.append("Since that the ratio is too small, 0.5 is used")

        if knowns[S("F")] <= 1:
            knowns[S("C_{pf}")] = ratio/10-0.025
            chunk = ('\\begin{align*}')
            chunk += "\n"+(f'{S("C_{pf}")} &= \\frac{{\\frac{{F}}{{D_{{in}}}}}}{{10}}-0.025\\\\')
            chunk += "\n"+(f'{S("C_{pf}")} &= {knowns[S("C_{pf}")]}\\\\')
            chunk += "\n"+('\end{align*}')
        elif knowns[S("F")] <= 15:
            knowns[S("C_{pf}")] = ratio/10-0.0375+0.0125*knowns[S("F")]
            chunk = ('\begin{align*}')
            chunk += "\n"+(f'{S("C_{pf}")} &= \\frac{{\\frac{{F}}{{D_{{in}}}}}}{{10}}-0.0375+0.0125 \cdot F\\\\')
            chunk += "\n"+(f'{S("C_{pf}")} &= {knowns[S("C_{pf}")]}\\\\')
            chunk += "\n"+('\end{align*}')
        else:
            raise Exception("Unexpected Face Width")
        logs.append(chunk)
        return logs

    def compute_Cma(knowns):
        logs = []
        if "Open" in knowns["exposure condition"]:
            logs += solve_pathway((PathType.EQUATION, "Mott Figure 9-13 Open",  Geqn(S("C_{ma}"), 0.2470 + 0.0167*S(r"F") - 0.0000765*S(r"F")*S(r"F"))), knowns)
        elif "Commercial" in knowns["exposure condition"]:
            logs += solve_pathway((PathType.EQUATION, "Mott Figure 9-13 Comm",  Geqn(S("C_{ma}"), 0.1270 + 0.0158*S(r"F") - 0.0001093*S(r"F")*S(r"F"))), knowns)
        elif "Precision" in knowns["exposure condition"]:
            logs += solve_pathway((PathType.EQUATION, "Mott Figure 9-13 Prec",  Geqn(S("C_{ma}"), 0.0675 + 0.0128*S(r"F") - 0.0000926*S(r"F")*S(r"F"))), knowns)
        elif "Extra-precision" in knowns["exposure condition"]:
            logs += solve_pathway((PathType.EQUATION, "Mott Figure 9-13 Extr",  Geqn(S("C_{ma}"), 0.0380 + 0.0102*S(r"F") - 0.0000822*S(r"F")*S(r"F"))), knowns)
        else:
            raise Exception("Unexpected exposure condition")
        return logs

    def compute_material(knowns):
        logs = []
        if knowns[S("s_{ab\\,min\\,in}")] < 44000 and knowns[S("s_{ac\\,min}")] < 160000:
            logs.append("Both stresses are reasonble, no case hardening required.")

            logs += solve_pathway((PathType.EQUATION, "Mott Equation", Geqn(S("Bending\\,Required\\,HB"), (S("s_{ab\\,min\\,in}")/1000-12.80)/0.0773)), knowns)
            logs += solve_pathway((PathType.EQUATION, "Mott Equation", Geqn(S("Contact\\,Required\\,HB"), (S("s_{ac\\,min}")/1000-29.10)/0.322)), knowns)
            logs += solve_pathway((PathType.EQUATION, "Mott Equation", Geqn(S("Required\\,HB"), sym.Max(S("Bending\\,Required\\,HB"), S("Contact\\,Required\\,HB")))), knowns)

            logs += solve_pathway((PathType.TABLE_OR_FIGURE, "Mott Table Appendix-3", [["SAE", S("HB")], [S("Required\\,HB")]]), knowns)

            logs += solve_pathway((PathType.EQUATION, "Mott Equation", Geqn(S("s_{ab}"), (0.0773*S("HB")+12.80)*1000)), knowns)
            logs += solve_pathway((PathType.EQUATION, "Mott Equation", Geqn(S("s_{ac}"), (0.322*S("HB")+29.10)*1000)), knowns)

        elif knowns[S("s_{ab\\,min\\,in}")] < 55000 and knowns[S("s_{ac\\,min}")] < 180000:
            logs.append("Stress is too high case Hardening Required:")
            logs.append("By looking at Mott Table Appendix 3, 4320 DOQT 300 is selected. with HRC=62")

            knowns[S("HRC")] = 62
            knowns[S("s_{ab}")] = 55000
            knowns[S("s_{ac}")] = 180000

            logs.append(f'By looking at Mott Table 9-9, ${S("s_{ab}")} = {55000}$, ${S("s_{ab}")} = {180000}$')
        else:
            raise Exception("exceptionally high stress")

        return logs

    # Everything is here is collected from the book through a completely manual process.
    pathways = [
        # Correction Factor
        (PathType.TABLE_OR_FIGURE, "Mott Table 9-1", [[S("K_o")], ["driven", "driver"]]),
        (PathType.EQUATION, "General Equation service factor",  Geqn(S("H_{des}"),      S("H_{nom}") * S("K_o"))),

        # Select diametrical pitch
        (PathType.TABLE_OR_FIGURE, "Mott Figure 9-11",  [[S("P_d")], [S("n_{in}"), S("H_{des}")]]),

        # Tangential Speed and Input Output Ratio
        (PathType.EQUATION, "General Equation VR",              Geqn(S("VR_{rough}"),       S("n_{in}")/S("n_{out\\,rough}"))),
        (PathType.EQUATION, "General Equation VR",              Geqn(S("VR"),               S("n_{in}")/S("n_{out}"))),
        (PathType.EQUATION, "General Equation VR",              Geqn(S("VR"),               S("N_{out}")/S("N_{in}"))),
        (PathType.CUSTOM, "Brute Force Gear Combination",       [[S("N_{in}"), S("N_{out}"), S("N_{VR}")], [S("N_{in\\,min}"), S("N_{in\\,max}"), S("VR_{rough}")]], force_gear_combination),
        (PathType.EQUATION, "General Equation Pitchline Velocity",      Geqn(S("V"), sym.pi*S("D_{in}")*S("n_{in}")/12)),

        # gear geometry
        (PathType.EQUATION, "Mott Equation 8-12",                       Geqn(S("p"), sym.pi/S("P_d"))),
        (PathType.EQUATION, "General Equation Gear Diameter",           Geqn(S("D_{in}"), S("N_{in}")/S("P_d"))),
        (PathType.EQUATION, "General Equation Gear Diameter",           Geqn(S("D_{out}"), S("N_{out}")/S("P_d"))),
        (PathType.EQUATION, "Mott Equation page 378",                   Geqn(S("F"), 12/S("P_d"))),

        # Torque and Force
        (PathType.EQUATION, "General Equation Torque input shaft ",     Geqn(S("T_{in}"), 63025*S("H_{nom}")/S("n_{in}"))),
        (PathType.EQUATION, "General Equation Transmitted Force",       Geqn(S("W_t"), 2*S("T_{in}")/S("D_{in}"))),
        (PathType.EQUATION, "General Equation Radial Force",            Geqn(S("W_r"), S("W_t")*sym.tan(S("\\phi")))),

        # Stress Analysis
        # s
        (PathType.TABLE_OR_FIGURE, "Mott Table 9-2", [[S("K_s")], [S("P_d")]]),
        # v
        (PathType.EQUATION, "Mott page 384 B for Kv", Geqn(S("B_{kv}"), 0.25*(S("A_v")-5)**0.667)),
        (PathType.EQUATION, "Mott page 384 C for Kv", Geqn(S("C_{kv}"), 50+56*(1-S("B_{kv}")))),
        (PathType.EQUATION, "Mott page 384 Kv", Geqn(S("K_v"), (S("C_{kv}")/(S("C_{kv}")+sym.sqrt(sym.Min(S("V"), (S("C_{kv}")+14-S("A_v"))**2))))**(-S("B_{kv}")))),
        # m
        (PathType.CUSTOM, "Mott Figure 9-12", [[S("C_{pf}")], [S("F"), S("D_{in}")]], compute_Cpf),
        (PathType.CUSTOM, "Mott Figure 9-13", [[S("C_{ma}")], [S("F"), "exposure condition"]], compute_Cma),
        (PathType.EQUATION, "Mott Equation 9-17", Geqn(S("K_m"), 1+S("C_{pf}")+S("C_{ma}"))),
        # R
        (PathType.TABLE_OR_FIGURE, "Mott Table 9-11", [[S("K_R")], ["Reliability"]]),
        # cycles
        (PathType.EQUATION, "9-27", Geqn(S("N_{c\\,in}"), 60*S("n_{in}")*S("L_{hr}"))),

        # - Bending Stress
        # J
        (PathType.CUSTOM, "Mott Figure 9-10", [[S("J_{in}"), S("J_{out}")], [S("N_{in}"), S("N_{out}"), S("\\phi")]], compute_J),
        # B
        (PathType.TABLE_OR_FIGURE, "Mott Figure 9-14", [[S("K_B")], []]),
        # sb
        (PathType.EQUATION, "Mott Equation 9-16", Geqn(S("s_{b\\,in}"), S("W_t")*S("P_d")*S("K_o")*S("K_s")*S("K_v")*S("K_m")*S("K_B")/(S("F")*S("J_{in}")))),
        (PathType.EQUATION, "Mott Equation 9-16", Geqn(S("s_{b\\,out}"), S("W_t")*S("P_d")*S("K_o")*S("K_s")*S("K_v")*S("K_m")*S("K_B")/(S("F")*S("J_{out}")))),
        # Y
        (PathType.TABLE_OR_FIGURE, "Mott Figure 9-21", [[S("Y_{in}")], [S("N_{c\\,in}")]]),
        # s ab required
        (PathType.EQUATION, "Mott Equation 9-30", Geqn(S("s_{ab\\,min\\,in}"), S("s_{b\\,in}")*S("K_R")/S("Y_{in}"))),

        # - Contact Stress
        # C_p
        (PathType.TABLE_OR_FIGURE, "Mott Table 9-7",  [[S("C_p")], []]),
        # I
        (PathType.TABLE_OR_FIGURE, "Mott Figure 9-17", [[S("I")], [S("N_{in}"), S("VR"), S("\\phi")]]),
        # sc
        (PathType.EQUATION, "Mott Equation 9-23", Geqn(S("s_c"), S("C_p")*sym.sqrt(S("W_t")*S("K_o")*S("K_s")*S("K_v")*S("K_m")*S("K_B")/(S("F")*S("I")*S("D_{in}"))))),
        # Z
        (PathType.TABLE_OR_FIGURE, "Mott Figure 9-22", [[S("Z_{in}")], [S("N_{c\\,in}")]]),
        # s ac required
        (PathType.EQUATION, "Mott Equation 9-31", Geqn(S("s_{ac\\,min}"), S("s_c")*S("K_R")/S("Z_{in}"))),

        # Material Selection
        (PathType.CUSTOM, "Mott Table 9-9", [["SAE", S("s_{ab}"), S("s_{ac}")], [S("s_{ab\\,min\\,in}"), S("s_{ac\\,min}")]], compute_material),

        # Safety Factor
        (PathType.EQUATION, "Mott Equation 9-32", Geqn(S("SF_b"), (S("s_{ab}")*S("Y_{in}"))/(S("s_{b\\,in}")*S("K_R")))),
        (PathType.EQUATION, "Mott Equation 9-33", Geqn(S("SF_c"), (S("s_{ac}")*S("Z_{in}"))/(S("s_c")*S("K_R")))),
        (PathType.EQUATION, "General Equation Safety Factor Comparison", Geqn(S("SF_W"), sym.Min(S("SF_b"), S("SF_c")*S("SF_c")))),
    ]

    return pathways
