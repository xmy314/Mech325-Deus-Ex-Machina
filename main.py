from infrastructure import *


input_context = {
}

# list_vars(input_context)
logs = analyze(context=input_context)
compile_latex(logs)
