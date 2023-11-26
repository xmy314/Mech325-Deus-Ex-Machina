import sympy as sym
from sympy import Symbol as S
from enum import Enum
from math import radians, copysign
from sympy import sin, cos, tan, sqrt
from os.path import join
from infrastructure import round_nsig, ComponentType, analyze

# This file is for force balancing on a shaft.
# Input forces in terms of z along shaft and use components x y or in terms of standard angle in x y plane.
# make the smallest z coordinate 0.

# This is built specifically for mech 325 so it only support point force and and point moment.


class LoadType(Enum):
    FORCE = 0
    MOMENT = 1


def convert_component_to_load(context):

    logs = []

    components = context["components"]
    rotation_direction = context["vars"]["rotation direction"]  # 1 for positive x, -1 for negative x
    n = context["vars"][S("n")]
    loads = []
    for component in components:
        driving = component["is driver"]
        radius = component["diameter"]/2
        torque = 63025*component["power"]/n
        nominal_force = 0 if torque == 0 else torque/radius
        rf_pair = []
        if component["component_type"] == ComponentType.FLAT_BELT:
            K = 3
            # tight side
            rf_pair.append((
                (0, rotation_direction*driving*radius, component["z"]),
                ((K/(K-1))*nominal_force, 0, 0)
            ))
            # loose side
            rf_pair.append((
                (0, -rotation_direction*driving*radius, component["z"]),
                ((1/(K-1))*nominal_force, 0, 0)
            ))
        elif component["component_type"] == ComponentType.V_BELT:
            K = 5
            # tight side
            rf_pair.append((
                (0, rotation_direction*driving*radius, component["z"]),
                ((K/(K-1))*nominal_force, 0, 0)
            ))
            # loose side
            rf_pair.append((
                (0, -rotation_direction*driving*radius, component["z"]),
                ((1/(K-1))*nominal_force, 0, 0)
            ))
        elif component["component_type"] == ComponentType.CHAIN:
            # tight side
            rf_pair.append((
                (0, rotation_direction*driving*radius, component["z"]),
                (nominal_force, 0, 0)
            ))
        elif component["component_type"] == ComponentType.SPUR_GEAR:
            Fx = -nominal_force*tan(component["pressure angle"])
            Fy = -driving*rotation_direction*nominal_force
            rf_pair.append((
                (radius, 0, component["z"]),
                (Fx, Fy, 0)
            ))
        elif component["component_type"] == ComponentType.HELICAL_GEAR:
            right_handed = component["is right hand"]

            Fx = -nominal_force*tan(component["normal pressure angle"])/cos(component["helix angle"])
            Fy = -driving*rotation_direction*nominal_force
            Fz = rotation_direction*driving*right_handed*nominal_force*tan(component["helix angle"])

            rf_pair.append((
                (radius, 0, component["z"]),
                (Fx, Fy, Fz)
            ))
        elif component["component_type"] == ComponentType.BEVEL_GEAR:
            positive_cone = component["is cone right"]

            Fx = -nominal_force*tan(component["pressure angle"])*cos(component["cone angle"])
            Fy = -driving*rotation_direction*nominal_force
            Fz = -positive_cone*nominal_force*tan(component["pressure angle"])*sin(component["cone angle"])

            rf_pair.append((
                (radius, 0, component["z"]),
                (Fx, Fy, Fz)
            ))
            raise NotImplementedError("Check component_type.")
        elif component["component_type"] == ComponentType.WORM_GEAR:
            right_handed = component["is right hand"]

            Fx = -nominal_force*tan(component["normal pressure angle"])/sin(component["lead angle"])
            Fy = -driving*rotation_direction*nominal_force
            Fz = rotation_direction*driving*right_handed*nominal_force*sin(component["lead angle"])

            rf_pair.append((
                (radius, 0, component["z"]),
                (Fx, Fy, Fz)
            ))
            raise NotImplementedError("Check component_type.")
        elif component["component_type"] == ComponentType.BALL_AND_CYLINDRICAL_BEARING_RADIAL:
            loads.append((
                LoadType.FORCE,
                component["name"],
                [0, 0, component["z"]],
                [S("R_{"+component["name"]+"x}"), S("R_{"+component["name"]+"y}"), 0]
            ))
        elif component["component_type"] == ComponentType.BALL_AND_CYLINDRICAL_BEARING_ALL:
            loads.append((
                LoadType.FORCE,
                component["name"],
                [0, 0, component["z"]],
                [S("R_{"+component["name"]+"x}"), S("R_{"+component["name"]+"y}"), S("R_{"+component["name"]+"z}")]
            ))
        else:
            raise NotImplementedError("Check component_type.")

        theta = component["theta"]
        for r, f in rf_pair:
            rx = cos(theta)*r[0]-sin(theta)*r[1]
            ry = sin(theta)*r[0]+cos(theta)*r[1]
            rz = r[2]
            fx = cos(theta)*f[0]-sin(theta)*f[1]
            fy = sin(theta)*f[0]+cos(theta)*f[1]
            fz = f[2]
            loads.append((
                LoadType.FORCE,
                component["name"],
                [rx, ry, rz],
                [fx, fy, fz],
            ))

    if not "loads" in context:
        context["loads"] = []
    context["loads"] += loads
    return "\n".join(logs)


