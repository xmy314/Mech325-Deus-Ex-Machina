from mech325.infrastructure import *

input_context = {
    "component_type": ComponentType.HELICAL_GEAR,
    "vars": {

    },
    "targets": [
        S("SF_W"),
    ],
}

# list_vars(input_context)
logs = analyze(context=input_context)
compile_latex(logs)
