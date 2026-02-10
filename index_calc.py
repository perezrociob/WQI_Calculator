import pandas as pd
import numpy as np
from abc import ABC, abstractmethod
from config import IWQI_PARAMS, DWQI_PARAMS

class IndexCalculator(ABC):
    """Clase abstracta"""
    def __init__(self, config):
        self.config=config
        self.intervalos=config["intervals"]
        self.cols_req=config["columns_req"]

    def _check_data(self,df):
        error_check_column = '0'
        error_check_data = '0'
        # Validar si estan las columnas requeridas, segun el indice a calcular
        missing_cols = [col for col in self.cols_req if col not in df.columns]

        # Validar si no hay datos faltantes en las columnas requeridas
        actual_cols = [col for col in df if col not in missing_cols]
        missing_data = df[actual_cols].isnull().any()

        if missing_cols:
            error_check_column =f"{', '.join(missing_cols)}"

        if missing_data.any():
            error_check_data = f"Hay datos faltantes"

        return error_check_column, error_check_data
    
    def _mg2meq(self,df, df_units):
        conversion_factors = {
            "Na+": 1 / 23.0,      # Na+ peso equivalente = 23
            "Cl-": 1 / 35.45,     # Cl- peso equivalente ≈ 35.45
            "HCO3-": 1 / 61.0,    # HCO3- peso equivalente ≈ 61
            "Ca2+": 2 / 40.08,    # Ca2+ peso equivalente ≈ 20.04 (40.08/2)
            "Mg2+": 2 / 24.31     # Mg2+ peso equivalente ≈ 12.155
        }
        df_2 = df.copy()
        for col in df.columns:
            if col in conversion_factors:
                if df_units[col].values == 'mg/L':
                    df_2[col] = pd.to_numeric(df[col], errors="coerce") * conversion_factors[col]
        return df_2
    
    
    @abstractmethod
    def calcIndex(self,df):
        """Algoritmo según el indice"""
        pass

class IWQICalculator(IndexCalculator):
    def __init__(self):
        super().__init__(IWQI_PARAMS)
        self.qi_ranges = self.config["qi_ranges"]
        self.relative_weights = self.config["relative_weights"]



    def __qi_IWQI(self, xij, parameter):
        if parameter in self.qi_ranges.keys():
            i = 0
            flag_interval = False
            while ((i<(len(self.qi_ranges[parameter])-1)) and (not flag_interval)):
                x_inf = self.qi_ranges[parameter][i]['x_inf']
                x_sup = self.qi_ranges[parameter][i]['x_sup']
                if xij>=x_inf and xij<x_sup:
                    qi_min = self.qi_ranges[parameter][i]['qi_min']
                    qi_max = self.qi_ranges[parameter][i]['qi_max']
                    flag_interval = True
                else:
                    i+=1

            if not flag_interval:
                x_inf = self.qi_ranges[parameter][0]['x_inf']
                x_sup = self.qi_ranges[parameter][2]['x_sup']

                dist_inf = abs(xij-x_inf)
                dist_sup = abs(xij-x_sup)

                if dist_sup < dist_inf:
                    x_inf = self.qi_ranges[parameter][2]['x_inf']
                    x_sup = self.qi_ranges[parameter][2]['x_sup']
                    xij = x_sup - 0.0000001 # Parentesis derecho abierto
                    qi_min = self.qi_ranges[parameter][2]['qi_min']
                    qi_max = self.qi_ranges[parameter][2]['qi_max']
                else:
                    x_inf = self.qi_ranges[parameter][0]['x_inf']
                    x_sup = self.qi_ranges[parameter][0]['x_sup']
                    xij = x_inf
                    qi_min = self.qi_ranges[parameter][0]['qi_min']
                    qi_max = self.qi_ranges[parameter][0]['qi_max']

            qi_amp = qi_max - qi_min
            x_amp = x_sup - x_inf
        return qi_max - ((xij-x_inf)*qi_amp/x_amp)
    
    def __calc_IWQI_row(self, xNa, xCl, xEC, xSAR, xHCO3):
        qiNa = self.__qi_IWQI(xNa,'Na+')
        qiCl = self.__qi_IWQI(xCl,'Cl-')
        qiEC = self.__qi_IWQI(xEC,'CE')
        qiSAR = self.__qi_IWQI(xSAR,'RAS')
        qiHCO3 = self.__qi_IWQI(xHCO3,'HCO3-')

        # SUM
        IWQI = qiNa*self.relative_weights['Na+'] + qiCl*self.relative_weights['Cl-'] + qiEC*self.relative_weights['CE'] + qiSAR*self.relative_weights['RAS'] + qiHCO3*self.relative_weights['HCO3-']
        return IWQI
    
    def __calculo_IWQI(self, cols):
        xNa = cols['Na+']
        xCl = cols['Cl-']
        xEC = cols['CE']
        xSAR = cols['RAS']
        xHCO3 = cols['HCO3-']
        return self.__calc_IWQI_row(xNa, xCl, xEC, xSAR, xHCO3)


    def calcIndex(self, df):
        # Extraer las unidades
        df_units=pd.DataFrame([df.iloc[0]], columns=df.columns)
        df_data = pd.DataFrame(df.iloc[1:], columns=df.columns)
        df_data.reset_index(drop=True, inplace = True)

        # Convertir los datos a tipo númerico, excepto la columna 'Muestra'
        for c in df_data.columns:
            if c != 'Muestra':
                df_data[c] = pd.to_numeric(df_data[c], errors='coerce')
        
        err_columns, err_data = self._check_data(df_data)

        if (err_columns == '0' and err_data == '0'):
            #df_data= self._mg2meq(df_data, df_units)
            df_data['IWQI'] = df_data.apply(self.__calculo_IWQI, axis=1)

        return df_data, err_columns, err_data

