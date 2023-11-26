import sympy as sym
from sympy import Symbol as S
import math
import cv2
from os.path import join
from enum import Enum

# TODO this framework code does not consider inequalities, currently all such decisions are made in custom python code.
# TODO a helper function that explains the different variables.
# !important a custom function that prints a substituted expression without reordering the terms.

#################################################################
#                                                               #
# Below this line are used to setup an environment.             #
#                                                               #
#################################################################


def Geqn(a, b): return a-b


def round_nsig(v, n): return 0 if v == 0 else round(round(v, -int(math.floor(math.log10(abs(v))))+n-1), 10)


#  a few helper functions for pretty print.
def ir(e): return {i: round(float(i), -int(math.floor(math.log10(abs(float(i)))))+2) for i in e.atoms(sym.Float)}


def touch(e): return e.xreplace(ir(e))


# list of different types of questions and their current state
class ComponentType(Enum):
    FLAT_BELT = 1                               # TODO need to compute developed friction and minimum operating stress.
    V_BELT = 2                                  # Done
    SYNCHRONOUS_BELT = 3                        # Done
    CHAIN = 4                                   # Done
    WIRE_ROPE = 5                               # TODO
    SPUR_GEAR = 6                               # Done
    HELICAL_GEAR = 7                            # TEST Selection
    BEVEL_GEAR = 8                              # TEST Selection
    WORM_GEAR = 9                               # TEST Selection
    RACK_PINION = 10                            # TODO
    BOUNDARY_LUBRICATED_BEARING = 11            # TEST Selection
    BALL_AND_CYLINDRICAL_BEARING_RADIAL = 12    # TODO need to determine clearance
    BALL_AND_CYLINDRICAL_BEARING_ALL = 13       # TODO need to determine clearance.
    TAPERED_ROLLER_BEARING = 14                 # TODO need to determine clearance.
    SHAFT_POINT = 15                            # TODO
    KEY = 16                                    # TODO
    RETAINING_RING = 17                         # TODO
    POWER_SCREWS = 18                           # TODO
    BALL_SCREWS = 19                            # not taught yet
    SPRINGS = 20                                # not taught yet
    FASTENER_AND_BOLTS = 21                     # not taught yet


class PathType(Enum):
    # things that need a human to read off of.
    TABLE_OR_FIGURE = 1
    # things that can be represented by equations solved automatically.
    EQUATION = 2
    # latex output describes it as a table or figure but are solved automatically by custom curfit.
    MOCK_TABLE_OR_FIGURE = 3
    # things that are more complicated and needs a python function. This takes care of branching and looping. can be automatic or manual. can nest other two types.
    CUSTOM = 4


#################################################################
#                                                               #
# Below this line are the codes the represent equations,        #
# tables, figures, and some more tedious processes that are     #
# relevent to each type of problem.                             #
#                                                               #
#################################################################


def retrieve_flatbelt_information():
    print("Retrieving information for solving flat belt questions from Shigley.")
    print("Please note that it only solves upper operation limit due to stress but not lower operation limit from friction.")

    def compute_cv(knowns):
        # return path to follow if ready, else return what is needed.
        if not "leather" in knowns["belt"]:
            return [(PathType.EQUATION, "Shigley Text pg 891", Geqn(S("C_v"), 1))]
        else:
            return [(PathType.TABLE_OR_FIGURE, "Shigley Figure 17-9", [[S("C_v")], [S("V")]])]

    # type, name, (output,input)
    pathways = [
        # Component Property
        (PathType.TABLE_OR_FIGURE, "Shigley Table 17-2", [[S("t"), S("D_{in\\,min}"), S("F_a"), S("\\gamma"), S("f")], ["belt"]]),
        (PathType.EQUATION, "General Equation lbf/ft",                  Geqn(S("w"),            12*S("\\gamma")*S("b")*S("t"))),  # weight per length [lbs/feet]

        # Tangential Speed and Input Output Ratio
        (PathType.EQUATION, "Shigley Equation pg 887",         Geqn(S("V"),            S("n_{in}")*S("D_{in}")*sym.pi/12)),
        (PathType.EQUATION, "General Equation VR",             Geqn(S("VR"),           S("D_{out}")/S("D_{in}"))),
        (PathType.EQUATION, "General Equation VR",             Geqn(S("VR"),           S("n_{in}")/S("n_{out}"))),

        # Geometry
        (PathType.EQUATION, "Shigley Equation 17-1",           Geqn(S("\\phi_{in}"),   sym.pi-2*sym.asin((S("D_{out}")-S("D_{in}"))/S("CD")))),
        (PathType.EQUATION, "Shigley Equation 17-1",           Geqn(S("\\phi_{out}"),  sym.pi+2*sym.asin((S("D_{out}")-S("D_{in}"))/S("CD")))),
        (PathType.EQUATION, "Shigley Equation 17-2",           Geqn(S("L"),            (4*S("CD")**2 - (S("D_{out}") - S("D_{in}"))**2)**(1/2) + (S("D_{in}")*S("\\phi_{in}")+S("D_{out}")*S("\\phi_{out}"))/2)),
        (PathType.EQUATION, "Shigley Equation 17-13",          Geqn(S("dip"),          S("CD")**2*S("w")/(96*S("F_i")))),

        # Correction Factors
        (PathType.TABLE_OR_FIGURE, "Shigley Table 17-4", [[S("C_p")], ["belt", S("D_{in}")]]),  # based on pulley diameter
        (PathType.CUSTOM, "Shigley Text pg 891", [[S("C_v")], ["belt", S("V")]], compute_cv),  # based on material

        # Torque and Forces
        (PathType.EQUATION, "Shigley Equation pg 892",                  Geqn(S("T_{in}"),       63025*S("H_{des}")/S("n_{in}"))),  # torque on the input side
        (PathType.EQUATION, "Shigley Equation section 17-2 (i)",        Geqn(S("F_i"),          (S("F_{1a}") + S("F_2"))/2-S("F_c"))),
        (PathType.EQUATION, "Shigley Equation section 17-2 (e)",        Geqn(S("F_c"),          (S("V")/60)**2*(S("w")/32.17))),
        (PathType.EQUATION, "Shigley Equation 17-12",                   Geqn(S("F_{1a}"),       S("b") * S("F_a") * S("C_p")*S("C_v"))),
        (PathType.EQUATION, "Shigley Equation section 17-2 (h)",        Geqn(S("F_2"),          S("F_{1a}") - 2*S("T_{in}")/S("D_{in}"))),
        (PathType.EQUATION, "General Equation F1-F2",                   Geqn(S("\\Delta F"),    S("F_{1a}")-S("F_2"))),

        # Power and Selection
        (PathType.EQUATION, "Shigley Equation section 17-2 (j)",        Geqn(S("H_{all}"),      (S("\\Delta F")*S("V"))/33000)),
        (PathType.EQUATION, "Shigley Equation pg 893",                  Geqn(S("H_{des}"),      S("H_{nom}") * S("K_s") * S("n_d"))),
        (PathType.EQUATION, "General Equation safety factor",           Geqn(S("n_{sf}"),       S("H_{all}")/S("H_{des}"))),
    ]

    return pathways


