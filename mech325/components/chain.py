from mech325.infrastructure import *


def retrieve_chain_information():
    print("Retrieving information for solving chain questions from Mott.")

    def ChooseChain(knowns):
        logs = []
        checks = [
            (knowns["lubrication type for 40"] == "A", 40),
            (knowns["lubrication type for 60"] == "A", 60),
            (knowns["lubrication type for 80"] == "A", 80),
            (knowns["lubrication type for 40"] == "B", 40),
            (knowns["lubrication type for 60"] == "B", 60),
            (knowns["lubrication type for 80"] == "B", 80),
            (knowns["lubrication type for 40"] == "C", 40),
            (knowns["lubrication type for 60"] == "C", 60),
            (knowns["lubrication type for 80"] == "C", 80),
        ]
        for check in checks:
            if check[0]:
                knowns[S("N_{in}")] = knowns[S("N_{in\\,"+f"{check[1]}"+"}")]
                knowns[S("N_{chain}")] = knowns[S("N_{chain\\,"+f"{check[1]}"+"}")]
                knowns[S("H_{tab}")] = knowns[S("H_{tab\\,"+f"{check[1]}"+"}")]
                knowns["lubrication type"] = knowns["lubrication type for "+f"{check[1]}"]
                knowns["chain number"] = check[1]
                logs.append(f"since the lubrication type for {check[1]} is {knowns['lubrication type']}, and this is the smallest chain, {check[1]} is chosen")
                return logs

    pathways = [
        # Tangential Speed and Input Output Ratio
        (PathType.EQUATION, "General Equation VR",              Geqn(S("VR_{rough}"),       S("n_{in}")/S("n_{out\\,rough}"))),
        (PathType.EQUATION, "General Equation VR",              Geqn(S("VR"),               S("n_{in}")/S("n_{out}"))),
        (PathType.EQUATION, "General Equation VR",              Geqn(S("VR_{rough}"),       S("N_{out\\,rough}")/S("N_{in}"))),
        (PathType.EQUATION, "General Equation VR",              Geqn(S("VR"),               S("N_{out}")/S("N_{in}"))),

        # Geometry
        (PathType.EQUATION, "Pitch definition",                 Geqn(S("CD_{C\\,rough}"),   S("CD_{rough}")/S("p"))),
        (PathType.EQUATION, "Pitch definition",                 Geqn(S("CD"),               S("CD_{C}")*S("p"))),
        (PathType.EQUATION, "Mott Equation 7-18",               Geqn(S("L_{C\\,rough}"),    2*S("CD_{C\\,rough}")+(S("N_{out}")+S("N_{in}"))/2+(S("N_{out}")-S("N_{in}"))**2/(4*sym.pi**2*S("CD_{C\\,rough}")))),
        (PathType.EQUATION, "Mott Equation 7-19",               Geqn(S("CD_{C}"),           0.25*((S("L_{C}")-(S("N_{out}")+S("N_{in}"))/2) + sym.sqrt((S("L_{C}")-(S("N_{out}")+S("N_{in}"))/2)**2 - 2*(S("N_{out}") - S("N_{in}"))**2/sym.pi**2)))),
        (PathType.TABLE_OR_FIGURE, "General Figure round",      [[S("N_{out}")], [S("N_{out\\,rough}")]]),
        (PathType.TABLE_OR_FIGURE, "General Figure round",      [[S("L_{C}")], [S("L_{C\\,rough}")]]),
        # The following commented out line are alternative equations to the one above but uses more name space.
        # (PathType.EQUATION, "Mott Equation 7-19-sub",           Geqn(S("B_{C}"),            S("L_{C}")-(S("N_{out}")+S("N_{in}"))/2)),
        # (PathType.EQUATION, "Mott Equation 7-19",               Geqn(S("CD_{C}"),           0.25*(S("B_{C}") + sym.sqrt(S("B_{C}")**2 - 2*(S("N_{out}") - S("N_{in}"))**2/sym.pi**2)))),
        (PathType.TABLE_OR_FIGURE, "Mott Table 7-12",  [[S("p")], ["chain number"]]),

        (PathType.EQUATION, "Mott Equation 17-20",              Geqn(S("D_{in}"),          S("p")/sym.sin(sym.pi/S("N_{in}")))),
        (PathType.EQUATION, "Mott Equation 17-20",              Geqn(S("D_{out}"),         S("p")/sym.sin(sym.pi/S("N_{out}")))),
        (PathType.EQUATION, "Mott Equation 17-21",              Geqn(S("\\theta_{in}"),     sym.pi-2*sym.asin((S("D_{out}")-S("D_{in}"))/S("CD")))),
        (PathType.EQUATION, "Mott Equation 17-22",              Geqn(S("\\theta_{out}"),    sym.pi+2*sym.asin((S("D_{out}")-S("D_{in}"))/S("CD")))),

        # Selection
        (PathType.EQUATION, "1 Chain Design Power",  Geqn(S("H_{des\\,1}"),      S("H_{des}"))),
        (PathType.EQUATION, "2 Chain Design Power",  Geqn(S("H_{des\\,2}"),      S("H_{des}")/1.7)),
        (PathType.EQUATION, "3 Chain Design Power",  Geqn(S("H_{des\\,3}"),      S("H_{des}")/2.5)),
        (PathType.EQUATION, "4 Chain Design Power",  Geqn(S("H_{des\\,4}"),      S("H_{des}")/3.3)),
        (PathType.TABLE_OR_FIGURE, "Mott Table 7-14",  [[S("N_{in\\,40}"), S("N_{chain\\,40}"), S("H_{tab\\,40}"), "lubrication type for 40"], [S("n_{in}"), S("H_{des\\,1}"), S("H_{des\\,2}"), S("H_{des\\,3}"), S("H_{des\\,4}")]]),
        (PathType.TABLE_OR_FIGURE, "Mott Table 7-15",  [[S("N_{in\\,60}"), S("N_{chain\\,60}"), S("H_{tab\\,60}"), "lubrication type for 60"], [S("n_{in}"), S("H_{des\\,1}"), S("H_{des\\,2}"), S("H_{des\\,3}"), S("H_{des\\,4}")]]),
        (PathType.TABLE_OR_FIGURE, "Mott Table 7-16",  [[S("N_{in\\,80}"), S("N_{chain\\,80}"), S("H_{tab\\,80}"), "lubrication type for 80"], [S("n_{in}"), S("H_{des\\,1}"), S("H_{des\\,2}"), S("H_{des\\,3}"), S("H_{des\\,4}")]]),
        # choose with a ton of lookup data.
        (
            PathType.CUSTOM,
            "Mott choose between 40, 60, 80",
            [
                [
                    "chain number", S("N_{in}"), S("N_{chain}"), S("H_{tab}"), "lubrication type",
                ], [
                    S("N_{in\\,40}"), S("N_{chain\\,40}"), S("H_{tab\\,40}"), "lubrication type for 40",
                    S("N_{in\\,60}"), S("N_{chain\\,60}"), S("H_{tab\\,60}"), "lubrication type for 60",
                    S("N_{in\\,80}"), S("N_{chain\\,80}"), S("H_{tab\\,80}"), "lubrication type for 80",
                ]
            ],
            ChooseChain
        ),

        # Power, Torque and Forces
        (PathType.EQUATION, "General Equation Torque",  Geqn(S("T_{in}"),           63025*S("H_{des}")/S("n_{in}"))),
        (PathType.EQUATION, "General Equation Torque",  Geqn(S("T_{out}"),          63025*S("H_{des}")/S("n_{out}"))),
        (PathType.EQUATION, "General Equation Torque",  Geqn(S("F"),                2*S("T_{in}")/S("D_{in}"))),

        # Correction Factors
        (PathType.TABLE_OR_FIGURE, "Mott Table 7-17",  [[S("K_s")], ["driven", "driver"]]),  # Service Factor
        (PathType.TABLE_OR_FIGURE, "Mott Figure 7-text-pg-281",  [[S("K_{strand}")], [S("N_{chain}")]]),  # Chain Count Factor

        # Power
        (PathType.EQUATION, "General Equation service factor",  Geqn(S("H_{des}"),          S("H_{nom}") * S("K_s"))),
        (PathType.EQUATION, "Mott Equation strand correction",  Geqn(S("H_{all}"),          S("K_{strand}")*S("H_{tab}"))),
        (PathType.EQUATION, "General Equation safety factor",   Geqn(S("n_{sf}"),           S("H_{all}")/S("H_{des}"))),
    ]

    return pathways