class DWQICalculator(IndexCalculator):
    def __init__(self):
        super().__init__(DWQI_PARAMS)
        self.standards = self.config["standards_WHO"]
        self.relative_weights = self.config["relative_weights"]
        self.ideal_values = self.config.get("ideal_values", {})

    def __qi_DWQI(self, Mi, parameter):
        """
        Calcula el subíndice Qi para un parámetro dado.
        Fórmula: Qi = [(Mi - Ii) / (Si - Ii)] * 100
        Donde:
            Mi = Valor medido
            Si = Estándar
            Ii = Valor ideal (0 para la mayoría, 7 para pH)
        """
        if parameter in self.standards:
            Si = self.standards[parameter]
            Ii = self.ideal_values.get(parameter, 0) # Si no está definido (como K+, Na+...), es 0
            
            # Evitar división por cero si Si == Ii (no debería pasar con estos estándares)
            if Si - Ii == 0:
                return 0
                
            Qi = ((Mi - Ii) / (Si - Ii)) * 100
            return Qi
        return 0

    def __calculo_DWQI_row(self, row):
        """Calcula el DWQI para una fila de datos"""
        QiWi_sum = 0
        Wi_sum = 0

        # Iteramos sobre los parámetros definidos en los pesos
        for param, weight in self.relative_weights.items():
            # Obtenemos el valor medido (Mi) de la columna correspondiente
            if param in row:
                Mi = row[param]
                Qi = self.__qi_DWQI(Mi, param)
                
                QiWi_sum += Qi * weight
                Wi_sum += weight
        
        if Wi_sum == 0:
            return 0
            
        return QiWi_sum / Wi_sum

    def calcIndex(self, df):
        # 1. Copia y limpieza básica
        df_data = pd.DataFrame(df.iloc[1:], columns=df.columns) # Saltamos la fila de unidades
        df_data.reset_index(drop=True, inplace=True)

        # 2. Convertir a numérico
        for c in df_data.columns:
            if c != 'Muestra':
                df_data[c] = pd.to_numeric(df_data[c], errors='coerce')
        
        # 3. Chequeo de errores (usando el método de la clase padre)
        err_columns, err_data = self._check_data(df_data)

        if (err_columns == '0' and err_data == '0'):
            # NOTA: Para DWQI el notebook dice "No convertir en este caso", 
            # así que NO llamamos a self._mg2meq()
            
            # 4. Calcular índice fila por fila
            df_data['DWQI'] = df_data.apply(self.__calculo_DWQI_row, axis=1)

        return df_data, err_columns, err_data

