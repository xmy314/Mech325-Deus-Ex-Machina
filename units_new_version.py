from infrastructure import QuestionType
from sympy import Symbol as S
descriptions = {
    QuestionType.TAPERED_ROLLER_BEARING: {
        S('Bore A'): 'Bore Diameter of bearing A',
        S('Bore B'): 'Bore Diameter of bearing B',
        S('C_{10\,A}'): 'Rated Load for Bearing A.',
        S('C_{10\,B}'): 'Rated Load for Bearing B.',
        S('F_{ae}'): 'Equivalent Axial Load.',
        S('F_{eA}'): 'Equivalent Radial Load at Bearing A.',
        S('F_{eB}'): 'Equivalent Radial Load at Bearing B.',
        S('F_{rA}'): 'Radial Load at Bearing A.',
        S('F_{rB}'): 'Radial Load at Bearing B.',
        S('K_A'): 'Geometry Factor for Bearing A.',
        S('K_B'): 'Geometry Factor for Bearing B.',
        S('K_{assume}'): 'Initially Assumed Geometry Factor for First Iteration of Bearing Selection.',
        S('L_{10}'): 'Rated lifetime in number of cycles.',
        S('L_d'): 'Design lifetime in number of cycles.',
        S('L_{hr}'): 'Rated lifetime in number of hours.',
        S('R'): 'Final Overall Reliability.',
        S('R_A'): 'Final Reliability of bearing A.',
        S('R_B'): 'Final Reliability of bearing B.',
        S('R_{dA}'): 'Design Reliability of bearing A.',
        S('R_{dB}'): 'Design Reliability of bearing B.',
        S('R_d'): 'Design Overall Reliability.',
        S('	heta'): 'One of the Failure Distribution Parameters.',
        S('a'): 'Relationship between load and lifetime. 3.3 for cylinderical roller bearing.',
        S('a_f'): 'Application Factor depending of the application of the bearing.',
        S('b'): 'One of the Failure Distribution Parameters.',
        S('n'): 'Rate of Rotation.',
        S('x_0'): 'One of the Failure Distribution Parameters.',
        S('x_d'): 'Dimension less Lifetime',
    },
    QuestionType.V_BELT: {
        S('B'): 'A Helper Value for Computing Center Distance.',
        S('CD'): 'Center Distance',
        S('CD_{rough}'): 'Estimated Proper Center Distance',
        S('C_L'): 'Length Correction Factor.',
        S('C_{\theta}'): 'Wrap Angle Correction Factor.',
        S('D_{in\,rough}'): 'Estimated Input Sheave Diameter.',
        S('D_{in}'): 'Input Sheave Diameter',
        S('D_{out}'): 'Output Sheave Diameter',
        S('H_{all}'): 'Allowable Power',
        S('H_{des}'): 'Design Power',
        S('H_{ext}'): 'Additional Allowable Power',
        S('H_{nom}'): 'Nominal Power',
        S('H_{tab}'): 'Tabulated Power',
        S('K_s'): 'Service Factor',
        S('L'): 'Belt Length',
        S('L_{rough}'): 'Estimated Proper Belt Length',
        S('N_{belt}'): 'Number of Belts used in Final Design',
        S('V'): 'Belt Velocity',
        S('VR'): 'Velocity Ratio, Input Angular Speed Over Output Angular Speed.',
        S('VR_{rough}'): 'Estimated Velocity Ratio',
        S('V_{rough}'): 'Estimated Belt Velocity',
        S('\theta_{in}'): 'Input Sheave Wrap Angle',
        S('\theta_{out}'): 'Output Sheave Wrap Angle',
        S('d'): 'Span of the setup, Length of un-supported belt.',
        S('n_{in}'): 'Input Angular Speed',
        S('n_{out\,rough}'): 'Estimated Output Angular Speed',
        S('n_{out}'): 'Output Angular Speed',
        S('n_{sf}'): 'Final Safety Factor',
    },
    QuestionType.FLAT_BELT: {
        S('CD'): 'Center Distance',
        S('C_p'): 'Pulley Correction Factor',
        S('C_v'): 'Velocity Correction Factor',
        S('D_{in\,min}'): 'Minimum Diameter of the driving pulley (the smaller pulley).',
        S('D_{in}'): 'Diameter of the driving pulley (the smaller pulley).',
        S('D_{out}'): 'Diameter of the driven pulley (the larger pulley).',
        S('F_{1a}'): 'Maximum tension that the belt can withstand.',
        S('F_2'): 'Loose Side Tension.',
        S('F_a'): "Manufacture's Allowable Tension.",
        S('F_c'): 'Centrifugal Tension.',
        S('F_i'): 'Initial Tension.',
        S('H_a'): 'Maximum Allowable Power.',
        S('H_d'): 'Design Power.',
        S('H_{nom}'): 'Nominal Power.',
        S('K_s'): 'Service Factor.',
        S('L'): 'Belt Length.',
        S('T_{in}'): 'Torque on the driving pulley.',
        S('V'): 'Belt Speed',
        S('VR'): 'Velocity Ratio, Input Angular Speed over Output Angular Speed.',
        S('\Delta F'): 'Different between Tight Side Tension and Loose Side Tension.',
        S('\gamma'): 'Specific Weight.',
        S('\phi_{in}'): 'Input Side Wrap Angle.',
        S('\phi_{out}'): 'Output Side Wrap Angle.',
        S('b'): 'Belt Width',
        S('dip'): 'Midspan Dip',
        S('f'): 'Coefficient of Friction.',
        S('n_d'): 'Design Factor.',
        S('n_{in}'): 'Input Angular Speed',
        S('n_{out}'): 'Output Angular Speed',
        S('n_{sf}'): 'Final Safety Factor',
        S('t'): 'Belt Thinkness',
        S('w'): 'Weight per Foot.',
    },
    QuestionType.SYNCHRONOUS_BELT: {
    },
}
units = {
    QuestionType.TAPERED_ROLLER_BEARING: {
        S('Bore A'): 'mm',
        S('Bore B'): 'mm',
        S('C_{10\,A}'): 'kN',
        S('C_{10\,B}'): 'kN',
        S('F_{ae}'): 'kN',
        S('F_{eA}'): 'kN',
        S('F_{eB}'): 'kN',
        S('F_{rA}'): 'kN',
        S('F_{rB}'): 'kN',
        S('K_A'): '',
        S('K_B'): '',
        S('K_{assume}'): '',
        S('L_{10}'): '',
        S('L_d'): '',
        S('L_{hr}'): 'hr',
        S('R'): '',
        S('R_A'): '',
        S('R_B'): '',
        S('R_{dA}'): '',
        S('R_{dB}'): '',
        S('R_d'): '',
        S('	heta'): '',
        S('a'): '',
        S('a_f'): '',
        S('b'): '',
        S('n'): 'RPM',
        S('x_0'): '',
        S('x_d'): '',
    },
    QuestionType.V_BELT: {
        S('B'): '',
        S('CD'): 'inch',
        S('CD_{rough}'): 'inch',
        S('C_L'): '',
        S('C_{\theta}'): '',
        S('D_{in\,rough}'): 'inch',
        S('D_{in}'): 'inch',
        S('D_{out}'): 'inch',
        S('H_{all}'): 'hp',
        S('H_{des}'): 'hp',
        S('H_{ext}'): 'hp',
        S('H_{nom}'): 'hp',
        S('H_{tab}'): 'hp',
        S('K_s'): '',
        S('L'): 'inch',
        S('L_{rough}'): 'inch',
        S('N_{belt}'): '',
        S('V'): 'ft/min',
        S('VR'): '',
        S('VR_{rough}'): '',
        S('V_{rough}'): 'ft/min',
        S('\theta_{in}'): 'rads',
        S('\theta_{out}'): 'rads',
        S('d'): 'inch',
        S('n_{in}'): 'RPM',
        S('n_{out\,rough}'): 'RPM',
        S('n_{out}'): 'RPM',
        S('n_{sf}'): '',
    },
    QuestionType.FLAT_BELT: {
        S('CD'): 'inch',
        S('C_p'): '',
        S('C_v'): '',
        S('D_{in\,min}'): 'inch',
        S('D_{in}'): 'inch',
        S('D_{out}'): 'inch',
        S('F_{1a}'): 'lbf',
        S('F_2'): 'lbf',
        S('F_a'): 'lbf/inch',
        S('F_c'): 'lbf',
        S('F_i'): 'lbf',
        S('H_a'): 'hp',
        S('H_d'): 'hp',
        S('H_{nom}'): 'hp',
        S('K_s'): '',
        S('L'): 'inch',
        S('T_{in}'): 'lbf inch',
        S('V'): 'ft/min',
        S('VR'): '',
        S('\Delta F'): 'lbf',
        S('\gamma'): 'lbf/inch^3',
        S('\phi_{in}'): 'rad',
        S('\phi_{out}'): 'rads',
        S('b'): 'inch',
        S('dip'): 'inch',
        S('f'): '',
        S('n_d'): '',
        S('n_{in}'): 'RPM',
        S('n_{out}'): 'RPM',
        S('n_{sf}'): '',
        S('t'): 'inch',
        S('w'): 'lbf/ft',
    },
    QuestionType.SYNCHRONOUS_BELT: {
    },
}