def retrieve_vbelt_information():
    print("Retrieving information for solving vbelt questions from Mott.")
    print("Please note that it only solves upper operation limit due to stress but not lower operation limit from friction.")

    def sheave_selection(knowns):
        logs = []
        if knowns["belt type"] == "3V" or knowns["belt type"] == "3v":
            logs += solve_pathway((PathType.TABLE_OR_FIGURE, "Mott Figure 7-14", [[S("D_{in}"), S("D_{out}"), S("H_{tab}")], [S("VR_{rough}"), S("D_{in\\,rough}")]]), knowns)
        elif knowns["belt type"] == "5V" or knowns["belt type"] == "5v":
            logs += solve_pathway((PathType.TABLE_OR_FIGURE, "Mott Figure 7-15", [[S("D_{in}"), S("D_{out}"), S("H_{tab}")], [S("VR_{rough}"), S("D_{in\\,rough}")]]), knowns)
        elif knowns["belt type"] == "8V" or knowns["belt type"] == "8v":
            logs += solve_pathway((PathType.TABLE_OR_FIGURE, "Mott Figure 7-16", [[S("D_{in}"), S("D_{out}"), S("H_{tab}")], [S("VR_{rough}"), S("D_{in\\,rough}")]]), knowns)
        else:
            raise Exception("unacceptable belt type")
        return logs

    def extra_power(knowns):
        logs = []
        if knowns["belt type"] == "3V" or knowns["belt type"] == "3v":
            logs += solve_pathway((PathType.TABLE_OR_FIGURE, "Mott Figure 7-14", [[S("H_{ext}")], [S("VR")]]), knowns)
        elif knowns["belt type"] == "5V" or knowns["belt type"] == "5v":
            logs += solve_pathway((PathType.TABLE_OR_FIGURE, "Mott Figure 7-17", [[S("H_{ext}")], [S("VR")]]), knowns)
        elif knowns["belt type"] == "8V" or knowns["belt type"] == "8v":
            logs += solve_pathway((PathType.TABLE_OR_FIGURE, "Mott Figure 7-16", [[S("H_{ext}")], [S("VR")]]), knowns)
        else:
            raise Exception("unacceptable belt type")
        return logs

    pathways = [

        # Tangential Speed and Input Output Ratio
        (PathType.EQUATION, "Mott Equation pg 255",             Geqn(S("V_{rough}"),        S("n_{in}")*S("D_{in\\,rough}")*sym.pi/12)),
        (PathType.EQUATION, "Mott Equation pg 255",             Geqn(S("V"),                S("n_{in}")*S("D_{in}")*sym.pi/12)),
        (PathType.EQUATION, "General Equation VR",              Geqn(S("VR_{rough}"),       S("n_{in}")/S("n_{out\\,rough}"))),
        (PathType.EQUATION, "General Equation VR",              Geqn(S("VR"),               S("D_{out}")/S("D_{in}"))),
        (PathType.EQUATION, "General Equation VR",              Geqn(S("VR"),               S("n_{in}")/S("n_{out}"))),

        # Geometry
        (PathType.EQUATION, "Mott Equation 7-17",               Geqn(S("CD_{rough}"),       2*S("D_{out}")+1.5*S("D_{in}"))),
        (PathType.EQUATION, "Mott Equation 7-12",               Geqn(S("L_{rough}"),        2*S("CD_{rough}")+1.57*(S("D_{out}")+S("D_{in}"))+(S("D_{out}")-S("D_{in}"))**2/(4*S("CD_{rough}")))),
        (PathType.TABLE_OR_FIGURE, "Mott Table 7-2",            [[S("L")], [S("L_{rough}")]]),
        (PathType.EQUATION, "Mott Equation 7-13-sub",           Geqn(S("B"),                4*S("L")-2*sym.pi*(S("D_{out}")+S("D_{in}")))),
        (PathType.EQUATION, "Mott Equation 7-13",               Geqn(S("CD"),               (S("B") + sym.sqrt(S("B")**2 - 32*(S("D_{out}") - S("D_{in}"))**2))/16)),
        (PathType.EQUATION, "Mott Equation 7-16",               Geqn(S("d"),                (S("CD")**2-((S("D_{out}")-S("D_{in}"))/2)**2)**0.5)),
        (PathType.EQUATION, "Mott Equation 17-14",              Geqn(S("\\theta_{in}"),     sym.pi-2*sym.asin((S("D_{out}")-S("D_{in}"))/S("CD")))),
        (PathType.EQUATION, "Mott Equation 17-15",              Geqn(S("\\theta_{out}"),    sym.pi+2*sym.asin((S("D_{out}")-S("D_{in}"))/S("CD")))),

        # Correction Factor
        (PathType.TABLE_OR_FIGURE, "Mott Table 7-1", [[S("K_s")], ["driven", "driver", "duty time"]]),  # overload factor
        (PathType.TABLE_OR_FIGURE, "Mott Figure 7-18", [[S("C_{\\theta}")], [S("\\theta_{in}")]]),  # angle correction factor
        (PathType.TABLE_OR_FIGURE, "Mott Figure 7-19", [[S("C_L")], ["belt type", S("L")]]),  # length correction factor

        # Torque and Forces
        # (PathType.EQUATION, "Shigley Equation pg 892",                  Geqn(S("T_{in}"),       63025*S("H_{des}")/S("n_{in}"))),  # torque on the input side
        # (PathType.EQUATION, "Shigley Equation section 17-2 (i)",        Geqn(S("F_i"),          (S("F_{1a}") + S("F_2"))/2-S("F_c"))),
        # (PathType.EQUATION, "Shigley Equation section 17-2 (e)",        Geqn(S("F_c"),          (S("V")/60)**2*(S("w")/32.17))),
        # (PathType.EQUATION, "Shigley Equation 17-12",                   Geqn(S("F_{1a}"),       S("b") * S("F_a") * S("C_p")*S("C_v"))),
        # (PathType.EQUATION, "Shigley Equation section 17-2 (h)",        Geqn(S("F_2"),          S("F_{1a}") - 2*S("T_{in}")/S("D_{in}"))),
        # (PathType.EQUATION, "General Equation F1-F2",                   Geqn(S("\\Delta F"),    S("F_{1a}")-S("F_2"))),

        # Power and Selection
        (PathType.TABLE_OR_FIGURE, "Mott Figure 7-13",          [["belt type"], [S("H_{des}"), S("n_{in}")]]),
        (PathType.EQUATION, "General Equation service factor",  Geqn(S("H_{des}"),          S("H_{nom}") * S("K_s"))),
        (PathType.EQUATION, "Mott Equation pg 262",             Geqn(S("H_{all}"),          S("C_{\\theta}")*S("C_L")*(S("H_{tab}")+S("H_{ext}")))),
        (PathType.CUSTOM, "Mott Text pg 257",                   [[S("H_{ext}")], ["belt type", S("VR")]], extra_power),
        (PathType.EQUATION, "Mott Equation pg 262",             Geqn(S("N_{belt}"),         sym.ceiling(S("H_{des}")/S("H_{all}")))),
        (PathType.CUSTOM, "Mott Text pg 257", [[S("D_{in}"), S("D_{out}"), S("H_{tab}")], ["belt type", S("VR_{rough}"), S("D_{in\\,rough}")]], sheave_selection),
        (PathType.EQUATION, "General Equation safety factor",   Geqn(S("n_{sf}"),           S("H_{des}")/(S("N_{belt}")*S("H_{all}")))),
    ]

    return pathways


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


