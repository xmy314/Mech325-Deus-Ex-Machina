from infrastructure import *

# home work question
input_context = {
    "question_type": QuestionType.CHAIN,
    "vars": {
        # text description []
        "driven": "Centrifugal Pump",
        "driver": "Steam Turbine",

        S("n_{in}"): 2200,              # inpur angular speed [rpm]
        S("n_{out\\,rough}"): 775,      # nominal output angular speed [rpm]
        S("CD_{C\\,rough}"): 40,        # inpur angular speed [number of pitches] value between [30,50]
        S("H_{nom}"): 20,               # nominal power [hp]
    },
    "targets": [
        # in order that solution comes, else the order of solution is weird.
        "chain number",                 # chain number eg 40/60/80
        S("N_{in}"),                    # input sprocket teeth
        S("PD_{in}"),                   # input sprocket pitch diameter
        S("N_{out}"),                   # input sprocket teeth
        S("PD_{out}"),                  # input sprocket pitch diameter
        S("L_{C}"),                     # length of chain in pitches
        "lubrication type",             # A or B or C
        S("CD"),                        # center line distance [inches]
    ],
}

# 2021 test 1
input_context = {
    "question_type": QuestionType.CHAIN,
    "vars": {
        # text description []
        "driver": "Electric Motor",
        "driven": "Reciprocating Pump",
        "duty time": 6,

        S("n_{in}"): 700,              # inpur angular speed [rpm]
        S("n_{out\\,rough}"): 300,      # nominal output angular speed [rpm]
        # S("CD_{C\\,rough}"): 40,        # input angular speed [number of pitches] value between [30,50]
        S("CD_{rough}"): 30,        # input angular speed [number of pitches] value between [30,50]
        S("H_{nom}"): 5,               # nominal power [hp]
    },
    "targets": [
        # in order that solution comes, else the order of solution is weird.
        S("K_s"),                 # chain number eg 40/60/80
        "chain number",                 # chain number eg 40/60/80
        S("N_{in}"),                    # input sprocket teeth
        # S("PD_{in}"),                   # input sprocket pitch diameter
        # S("N_{out}"),                   # input sprocket teeth
        # S("PD_{out}"),                  # input sprocket pitch diameter
        S("VR"),
        S("L_{C}"),                     # length of chain in pitches
        "lubrication type",             # A or B or C
        S("n_{sf}"),                        # center line distance [inches]
    ],
}

analyze(context=input_context)