def solve_reaction_force(context):
    """given a bunch of force and moment loads, solve."""

    loads = context["loads"]

    Fx, Fy, Fz, Mx, My, Mz = 0, 0, 0, 0, 0, 0
    for load in loads:
        if load[0] == LoadType.MOMENT:
            torque = load[3]
            Mx += torque[0]
            My += torque[1]
            Mz += torque[2]
        else:
            rx, ry, rz = load[2]
            fx, fy, fz = load[3]
            Fx += fx
            Fy += fy
            Fz += fz
            Mx += ry*fz-rz*fy
            My += rz*fx-rx*fz
            Mz += rx*fy-ry*fx

    all_vars = []
    exprs = [Fx, Fy, Fz, Mx, My, Mz]
    for expr in exprs:
        if isinstance(expr, sym.Expr):
            all_vars += expr.free_symbols

    if not "vars" in context:
        context["vars"] = {}

    targets = [v for v in all_vars if not v in context["vars"]]

    result = sym.solve(exprs, targets, dict=True)
    context["vars"].update(result[0])
    for load in loads:
        for i in range(3):
            if not isinstance(load[3][i], sym.Expr):
                continue
            expr = load[3][i]
            sub_dict = {}
            for symbol in expr.free_symbols:
                sub_dict[symbol] = context["vars"][symbol]
            load[3][i] = expr.evalf(subs=sub_dict)

    log = r"\begin{align*}"+"\n"
    for load in context["loads"]:
        load_name = f"F_{load[1]}" if load[0] == LoadType.FORCE else f"M_{load[1]}"
        log += f"{load_name} & = {load[3][0]:7.2f}\\hat{{i}}+{load[3][1]:7.2f}\\hat{{j}}+{load[3][2]:7.2f}\\hat{{k}}"+r"\\"+"\n"
        log += f"          & = {sqrt(load[3][0]**2+load[3][1]**2):7.2f}\\hat{{r}}+{load[3][2]:7.2f}\\hat{{k}}"+r"\\"+"\n"
    log += r"\end{align*}"+"\n"
    return log