def retrieve_spurgear_information():
    print("Retrieving information for solving spur gear questions from Mott.")

    def force_gear_combination(knowns):
        logs = []
        min_error = 100
        solution_set = (0, 0, 0)
        for nin in range(knowns[S("N_{in\\,min}")], knowns[S("N_{in\\,max}")]+1):
            error = (round(knowns["VR_{rough}"]*nin)/nin)-knowns["VR_{rough}"]
            if error <= min_error:
                min_error = error
                solution_set = (nin, round(knowns["VR_{rough}"]*nin), (round(knowns["VR_{rough}"]*nin)/nin))
        knowns["N_{in}"] = solution_set[0]
        knowns["N_{out}"] = solution_set[1]
        knowns["VR"] = solution_set[2]

        logs.append("By brute forcing, {solution_set[0]}:{solution_set[1]} is with in the allowed design constraints and is closest to the desired velocity ratio of {knowns['VR_{rough}']}")
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
        elif knowns[S("F")] <= 15:
            knowns[S("C_{pf}")] = ratio/10-0.0375+0.0125*knowns[S("F")]
        else:
            raise Exception("Unexpected Face Width")

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
        (PathType.CUSTOM, "Brute Force Gear Combination",       [["N_{in}", "N_{out}", "N_{VR}"], [S("N_{in\\,min}"), S("N_{in\\,max}"), S("VR_{rough}")]], force_gear_combination),
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


def retrieve_helicalgear_information():
    print("Retrieving information for solving helical gear questions from Mott.")
    print("Please note that the following code is not tested.")

    def force_gear_combination(knowns):
        logs = []
        min_error = 100
        solution_set = (0, 0, 0)
        for nin in range(knowns[S("N_{in\\,min}")], knowns[S("N_{in\\,max}")]+1):
            error = (round(knowns["VR_{rough}"]*nin)/nin)-knowns["VR_{rough}"]
            if error <= min_error:
                min_error = error
                solution_set = (nin, round(knowns["VR_{rough}"]*nin), (round(knowns["VR_{rough}"]*nin)/nin))
        knowns["N_{in}"] = solution_set[0]
        knowns["N_{out}"] = solution_set[1]
        knowns["VR"] = solution_set[2]

        logs.append("By brute forcing, {solution_set[0]}:{solution_set[1]} is with in the allowed design constraints and is closest to the desired velocity ratio of {knowns['VR_{rough}']}")
        return logs

    def compute_J_helical(knowns):
        logs = []
        normal_pressure_angle = math.degrees(knowns[S("\\phi_n")])
        errors = [abs(normal_pressure_angle - v) for v in [15, 20, 22]]
        if errors[0] == min(errors):
            logs += solve_pathway((PathType.TABLE_OR_FIGURE, "Mott Figure 10-5",  [[S("J_{o\\,in}"), S("J_{c\\,in}"), S("J_{o\\,out}"), S("J_{c\\,out}")], [S("N_{in}"), S("N_{out}"), S("\\psi")]]), knowns)
        elif errors[1] == min(errors):
            logs += solve_pathway((PathType.TABLE_OR_FIGURE, "Mott Figure 10-6",  [[S("J_{o\\,in}"), S("J_{c\\,in}"), S("J_{o\\,out}"), S("J_{c\\,out}")], [S("N_{in}"), S("N_{out}"), S("\\psi")]]), knowns)
        elif errors[2] == min(errors):
            logs += solve_pathway((PathType.TABLE_OR_FIGURE, "Mott Figure 10-7",  [[S("J_{o\\,in}"), S("J_{c\\,in}"), S("J_{o\\,out}"), S("J_{c\\,out}")], [S("N_{in}"), S("N_{out}"), S("\\psi")]]), knowns)
        else:
            raise Exception("This should not occur, but if it ever did, something else is wrong.")

        logs += solve_pathway((PathType.EQUATION, "Mott pg 433", Geqn("J_{in}", S("J_{o\\,in}")*S("J_{c\\,in}"))), knowns)
        logs += solve_pathway((PathType.EQUATION, "Mott pg 433", Geqn("J_{out}", S("J_{o\\,out}")*S("J_{c\\,out}"))), knowns)

        return logs

    def compute_I_helical(knowns):
        logs = []
        normal_pressure_angle = math.degrees(knowns[S("\\phi_n")])
        errors = [abs(normal_pressure_angle - v) for v in [20, 25]]
        if errors[0] == min(errors):
            logs += solve_pathway((PathType.TABLE_OR_FIGURE, "Mott Table 10-1",  [[S("I")], [S("N_{in}"), S("N_{out}"), S("\\psi")]]), knowns)
        elif errors[1] == min(errors):
            logs += solve_pathway((PathType.TABLE_OR_FIGURE, "Mott Table 10-2",  [[S("I")], [S("N_{in}"), S("N_{out}"), S("\\psi")]]), knowns)
        else:
            raise Exception("This should not occur, but if it ever did, something else is wrong.")

        return logs

    def compute_Cpf(knowns):
        logs = []
        ratio = knowns[S("F")]/knowns[S("D_{in}")]
        if ratio < 0.5:
            ratio = 0.5
            logs.append("Since that the ratio is too small, 0.5 is used")

        if knowns[S("F")] <= 1:
            knowns[S("C_{pf}")] = ratio/10-0.025
        elif knowns[S("F")] <= 15:
            knowns[S("C_{pf}")] = ratio/10-0.0375+0.0125*knowns[S("F")]
        else:
            raise Exception("Unexpected Face Width")

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
        # get design power is not necessary as there is no table or figure that can be used to selectct diametrical pitch.

        # Tangential Speed and Input Output Ratio
        (PathType.EQUATION, "General Equation VR",              Geqn(S("VR_{rough}"),       S("n_{in}")/S("n_{out\\,rough}"))),
        (PathType.EQUATION, "General Equation VR",              Geqn(S("VR"),               S("n_{in}")/S("n_{out}"))),
        (PathType.EQUATION, "General Equation VR",              Geqn(S("VR"),               S("N_{out}")/S("N_{in}"))),
        (PathType.CUSTOM, "Brute Force Gear Combination",  [["N_{in}", "N_{out}", "N_{VR}"], [S("N_{in\\,min}"), S("N_{in\\,max}"), S("VR_{rough}")]], force_gear_combination),
        (PathType.EQUATION, "General Equation Pitchline Velocity",      Geqn(S("V"), sym.pi*S("D_{in}")*S("n_{in}")/12)),

        # Geometry
        (PathType.EQUATION, "Mott Equation 8-11",                       Geqn(sym.tan(S("\\phi_n")), sym.tan(S("\\phi_t"))*sym.cos(S("\\psi")))),
        (PathType.EQUATION, "Mott Equation 8-16",                       Geqn(S("P_d"), S("P_{nd}")*sym.cos(S("\\psi")))),
        (PathType.EQUATION, "Mott Equation 8-16",                       Geqn(S("p_t"), sym.pi/S("P_d"))),
        (PathType.EQUATION, "Mott Equation 8-14",                       Geqn(S("p_x"), S("p_t")/sym.tan(S("\\psi")))),
        (PathType.EQUATION, "Mott Equation 8-14",                       Geqn(S("p_n"), S("p_t")*sym.tan(S("\\psi")))),
        (PathType.EQUATION, "General Equation Gear Diameter",           Geqn(S("D_{in}"), S("N_{in}")/S("P_d"))),
        (PathType.EQUATION, "General Equation Gear Diameter",           Geqn(S("D_{out}"), S("N_{out}")/S("P_d"))),
        (PathType.EQUATION, "Mott page 325",                            Geqn(S("F"), sym.ceiling(2*S("p_x")))),

        # Torque and Force
        (PathType.EQUATION, "General Equation Torque input shaft ",     Geqn(S("T_{in}"), 63025*S("H_{nom}")/S("n_{in}"))),
        (PathType.EQUATION, "General Equation Transmitted Force",       Geqn(S("W_t"), 2*S("T_{in}")/S("D_{in}"))),
        (PathType.EQUATION, "General Equation Radial Force",            Geqn(S("W_r"), S("W_t")*sym.tan(S("\\phi_t")))),
        (PathType.EQUATION, "General Equation Radial Force",            Geqn(S("W_x"), S("W_t")*sym.tan(S("\\psi")))),

        # Stress Analysis
        # o
        (PathType.TABLE_OR_FIGURE, "Mott Table 9-1", [[S("K_o")], ["driven", "driver"]]),
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
        (PathType.CUSTOM, "Mott Figure 9-10", [[S("J_{in}"), S("J_{out}")], [S("N_{in}"), S("N_{out}"), S("\\psi"), S("\\phi_n")]], compute_J_helical),
        # B
        (PathType.TABLE_OR_FIGURE, "Mott Figure 9-14", [[S("K_B")], []]),
        # sb # the gear stress isn't implemented at all
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
        (PathType.TABLE_OR_FIGURE, "Mott Table 10-1 and 10-2", [[S("I")], [S("N_{in}"), S("N_{out}"), S("\\psi"), S("\\phi_n")]], compute_I_helical),
        # sc
        (PathType.EQUATION, "Mott Equation 9-23", Geqn(S("s_c"), S("C_p")*sym.sqrt(S("W_t")*S("K_o")*S("K_s")*S("K_v")*S("K_m")*S("K_B")/(S("F")*S("I")*S("D_{in}"))))),
        # Z
        (PathType.TABLE_OR_FIGURE, "Mott Figure 9-22", [[S("Z_{in}")], [S("N_{c}")]]),
        # s ac required
        (PathType.EQUATION, "Mott Equation 9-31", Geqn(S("s_{ac\\,min}"), S("s_c")*S("K_R")/S("Z_{in}"))),

        # material selection
        (PathType.CUSTOM, "Mott Table 9-9", [["SAE", S("s_{ab}"), S("s_{ac}")], [S("s_{ab\\,min\\,in}"), S("s_{ac\\,min}")]], compute_material),

        # safety factors
        (PathType.EQUATION, "Mott Equation 9-32", Geqn(S("SF_b"), (S("s_{ab}")*S("Y_{in}"))/(S("s_{b\\,in}")*S("K_R")))),
        (PathType.EQUATION, "Mott Equation 9-33", Geqn(S("SF_c"), (S("s_{ac}")*S("Z_{in}"))/(S("s_c")*S("K_R")))),
        (PathType.EQUATION, "General Equation Safety Factor Comparison", Geqn(S("SF_W"), sym.Min(S("SF_b"), S("SF_c")**2))),
    ]

    return pathways


