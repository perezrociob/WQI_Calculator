############################################## IWQI ################################################################

## Configuración IWQI ##
IWQI_PARAMS = {
    "name": "IWQI",
    "columns_req": ["Muestra", "Na+", "Cl-", "HCO3-", "RAS", "CE"],
    "intervals": [
                    {"label": "Nula Restricción (NR)", "id": "NR", "start": 85.00005, "end": 100, "color": (0.188, 0.471, 0.212, 0.3)},
                    {"label": "Baja Restricción (BR)","id": "BR", "start": 70.00005, "end": 85, "color": (0.647, 0.714, 0.184, 0.3)},
                    {"label": "Moderada Restricción (MR)","id": "MR", "start": 55.00005, "end": 70, "color":(0.984, 0.765, 0.223, 0.3)},
                    {"label": "Alta Restricción (AR)","id": "AR", "start": 40.00005, "end": 55, "color":(0.894, 0.510, 0.172, 0.3)},
                    {"label": "Severa Restricción (SR)","id": "SR", "start": 0, "end": 40, "color": (1.0, 0.161, 0.118, 0.3)}
    ],
    "qi_ranges": {
                    "CE": [ # Unidades: uS/cm
                            {"qi_min": 85.0, "qi_max": 100.0, "x_inf": 200.0, "x_sup": 750.0},
                            {"qi_min": 60.0, "qi_max": 85.0, "x_inf": 750.0, "x_sup": 1500.0},
                            {"qi_min": 35.0, "qi_max": 60.0, "x_inf": 1500.0, "x_sup": 3000.0},
                            {"qi_min": 0.0, "qi_max": 35.0},
                        ],
                    "RAS": [ # Adimensional
                            {"qi_min": 85.0, "qi_max": 100.0, "x_inf": 2.0, "x_sup": 3.0},
                            {"qi_min": 60.0, "qi_max": 75.0, "x_inf": 3.0, "x_sup": 6.0},
                            {"qi_min": 35.0, "qi_max": 60.0, "x_inf": 6.0, "x_sup": 12.0},
                            {"qi_min": 0.0, "qi_max": 35.0},
                        ],
                    "Na+": [ # Unidades: mg/L
                            {"qi_min": 85.0, "qi_max": 100.0, "x_inf": 46, "x_sup": 69},
                            {"qi_min": 60.0, "qi_max": 75.0, "x_inf": 69, "x_sup": 138},
                            {"qi_min": 35.0, "qi_max": 60.0, "x_inf": 138, "x_sup": 207},
                            {"qi_min": 0.0, "qi_max": 35.0},
                            ],
                    "Cl-": [ # Unidades: mg/L
                            {"qi_min": 85.0, "qi_max": 100.0, "x_inf": 35.5, "x_sup": 140},
                            {"qi_min": 60.0, "qi_max": 75.0, "x_inf": 140, "x_sup": 248.5},
                            {"qi_min": 35.0, "qi_max": 60.0, "x_inf": 248.5, "x_sup": 355},
                            {"qi_min": 0.0, "qi_max": 35.0},
                            ],
                    "HCO3-": [ # Unidades: mg/L
                               {"qi_min": 85.0, "qi_max": 100.0, "x_inf": 61, "x_sup": 91.5},
                               {"qi_min": 60.0, "qi_max": 85.0, "x_inf": 91.5, "x_sup": 274.5},
                               {"qi_min": 35.0, "qi_max": 60.0, "x_inf": 274.5, "x_sup": 518.5},
                               {"qi_min": 0.0, "qi_max": 35.0},
                               ],
                },
    "relative_weights": {
                        "CE": 0.211,
                        "Na+": 0.204,
                        "Cl-": 0.194,
                        "RAS": 0.189,
                        "HCO3-": 0.202
                        }
}

DWQI_PARAMS = {
    "name": "DWQI",
    "columns_req": ["Muestra", "K+", "Na+", "Mg++", "Ca++", "HCO3-", "Cl-", "SO4--", "pH", "SDT"],
    "intervals": [
        # Rangos típicos del WQI (puedes ajustarlos)
        {"label": "Excelente (E)",      "id": "E", "start": 0,   "end": 25,  "color": (0.188, 0.471, 0.212, 0.3)}, # Verde
        {"label": "Buena (B)",          "id": "B", "start": 25,  "end": 50,  "color": (0.647, 0.714, 0.184, 0.3)}, # Verde claro
        {"label": "Regular (R)",          "id": "R", "start": 50,  "end": 75,  "color": (0.984, 0.765, 0.223, 0.3)}, # Amarillo
        {"label": "Mala (M)",      "id": "M", "start": 75,  "end": 100, "color": (0.894, 0.510, 0.172, 0.3)}, # Naranja
        {"label": "No Apta (NA)",     "id": "NA", "start": 100, "end": 200,"color": (1.0, 0.161, 0.118, 0.3)}  # Rojo
    ],
    "standards_WHO": { # Unidades estándar (generalmente mg/L)
        "K+": 12,
        "Na+": 200,
        "Mg++": 30,
        "Ca++": 75,
        "HCO3-": 120,
        "Cl-": 250,
        "SO4--": 250,
        "pH": 8.5,
        "SDT": 500
    },
    "relative_weights": {
        "K+": 0.065,
        "Na+": 0.129,
        "Mg++": 0.097,
        "Ca++": 0.097,
        "HCO3-": 0.032,
        "Cl-": 0.161,
        "SO4--": 0.161,
        "pH": 0.097,
        "SDT": 0.161
    },
    "ideal_values": { # I_i (generalmente 0, excepto pH que es 7)
        "pH": 7.0
    }
}

NAMES_CONC={
    "Na+": "Na⁺",      
    "Cl-": "Cl⁻",      
    "HCO3-": "HCO₃⁻",  
    "SO4--": "SO₄²⁻",  
    "CO3--": "CO₃²⁻",  
    "NO3-": "NO₃⁻",   
    "Ca++": "Ca²⁺",    
    "Mg++": "Mg²⁺",    
    "K+": "K⁺",                  
}

UNITS_MAP = {
    "Na+": "mg/L",
    "Cl-": "mg/L",
    "HCO3-": "mg/L",
    "K+": "mg/L",
    "Mg++": "mg/L",
    "Ca++": "mg/L",
    "SO4--": "mg/L",
    #"RAS": "",
    "CE": "uS/cm",
    #"pH": "",
    #"SDT":"",
    #"IWQI": "", 
    #"DWQI": "" 
}