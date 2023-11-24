from infrastructure import *

input_context = {
    "component_type": ComponentType.HELICAL_GEAR,
    "vars": {

    },
    "targets": [
        S("SF_W"),
    ],
}

analyze(context=input_context)