def retrieve_bevelgear_information():
    print("Retrieving information for solving bevel gear questions from Mott.")
    print("Please note that the following code is not tested.")

    def compute_Km(knowns):
        logs = []
        if (knowns["number of straddle mounted gear"] == 2):
            logs.append("K_{mb} = 1 for both gear straddle mounted")
            knowns[S("K_{mb}")] = 1
        elif (knowns["number of straddle mounted gear"] == 1):
            logs.append("K_{mb} = 1.1 for both gear straddle mounted")
            knowns[S("K_{mb}")] = 1.1
        elif (knowns["number of straddle mounted gear"] == 0):
            logs.append("K_{mb} = 1.25 for both gear straddle mounted")
            knowns[S("K_{mb}")] = 1.25

        logs += solve_pathway((PathType.EQUATION, "Mott Equation 10-16", Geqn(S("K_{mb}"), 0.0036*S("F")**2)), knowns)
        return logs

    def compute_Cxc(knowns):
        logs = []
        if (knowns["is crowned"] == 1):
            logs.append("C_{xc} = 1.5 for properly crowned teeth according to Mott Text pg-450")
            knowns[S("C_{xc}")] = 1.5
        elif (knowns["is crowned"] == 0):
            logs.append("C_{xc} = 2 for properly crowned teeth according to Mott Text pg-450")
            knowns[S("C_{xc}")] = 2

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
        (PathType.EQUATION, "General Equation GR",              Geqn(S("GR"), S("VR"))),

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

        (PathType.EQUATION, "Mott Equation 10-11", Geqn(S("R_{m\\,in}"), S("D_{in}")/2-S("F")*sym.sin("\\gamma"/2))),
        (PathType.EQUATION, "Mott Equation 10-11:", Geqn(S("R_{m\\,out}"), S("D_{out}")/2-S("F")*sym.sin("\\Gamma"/2))),

        # Force Analysis
        (PathType.EQUATION, "General Equation Torque input shaft ",     Geqn(S("T_{in}"), 63025*S("H_{nom}")/S("n_{in}"))),
        (PathType.EQUATION, "General Equation Torque input shaft ",     Geqn(S("T_{out}"), 63025*S("H_{nom}")/S("n_{out}"))),

        (PathType.EQUATION, "Mott Equation 10-10",                      Geqn(S("W_{t\\,in\\,force}"), S("T_{in}")/S("R_{m\\,in}"))),
        (PathType.EQUATION, "Mott Equation 10-12",                      Geqn(S("W_{r\\,in\\,force}"),  S("W_{t\\,force}")*sym.tan(S("\\phi"))*sym.cos("\\gamma"))),
        (PathType.EQUATION, "Mott Equation 10-13",                      Geqn(S("W_{x\\,in\\,force}"),  S("W_{t\\,force}")*sym.tan(S("\\phi"))*sym.sin("\\gamma"))),
        (PathType.EQUATION, "Mott Equation 10-10",                      Geqn(S("W_{t\\,out\\,force}"), S("T_{out}")/S("R_{m\\,out}"))),
        (PathType.EQUATION, "Mott Equation In Figure 10-8:",            Geqn(S("W_{r\\,out\\,force}"), S("W_{x\\,in\\,force}"))),
        (PathType.EQUATION, "Mott Equation In Figure 10-8:",            Geqn(S("W_{x\\,out\\,force}"), S("W_{r\\,in\\,force}"))),

        (PathType.EQUATION, "Mott Equation In Text pg-445",             Geqn(S("W_{t}"), 2*S("T_{in}")/S("D_{in}"))),
        (PathType.EQUATION, "Mott Equation In Text pg-445",             Geqn(S("W_{t}"), 2*S("T_{out}")/S("D_{out}"))),

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
        # Ks # can be modified
        (PathType.TABLE_OR_FIGURE, "Mott Table 9-2", [[S("K_s")], [S("P_d")]]),
        # J
        (PathType.TABLE_OR_FIGURE, "Mott Figure 10-15", [[S("J_{in}"), S("J_{out}")], [S("N_{in}"), S("N_{out}"), S("\\phi")]]),
        # sb
        (PathType.EQUATION, "Mott Equation 10-14",                      Geqn(S("s_{b\\,in}"), S("W_t")*S("P_d")*S("K_o")*S("K_s")*S("K_v")*S("K_m")/(S("F")*S("J_{in}")))),
        (PathType.EQUATION, "Mott Equation 10-14",                      Geqn(S("s_{b\\,out}"), S("W_t")*S("P_d")*S("K_o")*S("K_s")*S("K_v")*S("K_m")/(S("F")*S("J_{out}")))),
        # KLin
        (PathType.TABLE_OR_FIGURE, "Mott Figure 9-21", [[S("K__{L\\,in}")], [S("N_{c\\,in}")]]),
        # s ab required
        (PathType.EQUATION, "Mott Equation 10-18",                       Geqn(S("s_{ab\\,min\\,in}"), S("s_{b\\,in}")*S("K_R")/S("K__{L\\,in}"))),

        # - Contact Stress
        # Cp
        (PathType.TABLE_OR_FIGURE, "Mott Table 9-7",  [[S("C_p")], []]),
        # Cs
        (PathType.EQUATION, "Mott Equation 10-20",                      Geqn(S("C_s"), 0.125*S("F")+0.4375)),
        # Cxc
        (PathType.CUSTOM, "Mott Table 9-7",  [[S("C_{xc}")], ["is crowned"]], compute_Cxc),
        # I
        (PathType.TABLE_OR_FIGURE, "Mott Figure 10-19", [[S("I")], [S("N_{in}"), S("N_{out}"), S("\\psi"), S("\\phi_n")]]),
        # sc
        (PathType.EQUATION, "Mott Equation 9-23",                       Geqn(S("s_c"), S("C_p")*sym.sqrt(S("W_t")*S("K_o")*S("C_s")*S("K_v")*S("K_m")*S("C_{xc}")/(S("F")*S("I")*S("D_{in}"))))),
        # CL
        (PathType.TABLE_OR_FIGURE, "Mott Figure 9-22", [[S("C_L")], [S("N_{c\\,in}")]]),
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


