from infrastructure import *

input_context = {
    "question_type": QuestionType.V_BELT,
    "vars": {
        # text description []
        "driver": "Six cylinder engine",
        "driven": "Heavy Converyers",
        "duty time": "16 hours/day",

        S("n_{in}"): 1550,              # inpur angular speed [rpm]
        S("n_{out\\,rough}"): 550,      # nominal output angular speed [rpm]
        S("H_{nom}"): 40,                # nominal power [hp]

        S("V_{rough}"): 4000,
    },
    "targets": [                                    # in reverse direction as logical direction.
        "belt type",
        S("D_{in}"),
        S("D_{out}"),
        S("VR"),
        S("CD"),
        S("N_{belt}"),
    ],
}


analyze(context=input_context)