def fbd3d(context):
    """return the latex code that draws out the forces in 3d."""
    loads = context["loads"]
    loads.sort(key=lambda x: x[2][2])
    forces = []
    moments = []
    for load in loads:
        if load[0] == LoadType.MOMENT:
            moments.append(load)
        else:
            forces.append(load)

    normalized_unit_radial_length = sum([sqrt((x[2][0]**2)+(x[2][1]**2)) for x in loads])/len(loads)
    normalized_unit_axial_length = (max([x[2][2] for x in loads])-min([x[2][2] for x in loads]))/10
    normalized_unit_force = sum([sqrt(x[3][0]**2+x[3][1]**2+x[3][2]**2) for x in forces])/len(forces)

    if (normalized_unit_radial_length == 0):
        normalized_unit_radial_length = 1

    ret3d = r"""
\tdplotsetmaincoords{70}{110}
\tdplotsetrotatedcoords{90}{90}{90}
\tikz[
    tdplot_rotated_coords,
    axis/.style={thin,gray},
    forces/.style={thick,blue},
    cforces/.style={thin,blue},
    marking/.style={densely dashed,thin,gray,font=\tiny},
]{
    \draw[axis,-latex](0,0,-2)--(1,0,-2)node[above right]{$x$};
    \draw[axis,-latex](0,0,-2)--(0,1,-2)node[above left]{$y$};
    \draw[axis,-latex](0,0,-2)--(0,0,-1)node[above]{$z$};
    
    \draw[thick](0,0,0)--(0,0,10);
"""

    for i in range(len(loads)-1):
        npz0 = loads[i][2][2]/normalized_unit_axial_length
        npz1 = loads[i+1][2][2]/normalized_unit_axial_length
        if npz1-npz0 == 0:
            continue
        ret3d += f"    \draw(0,-0.1,{npz0})--(0,-1.7,{npz0});\n"
        ret3d += f"    \draw(0,-0.1,{npz1})--(0,-1.7,{npz1});\n"
        ret3d += f"    \draw[latex-latex](0,-1.5,{npz0})--(0,-1.5,{npz1}) node[pos=0.5,below] {{{round_nsig(loads[i+1][2][2]-loads[i][2][2],5)}}};\n\n"

    for i in range(len(loads)):
        npz0 = loads[i][2][2]/normalized_unit_axial_length
        ret3d += r"    \node[below right] at "+f"(0,0,{npz0}){{${loads[i][1]}$}};\n"

    for force in forces:
        nf = [x/normalized_unit_force for x in force[3]]
        np = [
            force[2][0]/normalized_unit_radial_length,
            force[2][1]/normalized_unit_radial_length,
            force[2][2]/normalized_unit_axial_length,
        ]

        # the indicator lines
        if abs(np[1]) >= 0.000001:
            ret3d += f"    \draw[marking]({np[0]},{np[1]},{np[2]})--({np[0]},0,{np[2]}) "
            if np[0] > 0:
                ret3d += f"node[pos=.5 ,below, sloped]"
            else:
                ret3d += f"node[pos=.5 ,above, sloped]"
            ret3d += f"{{{round_nsig(force[2][1],5):5.2f}}};\n"
        if abs(np[0]) >= 0.000001:
            ret3d += f"    \draw[marking]({np[0]},0,{np[2]})--(0,0,{np[2]}) "
            if np[1] > 0:
                ret3d += f"node[pos=.5 ,below, sloped]"
            else:
                ret3d += f"node[pos=.5 ,above, sloped]"
            ret3d += f"{{{round_nsig(force[2][0],5):5.2f}}};\n"

        # the components.
        if (nf[0] != 0):
            ret3d += f"    \draw[forces,-latex]({-(nf[0]+copysign(0.5,nf[0]))+np[0]},{np[1]},{np[2]})--({np[0]},{np[1]},{np[2]}) ;\n"
        if (nf[1] != 0):
            ret3d += f"    \draw[forces,-latex]({np[0]},{-(nf[1]+copysign(0.5,nf[1]))+np[1]},{np[2]})--({np[0]},{np[1]},{np[2]}) ;\n"
        if (nf[2] != 0):
            ret3d += f"    \draw[forces,-latex]({np[0]},{np[1]},{-(nf[2]+copysign(0.5,nf[2]))+np[2]})--({np[0]},{np[1]},{np[2]}) ;\n"

        ret3d += "\n"

    for moment in moments:
        np = [
            moment[2][0]/normalized_unit_radial_length,
            moment[2][1]/normalized_unit_radial_length,
            moment[2][2]/normalized_unit_axial_length,
        ]
        if moment[3][0] != 0 or moment[3][1] != 0:
            raise NotImplementedError("Didn't Implement Drawing Moment in arbitrary Direction.")

        ret3d += r"    \coordinate (MomentOrigin) at ("+f"{np[0]},{np[1]},{np[2]}"+");\n"
        ret3d += r"    \tdplotsetrotatedcoordsorigin{(MomentOrigin)}"+"\n"
        ret3d += r"    \tdplotsetrotatedcoords{90}{-90}{-90}"+"\n"
        if moment[3][2] <= 0:
            ret3d += r"    \tdplotdrawarc[tdplot_rotated_coords,-latex]{(0,0,0)}{0.5}{0}{180}{anchor = east}{};"+"\n"
        else:
            ret3d += r"    \tdplotdrawarc[tdplot_rotated_coords,-latex]{(0,0,0)}{0.5}{180}{0}{anchor = east}{};"+"\n"
        ret3d += r"    \tdplotresetrotatedcoordsorigin"+"\n\n"

    ret3d += "}\n\n"

    return ret3d