def retrieve_wormgeam_information():
    print("Retrieving information for solving bevel gear questions from Mott.")
    print("Please note that the following code is not tested.")

    def compute_friction_coefficient(knowns):
        logs = []
        # page 457
        if knowns[S("v_s")] == 0:
            logs.append("Static condition")
            logs += solve_pathway((PathType.EQUATION, "Mott Equation pg 457",  Geqn(S("\\mu"), 0.15)), knowns)
        elif knowns[S("v_s")] < 10:
            logs.append("Low speed")
            logs += solve_pathway((PathType.EQUATION, "Mott Equation 10-26",  Geqn(S("\\mu"), 0.124*sym.exp(-0.074*(S("v_s")**0.645)))), knowns)
        else:
            logs.append("High speed")
            logs += solve_pathway((PathType.EQUATION, "Mott Equation 10-26",  Geqn(S("\\mu"), 0.103*sym.exp(-0.110*(S("v_s")**0.450))+0.012)), knowns)
        return logs

    def compute_Cv(knowns):
        logs = []
        if (knowns[S("v_s")] < 700):
            logs += solve_pathway((PathType.EQUATION, "Mott Equation 10-49",  Geqn(S("C_v"), 0.659*sym.exp(-0.0011*S("v_s"))), knowns))
        elif (knowns[S("v_s")] < 3000):
            logs += solve_pathway((PathType.EQUATION, "Mott Equation 10-49",  Geqn(S("C_v"), 13.31*(S("v_s")**(-0.571))), knowns))
        else:
            logs += solve_pathway((PathType.EQUATION, "Mott Equation 10-49",  Geqn(S("C_v"), 65.52*(S("v_s")**(-0.774))), knowns))
        return logs

    def compute_Fe(knowns):
        logs = []
        if (knowns[S("F")] > 0.67 * knowns[S("D_{in}")]):
            logs.append("Wormgear face width is wider than 2/3 of worm diameter. As a result, the effective face width of 2/3 worm diameter is used.")
            knowns[S("F_e")] = 0.67 * knowns[S("D_{in}")]
        else:
            logs.append("Wormgear face width is thinned than 2/3 of worm diameter. As a result, the effective face is the face width.")
            knowns[S("F_e")] = knowns[S("F")]
        return logs

    pathways = [
        # get design power is not necessary as there is no table or figure that can be used to selectct diametrical pitch.

        # Speed and Input Output Ratio
        (PathType.EQUATION, "Mott Equation pg 333",             Geqn(sym.tan(S("v_{t\\,in}")), (sym.pi*S("D_{in}")*S("n_{in}")/12))),
        (PathType.EQUATION, "Mott Equation pg 334",             Geqn(sym.tan(S("v_{t\\,out}")), (sym.pi*S("D_{out}")*S("n_{out}")/12))),
        (PathType.EQUATION, "Mott Equation 10-24",              Geqn(sym.tan(S("v_s")), S("v_{t\\,out}")/sym.sin(S("\\lambda")))),

        (PathType.EQUATION, "General Equation VR",              Geqn(S("VR_{rough}"),       S("n_{in}")/S("n_{out\\,rough}"))),
        (PathType.EQUATION, "General Equation VR",              Geqn(S("VR"),               S("n_{in}")/S("n_{out}"))),
        (PathType.EQUATION, "General Equation VR",              Geqn(S("VR"),               S("N_{out}")/S("N_{in}"))),
        (PathType.EQUATION, "General Equation GR",              Geqn(S("GR"),               S("VR"))),
        (PathType.EQUATION, "General Equation GR",              Geqn(S("m_G"),              S("VR"))),

        # Geometry
        (PathType.EQUATION, "Mott Equation 8-20",               Geqn(S("p"), sym.pi*S("D_{out}")/S("N_{out}"))),
        (PathType.EQUATION, "Mott Equation 8-14",               Geqn(S("p_n"), S("p")*sym.cos("lambda"))),
        (PathType.EQUATION, "Mott Equation 8-21",               Geqn(S("P_d"), S("N_{out}")/S("D_{out}"))),
        (PathType.EQUATION, "Mott Equation 8-23",               Geqn(S("Lead"), S("N_{in}")*S("p"))),
        (PathType.EQUATION, "Mott Equation 8-23",               Geqn(sym.tan(S("\\lambda")), S("Lead")/(sym.pi*S("D_{in}")))),
        (PathType.EQUATION, "Mott Equation 8-26",               Geqn(sym.tan(S("\\phi_n")), sym.tan(S("\\phi_t"))*sym.cos(S("\\lambda")))),

        # Torque and Force

        (PathType.CUSTOM, "Mott Text pg 457",                          [[S("\\mu")], [S("v_s")]], compute_friction_coefficient),

        (PathType.EQUATION, "General Equation Torque input shaft",     Geqn(S("T_{in}"), 63025*S("H_{in}")/S("n_{in}"))),
        (PathType.EQUATION, "General Equation Torque input shaft",     Geqn(S("T_{out}"), 63025*S("H_{out}")/S("n_{out}"))),

        (PathType.EQUATION, "Mott Equation 10-29",                      Geqn(S("W_{t\\,out}"), 2*S("T_{out}")/S("D_{out}"))),
        (PathType.EQUATION, "Mott Equation 10-30",                      Geqn(S("W_{x\\,out}"), S("W_{t\\,out}") *
                                                                             (sym.cos(S("\\phi_n"))*sym.sin(S("\\lambda"))+S("\\mu")*sym.cos(S("\\lambda"))) /
                                                                             (sym.cos(S("\\phi_n"))*sym.cos(S("\\lambda"))-S("\\mu")*sym.sin(S("\\lambda")))
                                                                             )),
        (PathType.EQUATION, "Mott Equation 10-31",                      Geqn(S("W_{r\\,out}"), S("W_{t\\,out}") *
                                                                             (sym.sin(S("\\phi_n"))) /
                                                                             (sym.cos(S("\\phi_n"))*sym.cos(S("\\lambda"))-S("\\mu")*sym.sin(S("\\lambda")))
                                                                             )),
        (PathType.EQUATION, "Mott Equation 10-23",                       Geqn(S("W_{t\\,in}"), S("W_{x\\,out}"))),
        (PathType.EQUATION, "Mott Equation 10-23",                       Geqn(S("W_{x\\,in}"), S("W_{t\\,out}"))),
        (PathType.EQUATION, "Mott Equation 10-23",                       Geqn(S("W_{r\\,in}"), S("W_{r\\,out}"))),

        (PathType.EQUATION, "Mott Equation 10-32",                      Geqn(S("W_f"), S("W_{t\\,out}") *
                                                                             (S("\\mu")) /
                                                                             (sym.cos(S("\\phi_n"))*sym.cos(S("\\lambda"))-S("\\mu")*sym.sin(S("\\lambda")))
                                                                             )),

        # Stress (skipped for no use in the process of selection)

        # Power
        (PathType.EQUATION, "Mott Equation 10-33",                      Geqn(S("H_{loss}"), S("v_s") * sym.sin(S("W_f")) / 33000)),
        (PathType.EQUATION, "Mott Equation 10-34",                      Geqn(S("H_{out}"), S("H_{in}")-S("H_{loss}"))),
        (PathType.EQUATION, "Mott Equation 10-35",                      Geqn(S("\\eta"), S("H_{out}")/S("H_{in}"))),

        # Rated Load
        (PathType.TABLE_OR_FIGURE, "Mott Table 10-27",  [[S("C_s")], [S("P_d")]]),
        (PathType.TABLE_OR_FIGURE, "Mott Table 10-28",  [[S("C_m")], [S("m_G")]]),
        (PathType.CUSTOM, "Mott Text pg-461",      [[S("F_e")], [S("F"), S("D_{in}")]], compute_Fe),
        (PathType.CUSTOM, "Mott Text pg-463",      [[S("C_v")], [S("v_s")]], compute_Cv),
        (PathType.EQUATION, "Mott Equation 10-42",      Geqn(S("W_{tR}"), S("C_s")*(S("D_{out}")**0.8)*S("C_m")*S("F_e")*S("C_v"))),
    ]

    return pathways


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


