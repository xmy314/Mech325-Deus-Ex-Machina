from mech325.infrastructure import *


def retrieve_bevelgear_information():
    print("Retrieving information for solving bevel gear questions from Mott.")
    print("Please note that the following code is not throughly tested.")

    def compute_Km(knowns):
        logs = []
        if (knowns["straddle mount count"] == 2):
            logs.append("$K_{mb} = 1$ for both gear straddle mounted")
            knowns[S("K_{mb}")] = 1
        elif (knowns["straddle mount count"] == 1):
            logs.append("$K_{mb} = 1.1$ for both gear straddle mounted")
            knowns[S("K_{mb}")] = 1.1
        elif (knowns["straddle mount count"] == 0):
            logs.append("$K_{mb} = 1.25$ for both gear straddle mounted")
            knowns[S("K_{mb}")] = 1.25
        else:
            raise Exception("Not an option.")

        logs += solve_pathway((PathType.EQUATION, "Mott Equation 10-16", Geqn(S("K_m"), S("K_{mb}")+0.0036*S("F")**2)), knowns)
        return logs

    def compute_Cxc(knowns):
        logs = []
        if (knowns["is crowned"] == 1):
            logs.append("$C_{xc} = 1.5$ for properly crowned teeth according to Mott Text pg-450")
            knowns[S("C_{xc}")] = 1.5
        elif (knowns["is crowned"] == 0):
            logs.append("$C_{xc} = 2$ for properly crowned teeth according to Mott Text pg-450")
            knowns[S("C_{xc}")] = 2
        else:
            raise Exception("Not an option.")

        return logs

    def compute_material(knowns):
        logs = []
        if knowns[S("s_{ab\\,min\\,in}")] < 20000 and knowns[S("s_{ac\\,min}")] < 160000:
            logs.append("Both stresses are reasonble, no case hardening required.")

            logs += solve_pathway((PathType.EQUATION, "Mott Equation In Figure 10-17", Geqn(S("Bending\\,Required\\,HB"), (S("s_{ab\\,min\\,in}")/1000-2.10)/0.044)), knowns)
            logs += solve_pathway((PathType.EQUATION, "Mott Equation In Figure 10-21", Geqn(S("Contact\\,Required\\,HB"), (S("s_{ac\\,min}")/1000-23.62)/0.341)), knowns)
            logs += solve_pathway((PathType.EQUATION, "General Equation accomendate both", Geqn(S("Required\\,HB"), sym.Max(S("Bending\\,Required\\,HB"), S("Contact\\,Required\\,HB")))), knowns)

            logs += solve_pathway((PathType.TABLE_OR_FIGURE, "Mott Table Appendix-3", [["SAE", S("HB")], [S("Required\\,HB")]]), knowns)

            logs += solve_pathway((PathType.EQUATION, "Mott Equation In Figure 10-17", Geqn(S("s_{ab}"), (0.044*S("HB")+2.10)*1000)), knowns)
            logs += solve_pathway((PathType.EQUATION, "Mott Equation In Figure 10-21", Geqn(S("s_{ac}"), (0.341*S("HB")+23.62)*1000)), knowns)

        elif knowns[S("s_{ab\\,min\\,in}")] < 30000 and knowns[S("s_{ac\\,min}")] < 200000:
            logs.append("Stress is too high, case Hardening Required:")
            logs.append("By looking at Mott Table Appendix 3, 4320 DOQT 300 is selected. with HRC=62")

            knowns[S("HRC")] = 62
            knowns[S("s_{ab}")] = 30000
            knowns[S("s_{ac}")] = 200000

            logs.append(f'By looking at Mott Table 9-9, ${S("s_{ab}")} = {30000}$, ${S("s_{ab}")} = {200000}$')
        else:
            raise Exception("exceptionally high stress")

        return logs

    # Everything is here is collected from the book through a completely manual process.

    pathways = [
        # get design power is not necessary as there is no table or figure that can be used to selectct diametrical pitch.

        # Input Output Ratio
        (PathType.EQUATION, "General Equation VR",              Geqn(S("VR_{rough}"),       S("n_{in}")/S("n_{out\\,rough}"))),
        (PathType.EQUATION, "General Equation VR",              Geqn(S("VR"),               S("n_{in}")/S("n_{out}"))),
        (PathType.EQUATION, "General Equation VR",              Geqn(S("VR"),               S("N_{out}")/S("N_{in}"))),
        (PathType.EQUATION, "General Equation VR",              Geqn(S("VR_{rough}"),               S("N_{out\\,rough}")/S("N_{in}"))),
        (PathType.EQUATION, "General Equation GR",              Geqn(S("GR"), S("VR"))),

        (PathType.TABLE_OR_FIGURE, "General Figure round",      [[S("N_{out}")], [S("N_{out\\,rough}")]]),

        # Velocity
        (PathType.EQUATION, "General Equation Pitchline Velocity",      Geqn(S("V"), sym.pi*S("D_{in}")*S("n_{in}")/12)),


        # Geometry
        (PathType.EQUATION, "General Equation Gear Diameter",           Geqn(S("D_{in}"), S("N_{in}")/S("P_d"))),
        (PathType.EQUATION, "General Equation Gear Diameter",           Geqn(S("D_{out}"), S("N_{out}")/S("P_d"))),

        (PathType.EQUATION, "Mott Equation In Table 8-8:", Geqn(S("\\gamma"), sym.atan(S("N_{in}")/S("N_{out}")))),
        (PathType.EQUATION, "Mott Equation In Table 8-8", Geqn(S("\\Gamma"), sym.atan(S("N_{out}")/S("N_{in}")))),

        (PathType.EQUATION, "Mott Equation In Table 8-8", Geqn(S("A_o"), S("D_{in}")/(2*sym.sin(S("\\gamma"))))),
        (PathType.EQUATION, "Mott Equation In Table 8-8", Geqn(S("A_o"), S("D_{out}")/(2*sym.sin(S("\\Gamma"))))),

        (PathType.EQUATION, "Mott Equation In Table 8-8", Geqn(S("F_{nom}"), 0.3*S("A_o"))),
        (PathType.EQUATION, "Mott Equation In Table 8-8", Geqn(S("F_{max}"), sym.Min(S("A_o")/3, 10/S("P_d")))),

        (PathType.EQUATION, "Mott Equation In Table 8-8", Geqn(S("A_m"), S("A_o")-0.5*S("F"))),

        (PathType.EQUATION, "Mott Equation 10-11", Geqn(S("R_{m\\,in}"), S("D_{in}")/2-S("F")*sym.sin(S("\\gamma")/2))),
        (PathType.EQUATION, "Mott Equation 10-11:", Geqn(S("R_{m\\,out}"), S("D_{out}")/2-S("F")*sym.sin(S("\\Gamma")/2))),

        # Force Analysis
        (PathType.EQUATION, "General Equation Torque input shaft ",     Geqn(S("T_{in}"), 63025*S("H_{nom}")/S("n_{in}"))),
        (PathType.EQUATION, "General Equation Torque input shaft ",     Geqn(S("T_{out}"), 63025*S("H_{nom}")/S("n_{out}"))),

        (PathType.EQUATION, "Mott Equation 10-10",                      Geqn(S("W_{t\\,in\\,force}"), S("T_{in}")/S("R_{m\\,in}"))),
        (PathType.EQUATION, "Mott Equation 10-12",                      Geqn(S("W_{r\\,in\\,force}"),  S("W_{t\\,in\\,force}")*sym.tan(S("\\phi"))*sym.cos(S("\\gamma")))),
        (PathType.EQUATION, "Mott Equation 10-13",                      Geqn(S("W_{x\\,in\\,force}"),  S("W_{t\\,in\\,force}")*sym.tan(S("\\phi"))*sym.sin(S("\\gamma")))),
        (PathType.EQUATION, "Mott Equation 10-10",                      Geqn(S("W_{t\\,out\\,force}"), S("T_{out}")/S("R_{m\\,out}"))),
        (PathType.EQUATION, "Mott Equation In Figure 10-8:",            Geqn(S("W_{r\\,out\\,force}"), S("W_{x\\,in\\,force}"))),
        (PathType.EQUATION, "Mott Equation In Figure 10-8:",            Geqn(S("W_{x\\,out\\,force}"), S("W_{r\\,in\\,force}"))),

        (PathType.EQUATION, "Mott Equation In Text pg-445",             Geqn(S("W_t"), 2*S("T_{in}")/S("D_{in}"))),
        (PathType.EQUATION, "Mott Equation In Text pg-445",             Geqn(S("W_t"), 2*S("T_{out}")/S("D_{out}"))),

        # Stress Analysis
        # o
        (PathType.TABLE_OR_FIGURE, "Mott Table 9-1", [[S("K_o")], ["driven", "driver"]]),
        # v
        (PathType.EQUATION, "Mott page 384 B for Kv",                   Geqn(S("B_{kv}"), 0.25*(S("A_v")-5)**0.667)),
        (PathType.EQUATION, "Mott page 384 C for Kv",                   Geqn(S("C_{kv}"), 50+56*(1-S("B_{kv}")))),
        (PathType.EQUATION, "Mott page 384 Kv",                         Geqn(S("K_v"), (S("C_{kv}")/(S("C_{kv}")+sym.sqrt(sym.Min(S("V"), (S("C_{kv}")+14-S("A_v"))**2))))**(-S("B_{kv}")))),
        # m
        (PathType.CUSTOM, "Mott Equation 10-16", [[S("K_m")], [S("F"), "straddle mount count"]], compute_Km),
        # R
        (PathType.TABLE_OR_FIGURE, "Mott Table 9-11", [[S("K_R")], ["Reliability"]]),
        # cycles
        (PathType.EQUATION, "9-27",                                     Geqn(S("N_{c\\,in}"), 60*S("n_{in}")*S("L_{hr}"))),

        # - Bending Stress
        # Ks
        (PathType.TABLE_OR_FIGURE, "Mott Figure 10-13", [[S("K_s")], [S("P_d")]]),
        # J
        (PathType.TABLE_OR_FIGURE, "Mott Figure 10-15", [[S("J_{in}"), S("J_{out}")], [S("N_{in}"), S("N_{out}"), S("\\phi")]]),
        # sb
        (PathType.EQUATION, "Mott Equation 10-14",                      Geqn(S("s_{b\\,in}"), S("W_t")*S("P_d")*S("K_o")*S("K_s")*S("K_v")*S("K_m")/(S("F")*S("J_{in}")))),
        (PathType.EQUATION, "Mott Equation 10-14",                      Geqn(S("s_{b\\,out}"), S("W_t")*S("P_d")*S("K_o")*S("K_s")*S("K_v")*S("K_m")/(S("F")*S("J_{out}")))),
        # KLin
        (PathType.TABLE_OR_FIGURE, "Mott Figure 9-21",                  [[S("K_{L\\,in}")], [S("N_{c\\,in}")]]),
        # s ab required
        (PathType.EQUATION, "Mott Equation 10-18",                       Geqn(S("s_{ab\\,min\\,in}"), S("s_{b\\,in}")*S("K_R")/S("K_{L\\,in}"))),

        # - Contact Stress
        # Cp
        (PathType.TABLE_OR_FIGURE, "Mott Table 9-7",                        [[S("C_p")], []]),
        # Cs
        (PathType.EQUATION, "Mott Equation 10-20",                      Geqn(S("C_s"), 0.125*S("F")+0.4375)),
        # Cxc
        (PathType.CUSTOM, "Mott Table 9-7",                                  [[S("C_{xc}")], ["is crowned"]], compute_Cxc),
        # I
        (PathType.TABLE_OR_FIGURE, "Mott Figure 10-19",                      [[S("I")], [S("N_{in}"), S("N_{out}"), S("\\phi")]]),
        # sc
        (PathType.EQUATION, "Mott Equation 9-23",                       Geqn(S("s_c"), S("C_p")*sym.sqrt(S("W_t")*S("K_o")*S("C_s")*S("K_v")*S("K_m")*S("C_{xc}")/(S("F")*S("I")*S("D_{in}"))))),
        # CL
        (PathType.TABLE_OR_FIGURE, "Mott Figure 9-22",                      [[S("C_L")], [S("N_{c\\,in}")]]),
        # s ac required
        (PathType.EQUATION, "Mott Equation 10-22",                       Geqn(S("s_{ac\\,min}"), S("s_c")*S("K_R")/S("C_L"))),

        # material selection
        (PathType.CUSTOM, "Mott Table 9-9", [["SAE", S("s_{ab}"), S("s_{ac}")], [S("s_{ab\\,min\\,in}"), S("s_{ac\\,min}")]], compute_material),

        # safety factors
        (PathType.EQUATION, "Mott Equation 10-18",                       Geqn(S("SF_b"), (S("s_{ab}")*S("Y_{in}"))/(S("s_{b\\,in}")*S("K_R")))),
        (PathType.EQUATION, "Mott Equation 10-22",                       Geqn(S("SF_c"), (S("s_{ac}")*S("Z_{in}"))/(S("s_c")*S("K_R")))),
        (PathType.EQUATION, "General Equation Safety Factor Comparison", Geqn(S("SF_W"), sym.Min(S("SF_b"), S("SF_c")**2))),
    ]

    return pathways
