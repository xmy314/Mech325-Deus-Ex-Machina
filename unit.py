from infrastructure import ComponentType
from sympy import Symbol as S
descriptions = {
    ComponentType.TAPERED_ROLLER_BEARING: {
        S(r"Bore A"): "Bore Diameter of bearing A",
        S(r"Bore B"): "Bore Diameter of bearing B",
        S(r"C_{10\,A}"): "Rated Load for Bearing A.",
        S(r"C_{10\,B}"): "Rated Load for Bearing B.",
        S(r"F_{ae}"): "Equivalent Axial Load.",
        S(r"F_{eA}"): "Equivalent Radial Load at Bearing A.",
        S(r"F_{eB}"): "Equivalent Radial Load at Bearing B.",
        S(r"F_{rA}"): "Radial Load at Bearing A.",
        S(r"F_{rB}"): "Radial Load at Bearing B.",
        S(r"K_A"): "Geometry Factor for Bearing A.",
        S(r"K_B"): "Geometry Factor for Bearing B.",
        S(r"K_{assume}"): "Initially Assumed Geometry Factor for First Iteration of Bearing Selection.",
        S(r"L_{10}"): "Rated lifetime in number of cycles.",
        S(r"L_d"): "Design lifetime in number of cycles.",
        S(r"L_{hr}"): "Rated lifetime in number of hours.",
        S(r"R"): "Final Overall Reliability.",
        S(r"R_A"): "Final Reliability of bearing A.",
        S(r"R_B"): "Final Reliability of bearing B.",
        S(r"R_{dA}"): "Design Reliability of bearing A.",
        S(r"R_{dB}"): "Design Reliability of bearing B.",
        S(r"R_d"): "Design Overall Reliability.",
        S(r"a"): "Relationship between load and lifetime. 3.3 for cylinderical roller bearing.",
        S(r"a_f"): "Application Factor depending of the application of the bearing.",
        S(r"b"): "One of the Failure Distribution Parameters.",
        S(r"n"): "Rate of Rotation.",
        S(r"x_0"): "One of the Failure Distribution Parameters.",
        S(r"x_d"): "Dimension less Lifetime",
    },
    ComponentType.V_BELT: {
        S(r"B"): "A Helper Value for Computing Center Distance.",
        S(r"CD"): "Center Distance",
        S(r"CD_{rough}"): "Estimated Proper Center Distance",
        S(r"C_L"): "Length Correction Factor.",
        S(r"D_{in\,rough}"): "Estimated Input Sheave Diameter.",
        S(r"D_{in}"): "Input Sheave Diameter",
        S(r"D_{out}"): "Output Sheave Diameter",
        S(r"H_{all}"): "Allowable Power",
        S(r"H_{des}"): "Design Power",
        S(r"H_{ext}"): "Additional Allowable Power",
        S(r"H_{nom}"): "Nominal Power",
        S(r"H_{tab}"): "Tabulated Power",
        S(r"K_s"): "Service Factor",
        S(r"L"): "Belt Length",
        S(r"L_{rough}"): "Estimated Proper Belt Length",
        S(r"N_{belt}"): "Number of Belts used in Final Design",
        S(r"V"): "Belt Velocity",
        S(r"VR"): "Velocity Ratio, Input Angular Speed Over Output Angular Speed.",
        S(r"VR_{rough}"): "Estimated Velocity Ratio",
        S(r"V_{rough}"): "Estimated Belt Velocity",
        S(r"d"): "Span of the setup, Length of un-supported belt.",
        S(r"n_{in}"): "Input Angular Speed",
        S(r"n_{out\,rough}"): "Estimated Output Angular Speed",
        S(r"n_{out}"): "Output Angular Speed",
        S(r"n_{sf}"): "Final Safety Factor",
    },
    ComponentType.FLAT_BELT: {
        S(r"CD"): "Center Distance",
        S(r"C_p"): "Pulley Correction Factor",
        S(r"C_v"): "Velocity Correction Factor",
        S(r"D_{in\,min}"): "Minimum Diameter of the driving pulley (the smaller pulley).",
        S(r"D_{in}"): "Diameter of the driving pulley (the smaller pulley).",
        S(r"D_{out}"): "Diameter of the driven pulley (the larger pulley).",
        S(r"F_{1a}"): "Maximum tension that the belt can withstand.",
        S(r"F_2"): "Loose Side Tension.",
        S(r"F_a"): "Manufacture's Allowable Tension.",
        S(r"F_c"): "Centrifugal Tension.",
        S(r"F_i"): "Initial Tension.",
        S(r"H_{nom}"): "Nominal Power.",
        S(r"K_s"): "Service Factor.",
        S(r"L"): "Belt Length.",
        S(r"T_{in}"): "Torque on the driving pulley.",
        S(r"V"): "Belt Speed",
        S(r"VR"): "Velocity Ratio, Input Angular Speed over Output Angular Speed.",
        S(r"\Delta F"): "Different between Tight Side Tension and Loose Side Tension.",
        S(r"\gamma"): "Specific Weight.",
        S(r"\phi_{in}"): "Input Side Wrap Angle.",
        S(r"\phi_{out}"): "Output Side Wrap Angle.",
        S(r"b"): "Belt Width",
        S(r"dip"): "Midspan Dip",
        S(r"f"): "Coefficient of Friction.",
        S(r"n_d"): "Design Factor.",
        S(r"n_{in}"): "Input Angular Speed",
        S(r"n_{out}"): "Output Angular Speed",
        S(r"n_{sf}"): "Final Safety Factor",
        S(r"t"): "Belt Thinkness",
        S(r"w"): "Weight per Foot.",
    },
    ComponentType.SYNCHRONOUS_BELT: {
    },
    ComponentType.CHAIN: {
    },
    ComponentType.WIRE_ROPE: {
    },
    ComponentType.SPUR_GEAR: {
    },
    ComponentType.HELICAL_GEAR: {
    },
    ComponentType.BEVEL_GEAR: {
    },
    ComponentType.WORM_GEAR: {
    },
    ComponentType.RACK_PINION: {
    },
    ComponentType.BOUNDARY_LUBRICATED_BEARING: {
    },
    ComponentType.BALL_AND_CYLINDRICAL_BEARING_RADIAL: {
    },
    ComponentType.BALL_AND_CYLINDRICAL_BEARING_ALL: {
    },
    ComponentType.SHAFTS_AND_KEY: {
    },
    ComponentType.POWER_SCREWS: {
    },
    ComponentType.BALL_SCREWS: {
    },
    ComponentType.SPRINGS: {
    },
    ComponentType.FASTENER_AND_BOLTS: {
    },
}
units = {
    ComponentType.TAPERED_ROLLER_BEARING: {
        S(r"Bore A"): "mm",
        S(r"Bore B"): "mm",
        S(r"C_{10\,A}"): "kN",
        S(r"C_{10\,B}"): "kN",
        S(r"F_{ae}"): "kN",
        S(r"F_{eA}"): "kN",
        S(r"F_{eB}"): "kN",
        S(r"F_{rA}"): "kN",
        S(r"F_{rB}"): "kN",
        S(r"K_A"): "",
        S(r"K_B"): "",
        S(r"K_{assume}"): "",
        S(r"L_{10}"): "",
        S(r"L_d"): "",
        S(r"L_{hr}"): "hr",
        S(r"R"): "",
        S(r"R_A"): "",
        S(r"R_B"): "",
        S(r"R_{dA}"): "",
        S(r"R_{dB}"): "",
        S(r"R_d"): "",
        S(r"a"): "",
        S(r"a_f"): "",
        S(r"b"): "",
        S(r"n"): "RPM",
        S(r"x_0"): "",
        S(r"x_d"): "",
    },
    ComponentType.V_BELT: {
        S(r"B"): "",
        S(r"CD"): "inch",
        S(r"CD_{rough}"): "inch",
        S(r"C_L"): "",
        S(r"D_{in\,rough}"): "inch",
        S(r"D_{in}"): "inch",
        S(r"D_{out}"): "inch",
        S(r"H_{all}"): "hp",
        S(r"H_{des}"): "hp",
        S(r"H_{ext}"): "hp",
        S(r"H_{nom}"): "hp",
        S(r"H_{tab}"): "hp",
        S(r"K_s"): "",
        S(r"L"): "inch",
        S(r"L_{rough}"): "inch",
        S(r"N_{belt}"): "",
        S(r"V"): "ft/min",
        S(r"VR"): "",
        S(r"VR_{rough}"): "",
        S(r"V_{rough}"): "ft/min",
        S(r"d"): "inch",
        S(r"n_{in}"): "RPM",
        S(r"n_{out\,rough}"): "RPM",
        S(r"n_{out}"): "RPM",
        S(r"n_{sf}"): "",
    },
    ComponentType.FLAT_BELT: {
        S(r"CD"): "inch",
        S(r"C_p"): "",
        S(r"C_v"): "",
        S(r"D_{in\,min}"): "inch",
        S(r"D_{in}"): "inch",
        S(r"D_{out}"): "inch",
        S(r"F_{1a}"): "lbf",
        S(r"F_2"): "lbf",
        S(r"F_a"): "lbf/inch",
        S(r"F_c"): "lbf",
        S(r"F_i"): "lbf",
        S(r"H_{nom}"): "hp",
        S(r"K_s"): "",
        S(r"L"): "inch",
        S(r"T_{in}"): "lbf inch",
        S(r"V"): "ft/min",
        S(r"VR"): "",
        S(r"\Delta F"): "lbf",
        S(r"\gamma"): "lbf/inch^3",
        S(r"\phi_{in}"): "rad",
        S(r"\phi_{out}"): "rads",
        S(r"b"): "inch",
        S(r"dip"): "inch",
        S(r"f"): "",
        S(r"n_d"): "",
        S(r"n_{in}"): "RPM",
        S(r"n_{out}"): "RPM",
        S(r"n_{sf}"): "",
        S(r"t"): "inch",
        S(r"w"): "lbf/ft",
    },
    ComponentType.SYNCHRONOUS_BELT: {
    },
    ComponentType.CHAIN: {
    },
    ComponentType.WIRE_ROPE: {
    },
    ComponentType.SPUR_GEAR: {
    },
    ComponentType.HELICAL_GEAR: {
    },
    ComponentType.BEVEL_GEAR: {
    },
    ComponentType.WORM_GEAR: {
    },
    ComponentType.RACK_PINION: {
    },
    ComponentType.BOUNDARY_LUBRICATED_BEARING: {
    },
    ComponentType.BALL_AND_CYLINDRICAL_BEARING_RADIAL: {
    },
    ComponentType.BALL_AND_CYLINDRICAL_BEARING_ALL: {
    },
    ComponentType.SHAFTS_AND_KEY: {
    },
    ComponentType.POWER_SCREWS: {
    },
    ComponentType.BALL_SCREWS: {
    },
    ComponentType.SPRINGS: {
    },
    ComponentType.FASTENER_AND_BOLTS: {
    },
}
