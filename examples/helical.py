from infrastructure import *

input_context = {
    "question_type": QuestionType.HELICAL_GEAR,
    "vars": {

    },
    "targets": [
        S("SF_W"),
    ],
}

analyze(context=input_context)
