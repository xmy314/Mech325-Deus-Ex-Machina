import sympy as sym
import math
from sympy import Symbol as S
from enum import Enum
from math import radians, copysign
from sympy import sin, cos, tan, sqrt
from os.path import join
from mech325.infrastructure import round_nsig, ComponentType, PathType, Geqn, analyze, solve_pathway, compile_latex, touch


def geometry(context):
    logs = []

    for bolt in context["bolts"]:
        bolt[S("t")] = context["bracket"][S("t")]

    total_area = 0
    x_area = 0
    y_area = 0
    polar_moment_of_area = 0

    for bolt in context["bolts"]:
        bolt[S("A")] = (math.pi/4)*bolt[S("d")]**2
        total_area += bolt[S("A")]
        x_area += bolt[S("A")]*bolt[S("x")]
        y_area += bolt[S("A")]*bolt[S("y")]

    context["vars"][S("X_c")] = x_area/total_area
    context["vars"][S("Y_c")] = y_area/total_area

    for bolt in context["bolts"]:
        bolt["rcx"] = bolt[S("x")]-context["vars"][S("X_c")]
        bolt["rcy"] = bolt[S("y")]-context["vars"][S("Y_c")]
        bolt["rc"] = ((bolt["rcx"])**2+(bolt["rcy"])**2)**(1/2)
        polar_moment_of_area += bolt[S("A")]*bolt["rc"]*bolt["rc"]

    context["vars"][S("J")] = polar_moment_of_area

    return logs


def force_analysis(context):
    logs = []
    fx = 0
    fy = 0
    mz = 0
    for load in context["loads"]:
        fx += load["fx"]
        fy += load["fy"]
        mz += load["x"]*load["fy"] - load["y"]*load["fx"]
    context["vars"][S("f_{xtot}")] = fx
    context["vars"][S("f_{ytot}")] = fy
    context["vars"][S("m_{ztot}")] = mz
    return logs


def stress_analysis(context):
    logs = []
    primary_x = context["vars"][S("f_{xtot}")]/len(context["bolts"])
    primary_y = context["vars"][S("f_{ytot}")]/len(context["bolts"])

    max_shear = -1
    max_index = 0

    for (i, bolt) in enumerate(context["bolts"]):
        bolt["F'_x"] = primary_x
        bolt["F'_y"] = primary_y
        bolt["F''_x"] = -context["vars"][S("m_{ztot}")]*bolt[S("A")]*bolt["rcy"]/context["vars"][S("J")]
        bolt["F''_y"] = context["vars"][S("m_{ztot}")]*bolt[S("A")]*bolt["rcx"]/context["vars"][S("J")]

        bolt[S("F")] = ((bolt["F'_x"])**2+(bolt["F'_y"])**2+(bolt["F''_x"])**2+(bolt["F''_y"])**2)**(1/2)
        if bolt[S("F")] > max_shear:
            max_shear = bolt[S("F")]
            max_index = i

    logs.append(f'bolt at x = {context["bolts"][max_index][S("x")]}, y = {context["bolts"][max_index][S("y")]} have the highest shear and is selected for analysis.')

    def get_sy(knowns):
        logs = []
        if "SAE" in knowns["grade"]:
            pathway = (PathType.TABLE_OR_FIGURE, "Shigley Table 8-9", [[S("S_y")], ["grade"]])
        elif "ASTM" in knowns["grade"]:
            pathway = (PathType.TABLE_OR_FIGURE, "Shigley Table 8-10", [[S("S_y")], ["grade"]])
        elif "ISO" in knowns["grade"]:
            pathway = (PathType.TABLE_OR_FIGURE, "Shigley Table 8-11", [[S("S_y")], ["grade"]])
        else:
            raise Exception("Please identify the standard in \"grade\". [SAE, ISO, ASTM]")
        logs += solve_pathway(pathway, knowns)
        return logs

    bolt_pathways = [
        (PathType.CUSTOM, "Shigley Table 8-9 to 8-11", [[S("S_y")], ["grade"]], get_sy),
        (PathType.EQUATION, "Shigley Equation TODO", Geqn(S("S_{sy}"), S("S_y")/sym.sqrt(3))),
        (PathType.EQUATION, "Shigley Equation TODO", Geqn(S("\\tau"), S("F")/S("A"))),
        (PathType.EQUATION, "Shigley Equation TODO", Geqn(S("n_{\\text{bolt shear}}"), S("S_{sy}")/S("\\tau"))),

        (PathType.EQUATION, "Shigley Equation TODO", Geqn(S("\\sigma"), S("F")/(S("t")*S("d")))),
        (PathType.EQUATION, "Shigley Equation TODO", Geqn(S("n_{\\text{bolt bearing}}"), S("S_y")/S("\\sigma"))),
    ]

    bolt_sub_problem = {
        "component_type": ComponentType.CUSTOM,
        "pathways": bolt_pathways,
        "vars": context["bolts"][max_index],
        "targets": [
            S("n_{\\text{bolt shear}}"),
            S("n_{\\text{bolt bearing}}"),
        ]
    }

    logs += analyze(bolt_sub_problem, is_full_problem=False)

    context["bracket"]["weak point"][S("\\sigma")] = context["bolts"][max_index][S("\\sigma")]

    bracket_pathways = [
        (PathType.TABLE_OR_FIGURE, "Shigley Table A-20", [[S("S_y")], ["grade"]]),
        (PathType.EQUATION, "Shigley Equation TODO", Geqn(S("n_{\\text{bracket bearing}}"), S("S_y")/S("\\sigma"))),
        (PathType.EQUATION, "Shigley Equation TODO", Geqn(S("\\sigma_{bending}"), S("M")*S("y")/S("I"))),
        (PathType.EQUATION, "Shigley Equation TODO", Geqn(S("n_{\\text{bracket bending}}"), S("S_y")/S("\\sigma_{bending}"))),
    ]

    context["bracket"]["weak point"].update(context["bracket"])
    bracket_sub_problem = {
        "component_type": ComponentType.CUSTOM,
        "pathways": bracket_pathways,
        "vars": context["bracket"]["weak point"],
        "targets": [
            S("n_{\\text{bracket bearing}}"),
            S("n_{\\text{bracket bending}}"),
        ]
    }

    logs += analyze(bracket_sub_problem, is_full_problem=False)

    context["vars"][S("n_{\\text{bolt shear}}")] = context["bolts"][max_index][S("n_{\\text{bolt shear}}")]
    context["vars"][S("n_{\\text{bolt bearing}}")] = context["bolts"][max_index][S("n_{\\text{bolt bearing}}")]
    context["vars"][S("n_{\\text{bracket bearing}}")] = context["bracket"]["weak point"][S("n_{\\text{bracket bearing}}")]
    context["vars"][S("n_{\\text{bracket bending}}")] = context["bracket"]["weak point"][S("n_{\\text{bracket bending}}")]

    return logs