def retrieve_shaft_point_information_shigley():
    print("Retrieving information for solving shaft stresses with mixed loading questions from Shigley.")
    print("Please note that it only solves for stresses and doesn't do selection or iteration yet.")

    def find_kb(knowns):
        # unit is in inches
        logs = []
        if 0.3 <= knowns[S("d")] and knowns[S("d")] < 2:
            logs += solve_pathway(PathType.EQUATION, "Shigley Equation 6-19", Geqn(S("K_b"), 0.879*(knowns[S("d")])**(-0.107)))
        elif knowns[S("d")] < 10:
            logs += solve_pathway(PathType.EQUATION, "Shigley Equation 6-19", Geqn(S("K_b"), 0.91*(knowns[S("d")])**(-0.157)))
        return logs

    pathways = [
        # get design power is not necessary as there is no table or figure that can be used to selectct diametrical pitch.
        (PathType.TABLE_OR_FIGURE, "Shigley Figure 6-26", [[S("q_b")], [S("r_{notch}"), S("S_{ut}")]]),
        (PathType.TABLE_OR_FIGURE, "Shigley Figure 6-27", [[S("q_s")], [S("r_{notch}"), S("S_{ut}")]]),
        (PathType.EQUATION, "Shigle Equation 6-31a", Geqn(S("K_{fb}"), 1+S("q_b")*(S("K_{tb}")-1))),
        (PathType.EQUATION, "Shigle Equation 6-31b", Geqn(S("K_{fs}"), 1+S("q_s")*(S("K_{ts}")-1))),

        (PathType.EQUATION, "Shigley Equation 6-10", Geqn(S("S_e'"), sym.Min(100, S("S_{ut}")/2))),  # unit is in ksi
        (PathType.TABLE_OR_FIGURE, "Shigley Figure 6-24", [[S("K_a")], [S("S_{ut}")]]),
        (PathType.CUSTOM, "Shigley Figure 6-19", [[S("K_b")], [S("d")]], find_kb),
        (PathType.EQUATION, "Shigley Equation 6-25", Geqn(S("K_c"), 1)),  # for vast majority of the time, the alternating load is the bending moment.
        (PathType.EQUATION, "Assumed At Room Temperature", Geqn(S("K_d"), 1)),  # assume room temperature
        (PathType.TABLE_OR_FIGURE, "Shigley Table 6-4", [[S("K_e")], [S("R")]]),
        (PathType.EQUATION, "Assumed", Geqn(S("K_f"), 1)),

        (PathType.EQUATION, "Shigley Equation 6-10", Geqn(S("S_e"), S("K_a")*S("K_b")*S("K_c")*S("K_d")*S("K_e")*S("K_f")*S("S_e'"))),  # unit is in ksi
        (PathType.EQUATION, "Shigley Equation 7-6a", Geqn(
            S("A"),
            sym.sqrt(
                (8*S("K_{fb}")*S("M_a"))**2 +
                48*(S("K_{fs}")*S("T_a"))**2
            )/1000
        )),
        (PathType.EQUATION, "Shigley Equation 7-6b", Geqn(
            S("B"),
            sym.sqrt(
                (8*S("K_{fb}")*S("M_m"))**2 +
                48*(S("K_{fs}")*S("T_m"))**2
            )/1000
        )),

        # The commented out pathes are a variation of the above two lines but including axial loads.
        # (PathType.EQUATION, "Shigley Equation 7-6a", Geqn(
        #     S("A"),
        #     sym.sqrt(
        #         (8*S("K_{fb}")*S("M_a")+S("K_{fa}")*S("F_a")*S("d"))**2 +
        #         48*(S("K_{fs}")*S("T_a"))**2
        #     )/1000
        # )),
        # (PathType.EQUATION, "Shigley Equation 7-6b", Geqn(
        #     S("B"),
        #     sym.sqrt(
        #         (8*S("K_{fb}")*S("M_m")+S("K_{fa}")*S("F_m")*S("d"))**2 +
        #         48*(S("K_{fs}")*S("T_m"))**2
        #     )/1000
        # )),

        (PathType.EQUATION, "DE-Goodman", Geqn(
            S("n_{f\\,Goodman}"),
            (sym.pi/4)
            * S("d")**3
            * (S("A")/S("S_e")+S("B")/S("S_{ut}"))**-1
        )),

        # # The commented out Pathways Below are different Fatigue Failure Criteria.
        (PathType.EQUATION, "Shigley Equation 6-44", Geqn(S("\\tilde{\\sigma_f}"), S("S_{ut}")+50)),  # unit is in ksi
        (PathType.EQUATION, "DE-Morrow", Geqn(
            S("n_{f\\,Morrow}"),
            (sym.pi/4)
            * S("d")**3
            * (S("A")/S("S_e")+S("B")/S("\\tilde{\\sigma_f}"))**-1
        )),

        (PathType.EQUATION, "DE-Gerber", Geqn(
            S("n_{f\\,Gerber}"),
            (sym.pi/8)
            * S("d")**3
            * S("S_e")/S("A")
            * (
                1
                + sym.sqrt(
                    1
                    + (2*S("B")*S("S_e")/(S("A")*S("S_{ut}")))**2
                )**(1/2)
            )**-1
        )),

        (PathType.EQUATION, "DE-SWT", Geqn(
            S("n_{f\\,SWT}"),
            (sym.pi/16)
            * S("d")**3
            * S("S_e")/(S("A")**2+S("A")*S("B"))**(1/2)
        )),

        (PathType.EQUATION, "von Mises", Geqn(
            S("n_y"),
            (
                (
                    32*S("K_f")*(S("M_m")+S("M_a"))
                    / (sym.pi*S("d")**3)
                )**2
                + 3*(
                    32*S("K_{fs}")*(S("T_m")+S("T_a"))
                    / (sym.pi*S("d")**3)
                )**2
            )**(1/2)
        )),
    ]

    return pathways


