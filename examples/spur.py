from mech325.infrastructure import *

input_context = {
    "component_type": ComponentType.SPUR_GEAR,
    "vars": {
        S("\\phi"):  math.radians(20),

        # # if gear size can be choosed, use the following section
        # S("N_{in\,min}"): 17,
        # S("N_{in\,max}"): 20,
        # S("VR_{rough}"): 3,

        # if gear size is set, use the following section. but dont have both.
        S("N_{in}"): 16,
        S("N_{out}"): 48,

        # gear face width, diametrical pitch, and agma 2015 quality
        S("F"): 2,
        S("P_d"): 6,
        S("A_v"): 9,

        # input setting
        "gear type": "External",
        "driven": "milling machine",
        "driver": "electric motor",
        S("n_{in}"): 300,
        S("H_{nom}"): 5,

        # performace and reliability setting
        "Reliability": 0.9,             # reliability, typically 0.9 []

        # life time setting, choose one of the following lines.
        S("L"): 5000,                    # number of working hours [hour]
        # S("N_{c\\,in}"): 10**8,         # number of load cycles on pinion []
        # S("N_{c\\,out}"): 10**8,        # number of load cycles on gear []

        # straddle mounted and how much off from center
        S("S_1"): 0,         # distance from center of gear to center of support
        S("S"): 2,           # distance between the supports

        # Exposure or Enclosure Condition
        "exposure condition": "Commercial enclosed gear units",

        # default conditions: no rim effect, alternatively comment the following line
        S("K_B"): 1,
    },
    "targets": [
        S("SF_W"),
    ],
}

# 2021 mt 2

input_context = {
    "component_type": ComponentType.SPUR_GEAR,
    "vars": {

        # # if gear size can be choosed, use the following section
        # S("N_{in\,min}"): 17,
        # S("N_{in\,max}"): 20,
        # S("VR_{rough}"): 3,

        # if gear size is set, use the following section. but dont have both.
        S("N_{in}"): 16,
        S("N_{out}"): 51,

        # gear face width, diametrical pitch, and agma 2015 quality
        S("P_d"): 12,
        S("\\phi"):  math.radians(20),
        S("A_v"): 7,
        S("F"): 1,

        # input setting
        "driver": "electric motor",
        "driven": "agitator",
        "gear type": "External",
        S("n_{in}"): 1750,
        S("H_{nom}"): 5,

        # performace and reliability setting
        "Reliability": 0.9,             # reliability, typically 0.9 []

        # life time setting, choose one of the following lines.
        "duty time": 4,
        # S("L"): 5000,                    # number of working hours [hour]
        S("N_{c\\,in}"): 10**7,         # number of load cycles on pinion []
        # S("N_{c\\,out}"): 10**8,        # number of load cycles on gear []

        # straddle mounted and how much off from center
        S("S_1"): 0,         # distance from center of gear to center of support
        S("S"): 2,           # distance between the supports

        # Exposure or Enclosure Condition
        "exposure condition": "Commercial enclosed gear units",

        # default conditions: no rim effect, alternatively comment the following line
        S("K_B"): 1,
        S("K_s"): 1,
        S("K_o"): 1.25,
        S("K_R"): 1,
    },
    "targets": [
        # S("VR"),
        # S("D_{in}"),
        # S("D_{out}"),
        # S("V"),
        # S("W_t"),
        # S("W_r"),

        S("C_p"),
        S("K_v"),
        S("K_m"),
        S("I"),

        S("s_{c\\,in}"),

        "SAE",

        S("SF_c"),
        # S("SF_W"),
    ],
}


analyze(context=input_context)
