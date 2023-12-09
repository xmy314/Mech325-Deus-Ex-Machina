from mech325.infrastructure import *


def retrieve_power_screw_information():
    print("Retrieving information for solving power screw questions from Shigley.")
    print("Please note that the following code is not tested.")

    pathways = [
        (PathType.EQUATION, "Shigley Equation 8-1", Geqn(S("T_R"), S("F")*S("d_m")*(sym.pi*S("f")*S("d_m")+S("l"))/(sym.pi*S("d_m")-S("f")*S("l"))/2)),
        (PathType.EQUATION, "Shigley Equation 8-2", Geqn(S("T_L"), S("F")*S("d_m")*(sym.pi*S("f")*S("d_m")-S("l"))/(sym.pi*S("d_m")+S("f")*S("l"))/2)),
        (PathType.EQUATION, "Shigley Equation 8-4", Geqn(S("e"), S("F")*S("l")/(2*sym.pi*S("T_R")))),
        (PathType.EQUATION, "Shigley Equation 8-6", Geqn(S("T_c"), S("F")*S("f_c")*S("d_c")/2)),
        (PathType.EQUATION, "Shigley Equation 8-7", Geqn(S("\\tau"), 16*S("T")/(sym.pi*S("d_r")**3))),
        (PathType.EQUATION, "Shigley Equation 8-7", Geqn(S("\\sigma"), -4*S("F")/(sym.pi*S("d_r")**2))),
    ]

    return pathways