def retrieve_shaft_point_information_mott():
    print("Retrieving information for solving shaft stresses with mixed loading questions from Mott and Shigley.")
    print("Please note that this only solves for one point on the shaft.")

    def diameter_iteration(knowns):
        logs = []
        if knowns[S("D_{iter}")] > knowns[S("D_{min}")]:
            logs.append(f'Since $D_{{iter}} = {knowns[S("D_{iter}")]:7.2f} > {knowns[S("D_{min}")]:7.2f} = D_{{min}}$, the current selected diameter is good.')
            knowns[S("D")] = knowns[S("D_{iter}")]
        else:
            new_iter_d = math.ceil(4*knowns[S("D_{min}")])/4
            logs.append(f'Since $D_{{iter}} = {knowns[S("D_{iter}")]:7.2f} < {knowns[S("D_{min}")]:7.2f} = D_{{min}}$, round $D_{{min}}$ up to ${new_iter_d}$ and let it be the new $D_{{iter}}$ to continue iteration.')
            knowns[S("D_{iter}")] = new_iter_d
            discards = [S("C_s"), S("s_n'"), S("D_{min\\,s}"), S("D_{min\\,t}"), S("D_{min}")]
            for discard in discards:
                if discard in knowns:
                    knowns.pop(discard)
        return logs

    def cs_mock(knowns):
        knowns[S("C_s")] = round((2.85289**(knowns[S("D_{iter}")]**(-0.0857608))-2.15255)/2+0.5, 2)

    def shear_wrapper(knowns):
        logs = []
        if knowns[S("V")] != 0:
            logs += solve_pathway((PathType.EQUATION, "Mott 12-16", Geqn(S("D_{min\\,s}"), sym.sqrt(2.94*S("K_t")*S("V")*S("N")/S("s_n'")))), knowns)
        else:
            knowns[S("D_{min\\,s}")] = 0
        return logs

    def moment_wrapper(knowns):
        logs = []
        if knowns[S("M")] != 0 or knowns[S("T")] != 0:
            logs += solve_pathway((PathType.EQUATION, "Mott 12-24", Geqn(
                S("D_{min\\,t}"),
                sym.cbrt(
                    32*S("N")/sym.pi *
                    sym.sqrt(
                        (S("K_t")*S("M")/S("s_n'"))**2 +
                        3/4*(S("T")/S("s_y"))**2
                    )
                )
            )), knowns)
        else:
            knowns[S("D_{min\\,t}")] = 0
        return logs

    pathways = [
        (PathType.EQUATION, "Make a Guess", Geqn(S("D_{iter}"), 0.5)),
        (PathType.TABLE_OR_FIGURE, "Mott Table Appendix-3", [[S("s_u"), S("s_y")], ["SAE"]]),
        (PathType.TABLE_OR_FIGURE, "Mott Figure 5-11", [[S("s_n")], [S("s_u"), "surface condition"]]),
        (PathType.EQUATION, "Mott pg-178", Geqn(S("C_m"), 1)),
        (PathType.EQUATION, "Mott pg-178", Geqn(S("C_{st}"), 1)),
        (PathType.TABLE_OR_FIGURE, "Mott Table 5-3", [[S("C_R")], ["Reliability"]]),
        (PathType.MOCK_TABLE_OR_FIGURE, "Mott Figure 5-12", [[S("C_s")], [S("D_{iter}")]], cs_mock),
        (PathType.EQUATION, "Mott 5-21", Geqn(S("s_n'"), S("s_n")*S("C_m")*S("C_{st}")*S("C_R")*S("C_s"))),

        (PathType.CUSTOM, "Shear Wrapper", [[S("D_{min\\,s}")], [S("K_t"), S("V"), S("N"), S("s_n'")]], shear_wrapper),
        (PathType.CUSTOM, "Moment Wrapper", [[S("D_{min\\,t}")], [S("K_t"), S("M"), S("T"), S("N"), S("s_n'"), S("s_y")]], moment_wrapper),

        (PathType.EQUATION, "Pick Maximum", Geqn(
            S("D_{min}"),
            sym.Max(S("D_{min\\,s}"), S("D_{min\\,t}"))
        )),

        (PathType.CUSTOM, "Diameter Iteration", [[S("D")], [S("D_{iter}"), S("D_{min}")]], diameter_iteration)
    ]

    return pathways

#################################################################
#                                                               #
# Below this line is the core python code that solves problems  #
#                                                               #
#################################################################


def solve_pathway(pathway, knowns):
    if pathway[0] == PathType.EQUATION:
        unknowns = []
        symbols_in_eqn = pathway[2].free_symbols
        for symbol_in_eqn in symbols_in_eqn:
            if not symbol_in_eqn in knowns:
                unknowns.append(symbol_in_eqn)

        if len(unknowns) > 1:
            raise Exception("Solving equation that cannot be solved")
        unknown = unknowns[0]

        expression = sym.solve(pathway[2], unknown)[0]
        direct_latex = sym.latex(unknown) + " &= " + sym.latex(touch(expression), order=None) + f"\\tag{{{pathway[1]}}}"

        substitution_dict = {}
        for known in knowns:
            if isinstance(known, sym.Expr):
                substitution_dict[known] = knowns[known]
        knowns[unknown] = expression.evalf(subs=substitution_dict)
        with sym.evaluate(False):

            subbed_expression = expression.subs({key: round_nsig(float(substitution_dict[key]), 5) for key in substitution_dict})
            subbed_latex = sym.latex(unknown) + " &= " + sym.latex(touch(subbed_expression))

        latex_entry = r"\begin{align*}"
        latex_entry += "\n    "+direct_latex
        if len(symbols_in_eqn) > 1:
            latex_entry += r"\\"+"\n    "+subbed_latex
            latex_entry += r"\\"+"\n    "+sym.latex(touch(sym.Eq(unknown, knowns[unknown]))).replace("=", "&=")
        latex_entry += "\n"+r"\end{align*}"

        return [latex_entry]

    # if figure, prompt it.
    if pathway[0] == PathType.TABLE_OR_FIGURE:
        file_path = ["References"]+pathway[1].split(" ")
        file_path[-1] += ".png"
        img = cv2.imread(join(*file_path))
        cv2.imshow(pathway[1], img)
        cv2.waitKey(1)

        query_keys = pathway[2][1]
        for symbol in query_keys:
            if isinstance(symbol, sym.Expr):
                print(f"    {sym.pretty(symbol, use_unicode=True)} = {round_nsig(knowns[symbol],4)}")
            else:
                print(f"    {symbol} = {knowns[symbol]}")

        knowables = pathway[2][0]
        new_knowledge = []
        for knowable in knowables:
            if not knowable in knowns:
                print(f"what is {sym.pretty(knowable, use_unicode=True)}?")
                raw_input = input("  > ")
                knowns[knowable] = float(raw_input) if isinstance(knowable, sym.Expr) else raw_input
                new_knowledge.append(knowable)

        cv2.destroyAllWindows()

        substring = ', '.join([f'${sym.latex(symbol)} = {round_nsig(knowns[symbol],3)} $' if isinstance(symbol, sym.Expr) else f'$\\text{{{symbol}}} = \\text{{{knowns[symbol]}}} $' for symbol in query_keys])
        return_string = f"Query {pathway[1]} with {substring}: "
        substring = "\n"+'\n'.join([f'$${sym.latex(symbol)} = {knowns[symbol]} $$' if isinstance(symbol, sym.Expr) else f'$$\\text{{{symbol}}} = {knowns[symbol]} $$' for symbol in new_knowledge])
        return_string += substring
        return [return_string]

    # if is a mock of a table, evaluate with the mock.
    if pathway[0] == PathType.MOCK_TABLE_OR_FIGURE:
        substring = ', '.join([
            f'${sym.latex(symbol)} = {round_nsig(knowns[symbol],3)} $'
            if isinstance(symbol, sym.Expr) else
            f'$\\text{{{symbol}}} = \\text{{{knowns[symbol]}}} $'
            for symbol in pathway[2][1]])

        return_string = f"Query {pathway[1]} with {substring}: "

        new_knowledge = [a for a in pathway[2][0] if not a in knowns]

        pathway[3](knowns)

        substring = "\n"+'\n'.join([
            f'$${sym.latex(symbol)} = {knowns[symbol]} $$'
            if isinstance(symbol, sym.Expr)
            else f'$$\\text{{{symbol}}} = {knowns[symbol]} $$'
            for symbol in new_knowledge])

        return_string += substring
        return [return_string]

    # if conditional, recursion it.
    if pathway[0] == PathType.CUSTOM:

        logs = pathway[3](knowns)

        return logs