def shaft_analysis(context):
    """return the latex code that draws out the internal shear, moment, compression, torsion of the shaft."""

    loads = context["loads"]
    loads.sort(key=lambda x: x[2][2])
    key_points = [[0, [0, 0, 0], [0, 0, 0]]]
    for load in loads:
        if load[0] == LoadType.MOMENT:
            rx, ry, rz = load[2]
            mx, my, mz = load[3]
            if rz == key_points[-1][0]:
                key_points[-1][2][0] += mx
                key_points[-1][2][1] += my
                key_points[-1][2][2] += mz
            else:
                key_points.append([rz, [0, 0, 0], [mx, my, mz]])
        else:
            rx, ry, rz = load[2]
            fx, fy, fz = load[3]
            if rz == key_points[-1][0]:
                key_points[-1][1][0] += fx
                key_points[-1][1][1] += fy
                key_points[-1][1][2] += fz
                key_points[-1][2][0] += ry*fz
                key_points[-1][2][1] += -rx*fz
                key_points[-1][2][2] += rx*fy-ry*fx
            else:
                key_points.append([rz, [fx, fy, fz], [ry*fz, -rx*fz, rx*fy-ry*fx]])

    normalized_unit_axial_length = (key_points[-1][0])/10

    # draw 8 plots

    # begin 2d plot
    ret2d = [r"""\begin{tikzpicture}[
    axis/.style={thin,gray},
    forces/.style={thick,blue},
    marking/.style={densely dashed,thin,gray},
    plot/.style={thick,blue}]
\draw[help lines] (-2,-2) grid (10,2);
\draw[thick](0,0)--(10,0);
\draw[axis,-latex](-2,0)--(-1,0)node[above left]{$z$};
"""+v+"\n" for v in [
        r"""    \draw[axis,-latex](-2,0)--(-2,1)node[above right]{$V_{xz}$};""",
        r"""    \draw[axis,-latex](-2,0)--(-2,1)node[above right]{$M_{xz}$};""",
        r"""    \draw[axis,-latex](-2,0)--(-2,1)node[above right]{$V_{yz}$};""",
        r"""    \draw[axis,-latex](-2,0)--(-2,1)node[above right]{$M_{yz}$};""",
        r"""    \draw[axis,-latex](-2,0)--(-2,1)node[above right]{$T$};""",
        r"""    \draw[axis,-latex](-2,0)--(-2,1)node[above right]{Axial Compression};""",
        r"""    \draw[axis,-latex](-2,0)--(-2,1)node[above right]{$|V|$};""",
        r"""    \draw[axis,-latex](-2,0)--(-2,1)node[above right]{$|M|$};""",
    ]
    ]

    maximum_value = [0.0001 for i in range(8)]

    # fx fy are shear, fz is compression, mx, my are moments, mz is torsion.
    beam_segments = [(0, (0, 0, 0, 0, 0, 0, 0, 0), (0, 0, 0, 0, 0, 0, 0, 0))]  # z, v(z-), v(z).

    for key_point in key_points:

        rfx_expr = beam_segments[-1][2][0]+sym.integrate(0, S("z")).subs({S("z"): S("z")-beam_segments[-1][0]})   # 0 for not supporting distributed load
        rfy_expr = beam_segments[-1][2][1]+sym.integrate(0, S("z")).subs({S("z"): S("z")-beam_segments[-1][0]})   # 0 for not supporting distributed load
        rfz_expr = beam_segments[-1][2][2]+sym.integrate(0, S("z")).subs({S("z"): S("z")-beam_segments[-1][0]})   # 0 for not supporting distributed load
        rmx_expr = beam_segments[-1][2][3]+sym.integrate(rfx_expr, S("z")).subs({S("z"): S("z")-beam_segments[-1][0]})
        rmy_expr = beam_segments[-1][2][4]+sym.integrate(rfy_expr, S("z")).subs({S("z"): S("z")-beam_segments[-1][0]})
        rmz_expr = beam_segments[-1][2][5]+sym.integrate(0, S("z")).subs({S("z"): S("z")-beam_segments[-1][0]})   # 0 for not supporting distributed load
        rfxy_expr = sym.sqrt(rfx_expr**2+rfy_expr**2)
        rmxy_expr = sym.sqrt(rmx_expr**2+rmy_expr**2)

        rfx_accu = rfx_expr.evalf(subs={S("z"): key_point[0]}) + key_point[1][0]
        rfy_accu = rfy_expr.evalf(subs={S("z"): key_point[0]}) + key_point[1][1]
        rfz_accu = rfz_expr.evalf(subs={S("z"): key_point[0]}) + key_point[1][2]
        rmx_accu = rmx_expr.evalf(subs={S("z"): key_point[0]}) - key_point[2][1]  # rmx means moment in xz plane which is y in vector notation which is why the y moment load is added. The negative sign is a quirk as xz is negative y.
        rmy_accu = rmy_expr.evalf(subs={S("z"): key_point[0]}) + key_point[2][0]  # rmy means moment in yz plane which is x in vector notation which is why the x moment load is added.
        rmz_accu = rmz_expr.evalf(subs={S("z"): key_point[0]}) + key_point[2][2]
        rfxy_accu = sym.sqrt(rfx_accu**2+rfy_accu**2)
        rmxy_accu = sym.sqrt(rmx_accu**2+rmy_accu**2)

        beam_segments.append((
            key_point[0],
            (rfx_expr, rfy_expr, rfz_expr, rmx_expr, rmy_expr, rmz_expr, rfxy_expr, rmxy_expr),
            (rfx_accu, rfy_accu, rfz_accu, rmx_accu, rmy_accu, rmz_accu, rfxy_accu, rfxy_expr),
        ))

        maximum_value = [
            max(maximum_value[0], abs(rfx_expr.evalf(subs={S("z"): key_point[0]})), abs(rfx_accu)),
            max(maximum_value[1], abs(rfy_expr.evalf(subs={S("z"): key_point[0]})), abs(rfy_accu)),
            max(maximum_value[2], abs(rfz_expr.evalf(subs={S("z"): key_point[0]})), abs(rfz_accu)),
            max(maximum_value[3], abs(rmx_expr.evalf(subs={S("z"): key_point[0]})), abs(rmx_accu)),
            max(maximum_value[4], abs(rmy_expr.evalf(subs={S("z"): key_point[0]})), abs(rmy_accu)),
            max(maximum_value[5], abs(rmz_expr.evalf(subs={S("z"): key_point[0]})), abs(rmz_accu)),
            max(maximum_value[6], abs(rfxy_expr.evalf(subs={S("z"): key_point[0]})), abs(rfxy_accu)),
            max(maximum_value[7], abs(rmxy_expr.evalf(subs={S("z"): key_point[0]})), abs(rfxy_expr)),
        ]

    normalized_unit = [v/1.8 for v in maximum_value]

    graph_order = [0, 2, 5, 1, 3, 4, 6, 7]  # look up from variable index to graph index

    for i in range(8):
        last_tag = 0
        graph_i = graph_order[i]
        ret2d[graph_i] += r"\draw[plot](0,0)"
        for j in range(len(beam_segments)-1):
            this_point = beam_segments[j]
            next_point = beam_segments[j+1]
            for k in range(21):
                z = (next_point[0]-this_point[0])*(k)/20+this_point[0]
                v = next_point[1][i].evalf(subs={S("z"): z})
                if (k == 0 or k == 20) and abs(v-last_tag) >= 0.01*normalized_unit[i] and abs(v) >= 0.01*normalized_unit[i]:
                    ret2d[graph_i] += f"--({z/normalized_unit_axial_length},{v/normalized_unit[i]}) node[above right] {{{round_nsig(v,5):5.0f}}} "
                    last_tag = v
                else:
                    ret2d[graph_i] += f"--({z/normalized_unit_axial_length},{v/normalized_unit[i]}) "

        ret2d[graph_i] += f"--(10,{beam_segments[-1][2][i]/normalized_unit[i]});\n"

    for i in range(8):
        graph_i = graph_order[i]
        for i in range(len(loads)):
            npz0 = loads[i][2][2]/normalized_unit_axial_length
            ret2d[graph_i] += r"    \node[below] at "+f"({npz0},0){{${loads[i][1]}$}};\n"
        ret2d[graph_i] += r"\end{tikzpicture}"+"\n"

    ret2d = "\n".join(ret2d)

    context["internal"] = beam_segments

    return ret2d


