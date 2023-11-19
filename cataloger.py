from infrastructure import *
import sympy as sym

# run this program to start logging information.
# to exist, press control c.

try:
    from unit import descriptions
    from unit import units
    for s in QuestionType:
        if not s in descriptions:
            descriptions[s] = {}
        if not s in units:
            units[s] = {}
        context = {
            "question_type": s,
        }
        text_vars, symbolic_vars = list_vars(context)
        for var in symbolic_vars:
            if (var in descriptions[s]) and (var in units[s]):
                continue
            print(var)
            descriptions[s][var] = input("Description:")
            units[s][var] = input("Unit:")
except KeyboardInterrupt:
    with open("units_new_version.py", "w+") as fi:
        fi.write("from infrastructure import QuestionType\n")
        fi.write("from sympy import Symbol as S\n")

        fi.write("descriptions = {\n")
        for question_type in descriptions:
            fi.write("    "+str(question_type)+":{\n")
            for var in descriptions[question_type]:
                if isinstance(var, sym.Expr):
                    fi.write(f"        S('{str(var)}'): '{descriptions[question_type][var]}',\n")
                else:
                    fi.write(f"        '{str(var)}': '{descriptions[question_type][var]}',\n")
            fi.write("    },\n")
        fi.write("}\n")

        fi.write("units = {\n")
        for question_type in units:
            fi.write("    "+str(question_type)+": {\n")
            for var in units[question_type]:
                if isinstance(var, sym.Expr):
                    fi.write(f"        S('{str(var)}'): '{units[question_type][var]}',\n")
                else:
                    fi.write(f"        '{str(var)}': '{units[question_type][var]}',\n")
            fi.write("    },\n")
        fi.write("}\n")
