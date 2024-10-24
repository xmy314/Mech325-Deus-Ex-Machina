import sympy as sym
from sympy import Symbol as S
import math
import cv2
from os.path import join
from enum import Enum
from screeninfo import get_monitors

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
    FLAT_BELT = 1
    V_BELT = 2
    SYNCHRONOUS_BELT = 3
    CHAIN = 4
    WIRE_ROPE = 5
    SPUR_GEAR = 6
    HELICAL_GEAR = 7
    BEVEL_GEAR = 8
    WORM_GEAR = 9
    RACK_PINION = 10
    BOUNDARY_LUBRICATED_BEARING = 11
    BALL_AND_CYLINDRICAL_BEARING_RADIAL = 12
    BALL_AND_CYLINDRICAL_BEARING_ALL = 13
    TAPERED_ROLLER_BEARING = 14
    SHAFT_POINT = 15
    KEY = 16
    RETAINING_RING = 17
    POWER_SCREWS = 18
    BALL_SCREWS = 19
    SPRINGS = 20
    BOLTS = 21
    CUSTOM = 22


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

        subbed_latex = sym.latex(touch(expression.subs({symbol_in_eqn: S("xxxxxx"+sym.latex(symbol_in_eqn)+"xxxxxx") for symbol_in_eqn in symbols_in_eqn})), order=None)
        for symbol_in_eqn in symbols_in_eqn:
            subbed_latex = subbed_latex.replace(sym.latex(S("xxxxxx"+sym.latex(symbol_in_eqn)+"xxxxxx")), f"\\left({round_nsig(knowns[symbol_in_eqn],5):.5g}\\right)")
        subbed_latex = sym.latex(unknown) + " &= " + subbed_latex

        latex_entry = r"\begin{align*}"
        latex_entry += "\n    "+direct_latex
        if len(symbols_in_eqn) > 1:
            latex_entry += r"\\"+"\n    "+subbed_latex
            latex_entry += r"\\"+"\n    "+f"{unknown} &= {knowns[unknown]:.5g}"
        latex_entry += "\n"+r"\end{align*}"

        return [latex_entry]

    # if figure, prompt it.
    if pathway[0] == PathType.TABLE_OR_FIGURE:
        file_path = ["References"]+pathway[1].split(" ")
        file_path[-1] += ".png"
        print("")
        print(join(*file_path))

        img = cv2.imread(join(*file_path))
        monitor = get_monitors()[0]
        true_screen_size = (monitor.height,monitor.width)
        screen_ratio = 0.5*max(true_screen_size[0]/img.shape[0],true_screen_size[1]/img.shape[1])
        img = cv2.resize(img,(round(img.shape[1]*screen_ratio),round(img.shape[0]*screen_ratio)))

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

        substring = ', '.join([f'${sym.latex(symbol)} = {round_nsig(knowns[symbol],3):.3g} $' if isinstance(symbol, sym.Expr) else f'$\\text{{{symbol}}} = \\text{{{knowns[symbol]}}} $' for symbol in query_keys])
        return_string = f"Query {pathway[1]} with {substring}: "
        substring = "\n"+'\n'.join([f'$${sym.latex(symbol)} = {knowns[symbol]:g} $$' if isinstance(symbol, sym.Expr) else f'$$\\text{{{symbol}}} = {knowns[symbol]} $$' for symbol in new_knowledge])
        return_string += substring
        return [return_string]

    # if is a mock of a table, evaluate with the mock.
    if pathway[0] == PathType.MOCK_TABLE_OR_FIGURE:
        substring = ', '.join([
            f'${sym.latex(symbol)} = {knowns[symbol]:.5g} $'
            if isinstance(symbol, sym.Expr) else
            f'$\\text{{{symbol}}} = \\text{{{knowns[symbol]}}} $'
            for symbol in pathway[2][1]])

        return_string = f"Query {pathway[1]} with {substring}: "

        new_knowledge = [a for a in pathway[2][0] if not a in knowns]

        pathway[3](knowns)

        substring = "\n"+'\n'.join([
            f'$${sym.latex(symbol)} = {knowns[symbol]:.3g} $$'
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
    if context["component_type"] == ComponentType.FLAT_BELT:
        from mech325.components.flat_belt import retrieve_flatbelt_information
        pathways = retrieve_flatbelt_information()
    elif context["component_type"] == ComponentType.V_BELT:
        from mech325.components.v_belt import retrieve_vbelt_information
        pathways = retrieve_vbelt_information()
    elif context["component_type"] == ComponentType.SYNCHRONOUS_BELT:
        from mech325.components.sync_belt import retrieve_syncbelt_information
        pathways = retrieve_syncbelt_information()
    elif context["component_type"] == ComponentType.CHAIN:
        from mech325.components.chain import retrieve_chain_information
        pathways = retrieve_chain_information()
    elif context["component_type"] == ComponentType.SPUR_GEAR:
        from mech325.components.spur_gear import retrieve_spurgear_information
        pathways = retrieve_spurgear_information()
    elif context["component_type"] == ComponentType.HELICAL_GEAR:
        from mech325.components.helical_gear import retrieve_helicalgear_information
        pathways = retrieve_helicalgear_information()
    elif context["component_type"] == ComponentType.BEVEL_GEAR:
        from mech325.components.bevel_gear import retrieve_bevelgear_information
        pathways = retrieve_bevelgear_information()
    elif context["component_type"] == ComponentType.BOUNDARY_LUBRICATED_BEARING:
        from mech325.components.bushing import retrieve_bushing_information
        pathways = retrieve_bushing_information()
    elif context["component_type"] == ComponentType.BALL_AND_CYLINDRICAL_BEARING_RADIAL:
        from mech325.components.bcbearing_radial import retrieve_bcbearingradial_information
        pathways = retrieve_bcbearingradial_information()
    elif context["component_type"] == ComponentType.BALL_AND_CYLINDRICAL_BEARING_ALL:
        from mech325.components.bcbearing_all import retrieve_bcbearingall_information
        pathways = retrieve_bcbearingall_information()
    elif context["component_type"] == ComponentType.TAPERED_ROLLER_BEARING:
        from mech325.components.taper_bearing import retrieve_tbeaing_information
        pathways = retrieve_tbeaing_information()
    elif context["component_type"] == ComponentType.SHAFT_POINT:
        from mech325.components.shaft_point_mott import retrieve_shaft_point_information_mott
        pathways = retrieve_shaft_point_information_mott()
    elif context["component_type"] == ComponentType.KEY:
        from mech325.components.key import retrieve_key_information_mott
        pathways = retrieve_key_information_mott()
    elif context["component_type"] == ComponentType.POWER_SCREWS:
        from mech325.components.power_screw import retrieve_power_screw_information
        pathways = retrieve_power_screw_information()
    elif context["component_type"] == ComponentType.BALL_SCREWS:
        from mech325.components.ball_screw import retrieve_ballscrew_information
        pathways = retrieve_ballscrew_information()
    elif context["component_type"] == ComponentType.BOLTS:
        from mech325.components.single_bolt import retrieve_singlebolt_information
        pathways = retrieve_singlebolt_information()
    elif context["component_type"] == ComponentType.SPRINGS:
        from mech325.components.spring import retrieve_spring_information
        pathways = retrieve_spring_information(context["vars"])
    elif context["component_type"] == ComponentType.CUSTOM:
        pathways = context["pathways"]
    else:
        raise NotImplementedError("not implemented")

    return pathways


def list_vars(context,print_out=True):

    vars = []
    if context["component_type"] == ComponentType.CUSTOM:
        print("no general data aviliable for custom component/question type, please check the implementation for more detail.")
        return {}, {}

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

    text_vars.sort()
    symbolic_vars.sort(key=lambda x: sym.latex(x))

    if print_out:
        print("The following are text type variables")
        for var in text_vars:
            print("-", var)

        print("The following are value type variables")
        for var in symbolic_vars:
            print("-", var)

    return text_vars, symbolic_vars


def analyze(context, is_full_problem=True):

    pathways = query_pathways(context)

    # this keeps track of how each of the variables is found. (found variable) : (pathway used to derive it)
    source = {}

    mock_knowns = set(context["vars"].keys())

    # traverse a directed acyclic graph
    while True:
        new_information_acquired = False

        # for each equation, check if there is a equation where only 1 value is missing.
        # for each figure, check if there is a figure where only 1 value is missing.
        # this solution complete ignores the case of coupled equations but those have all been refactored as custom functions.

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
                        new_information_acquired = True
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
                    new_information_acquired = True
                    mock_knowns.add(unknown_symbol)
                    source[unknown_symbol] = i

                # check completion
        
        if not new_information_acquired:
            print("Not enough information are provided. Please check the pdf output for what might be missing.")

            t_var,s_var = list_vars(context)

            logs = [
                "Not enough information are provided. Please reference against the followings lists.",
                "Here is a list of the knowns:",
                ", ".join([f"${str(v)}$" if isinstance(v, sym.Expr) else v for v in t_var if v in mock_knowns]),
                "Here is a list of the knowns:",
                ", ".join([f"${str(v)}$" if isinstance(v, sym.Expr) else v for v in s_var if v in mock_knowns]),
                "Here is a list of the unknown text types:",
                ", ".join([f"${str(v)}$" if isinstance(v, sym.Expr) else v for v in t_var if not v in mock_knowns]),
                "Here is a list of the unknown value types:",
                ", ".join([f"${str(v)}$" if isinstance(v, sym.Expr) else v for v in s_var if not v in mock_knowns]),
            ]

            return logs

        all_target_solved = True
        for target in context["targets"]:
            if not target in mock_knowns:
                all_target_solved = False
                break
        
        if all_target_solved:
            break
        else:
            continue
        

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
                summary_lines += f"\n    ${sym.latex(target)}$ & : & {knowns[target]:.5g}"+r"\\"
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