# Unit for length, force, and moment are not important as long as
# unit length cross unit force = unit moment.
context = {
    "components": [
        {
            "component_type": ComponentType.V_BELT,
            "name": "A",
            "z": 0,  # [inch]
            "theta": radians(-90),
            "is driver": 1,
            "power": 10,  # [hp]
            "diameter": 12,
            "left feature": "ring",
            "right feature": "ring",
        },
        {
            "component_type": ComponentType.BALL_AND_CYLINDRICAL_BEARING_RADIAL,
            "name": "B",
            "z": 6,
            "theta": 0,
            "is driver": 0,
            "power": 0,
            "diameter": 0,
            "left feature": "ring",
            "right feature": "sharp fillet",
        },
        {
            "component_type": ComponentType.BALL_AND_CYLINDRICAL_BEARING_RADIAL,
            "name": "C",
            "z": 36,
            "theta": 0,
            "is driver": 0,
            "power": 0,
            "diameter": 0,
            "left feature": "shoulder",
            "right feature": "sharp fillet",
        },
        {
            "component_type": ComponentType.SPUR_GEAR,
            "name": "D",
            "z": 42,
            "theta": radians(210),
            "is driver": -1,
            # "power": sym.Integer(15),  # This is passed to avoid over constraining and floating point error.
            "power": S("P_g"),
            "diameter": 8,
            "pressure angle": radians(20),
            "left feature": "ring",
            "right feature": "ring",
        },
        {
            "component_type": ComponentType.CHAIN,
            "name": "E",
            "z": 52,
            "theta": radians(30),
            "is driver": 1,
            "power": sym.Integer(5),
            "diameter": 6,
            "left feature": "ring",
            "right feature": "ring",
        },
    ],
    "vars": {
        S("n"): 240,  # [RPM]
        "rotation direction": -1,
    },
}

logs = []
logs.append(convert_component_to_load(context))
logs.append(solve_reaction_force(context))
logs.append(fbd3d(context))
logs.append(shaft_analysis(context))

with open(join("latex_output", "solution.tex"), "w+") as fi:
    fi.write("\n\n".join(logs))
