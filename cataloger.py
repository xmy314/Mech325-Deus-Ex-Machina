from infrastructure import *
import sympy as sym

# run this program to start logging information.
# to exist, press control c.

try:
    from unit import descriptions
    from unit import units
    for s in ComponentType:
        if not s in descriptions:
            descriptions[s] = {}
        if not s in units:
            units[s] = {}
        context = {"component_type": s}
        try:
            text_vars, symbolic_vars = list_vars(context)
        except NotImplementedError:
            continue

        # Remove Renamed Symbols
        tbr = []
        for var in descriptions[s]:
            if not var in text_vars and not var in symbolic_vars:
                tbr.append(var)
        for var in tbr:
            descriptions[s].pop(var)
        tbr = []
        for var in units[s]:
            if not var in text_vars and not var in symbolic_vars:
                tbr.append(var)
        for var in tbr:
            units[s].pop(var)

        # Ask about information
        for var in text_vars:
            if (var in descriptions[s]):
                continue
            print(var)
            descriptions[s][var] = input("Description:")

        for var in symbolic_vars:
            if (var in descriptions[s]) and (var in units[s]):
                continue
            print(var)
            descriptions[s][var] = input("Description:")
            units[s][var] = input("Unit:")

except KeyboardInterrupt:
    pass

print("Recording")

with open("units_new_version.py", "w+") as fi:
    fi.write("from infrastructure import ComponentType\n")
    fi.write("from sympy import Symbol as S\n")

    fi.write("descriptions = {\n")
    for component_type in descriptions:
        fi.write("    "+str(component_type)+":{\n")
        for var in descriptions[component_type]:
            if isinstance(var, sym.Expr):
                fi.write(f"        S(r\"{str(var)}\"): \"{descriptions[component_type][var]}\",\n")
            else:
                fi.write(f"        r\"{str(var)}\": \"{descriptions[component_type][var]}\",\n")
        fi.write("    },\n")
    fi.write("}\n")

    fi.write("units = {\n")
    for component_type in units:
        fi.write("    "+str(component_type)+": {\n")
        for var in units[component_type]:
            if isinstance(var, sym.Expr):
                fi.write(f"        S(r\"{str(var)}\"): \"{units[component_type][var]}\",\n")
            else:
                fi.write(f"        r\"{str(var)}\": \"{units[component_type][var]}\",\n")
        fi.write("    },\n")
    fi.write("}\n")

print("Recorded")