def query_pathways(context):
    if (context["component_type"] == ComponentType.FLAT_BELT):
        pathways = retrieve_flatbelt_information()
    elif (context["component_type"] == ComponentType.V_BELT):
        pathways = retrieve_vbelt_information()
    elif (context["component_type"] == ComponentType.SYNCHRONOUS_BELT):
        pathways = retrieve_syncbelt_information()
    elif (context["component_type"] == ComponentType.CHAIN):
        pathways = retrieve_chain_information()
    elif (context["component_type"] == ComponentType.SPUR_GEAR):
        pathways = retrieve_spurgear_information()
    elif (context["component_type"] == ComponentType.HELICAL_GEAR):
        pathways = retrieve_helicalgear_information()
    elif (context["component_type"] == ComponentType.BOUNDARY_LUBRICATED_BEARING):
        pathways = retrieve_bushing_information()
    elif (context["component_type"] == ComponentType.BALL_AND_CYLINDRICAL_BEARING_RADIAL):
        pathways = retrieve_bcbearingradial_information()
    elif (context["component_type"] == ComponentType.BALL_AND_CYLINDRICAL_BEARING_ALL):
        pathways = retrieve_bcbearingall_information()
    elif (context["component_type"] == ComponentType.TAPERED_ROLLER_BEARING):
        pathways = retrieve_tbeaing_information()
    elif (context["component_type"] == ComponentType.SHAFT_POINT):
        pathways = retrieve_shaft_point_information_mott()
    else:
        raise NotImplementedError("not implemented")
    return pathways


def list_vars(context):

    vars = []
    pathways = query_pathways(context)
    for pathway in pathways:
        if pathway[0] == PathType.EQUATION:
            symbols = pathway[2].free_symbols
        else:
            symbols = pathway[2][0]+pathway[2][1]
        for s in symbols:
            if not s in vars:
                vars.append(s)

    text_vars = []
    symbolic_vars = []

    for var in vars:
        if isinstance(var, sym.Expr):
            symbolic_vars.append(var)
        else:
            text_vars.append(var)

    print("The following are text type variables")
    text_vars.sort()
    for var in text_vars:
        print(var)

    print("The following are value type variables")
    symbolic_vars.sort(key=lambda x: sym.latex(x))
    for var in symbolic_vars:
        print(var)

    return text_vars, symbolic_vars


def analyze(context, is_full_problem=True):

    pathways = query_pathways(context)

    # this keeps track of how each of the variables is found. (found variable) : (pathway used to derive it)
    source = {}

    mock_knowns = set(context["vars"].keys())

    # solve a tree
    while True:
        # check completion
        for target in context["targets"]:
            if not target in mock_knowns:
                break
        else:
            break

        # for each equation, check if there is a equation where only 1 value is missing.
        # for each figure, check if there is a figure where only 1 value is missing.
        # this solution complete ignores the case of coupled equations but it doesn't exist in this unit so whatever.

        for i in range(len(pathways)):
            pathway = pathways[i]
            path_type = pathway[0]

            if (path_type == PathType.TABLE_OR_FIGURE or
                path_type == PathType.MOCK_TABLE_OR_FIGURE or
                    path_type == PathType.CUSTOM):
                symbols_retrievable = pathway[2][0]
                symbols_needed = pathway[2][1]

                # if all values are known, no need to go down this path
                all_know = True
                for symbol_retrievable in symbols_retrievable:
                    if not symbol_retrievable in mock_knowns:
                        all_know = False
                        break
                if all_know:
                    continue

                # if cannot solve yet, no need to continue.
                can_solve = True
                for symbol_needed in symbols_needed:
                    if not symbol_needed in mock_knowns:
                        can_solve = False
                        break
                if not can_solve:
                    continue

                for symbol_retrievable in symbols_retrievable:
                    if not symbol_retrievable in mock_knowns:
                        mock_knowns.add(symbol_retrievable)
                        source[symbol_retrievable] = i

            elif path_type == PathType.EQUATION:
                symbols_in_eqn = pathway[2].free_symbols

                unsolved = 0
                unknown_symbol = 0
                for symbol_in_eqn in symbols_in_eqn:
                    if (not symbol_in_eqn in mock_knowns):
                        unsolved += 1
                        unknown_symbol = symbol_in_eqn

                if unsolved == 1:
                    mock_knowns.add(unknown_symbol)
                    source[unknown_symbol] = i

    # start solving and removing extra branches
    knowns = context["vars"]

    logs = []

    target_stack = context["targets"].copy()
    target_stack.reverse()
    while len(target_stack) > 0:

        # get top of target stack
        target = target_stack[-1]
        if (target) in knowns:
            target_stack.pop()
            continue

        # if not solvable yet, add new targets to stack
        pathway = pathways[source[target]]
        path_type = pathway[0]
        solvable = True

        if (path_type == PathType.TABLE_OR_FIGURE or
            path_type == PathType.MOCK_TABLE_OR_FIGURE or
                path_type == PathType.CUSTOM):
            symbols_needed = pathway[2][1]

            # if cannot solve yet, no need to continue.
            can_solve = True
            for symbol_needed in symbols_needed:
                if not symbol_needed in knowns:
                    target_stack.append(symbol_needed)
                    solvable = False

        elif path_type == PathType.EQUATION:
            symbols_in_eqn = pathway[2].free_symbols
            for symbol_in_eqn in symbols_in_eqn:
                if symbol_in_eqn == target:
                    continue
                if not symbol_in_eqn in knowns:
                    target_stack.append(symbol_in_eqn)
                    solvable = False

        if not solvable:
            continue

        # if solvable
        logs += solve_pathway(pathway, knowns)

    if (is_full_problem):
        summary_lines = "\nFinal Design Parameters:\\\\"
        summary_lines += "\n\\begin{tabular}{lll}"
        for target in context["targets"]:
            if isinstance(target, sym.Expr):
                summary_lines += f"\n    ${sym.latex(target)}$ & : & {round_nsig(knowns[target],3)}"+r"\\"
            else:
                summary_lines += f"\n    {target} & : & {knowns[target]}"+r"\\"
        summary_lines += "\n\\end{tabular}"
        logs.append(summary_lines)

    return logs


def compile_latex(logs):
    import subprocess
    import os
    from os.path import join
    import re

    latex_output = "\n\n".join(logs)
    # remove space between slign blocks
    latex_output = re.sub(r"\\end\{align\*\}\n\n\\begin\{align\*\}", r"\\end{align*}\n\\begin{align*}", latex_output)
    with open(join("latex_output", "solution.tex"), "w+") as fi:
        fi.write(latex_output)

    print("Solution Output Successful")

    print("Compiling Latex into PDF format.")
    subprocess.Popen(
        "pdflatex -output-directory=aux main.tex",
        shell=True,
        cwd=join(os.getcwd(), 'latex_output'),
        stdout=subprocess.DEVNULL)
    print("Compilation successful.")

# < I despise 325 with this many lines of code.
