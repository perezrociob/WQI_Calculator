import sys
import pandas as pd

from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import QLabel, QVBoxLayout, QHeaderView

from uiWQI import Ui_MainWindow
from index_calc import IWQICalculator, DWQICalculator
from plotmodules import MplCanvas, PandasModel, PercentageCanvas
import config as cfg

class WQI_Application(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Configuración inicial de la Interfaz
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # Variable de estado de carga del .csv
        self.csv_cargado = None

        self.df_result_IWQI = None
        self.df_result_DWQI = None

        self.plotIWQI = None
        self.plotDWQI = None

        self.plot_percent_IWQI = None
        self.plot_percent_DWQI = None

        # Inicializar tablas
        self.clean_table(self.ui.tableWidget_IWQI)
        self.clean_table(self.ui.tableWidget_DWQI)
        self.ui.tableWidget_IWQI.verticalHeader().setVisible(False)
        self.ui.tableWidget_DWQI.verticalHeader().setVisible(False)

        # Inicializar gráficos
        self.set_placeholder(self.ui.widget_plot_IWQI, "No hay datos cargados")
        self.set_placeholder(self.ui.widget_plot_DWQI, "No hay datos cargados")
        self.set_placeholder(self.ui.widget_percents_IWQI, "No hay datos cargados")
        self.set_placeholder(self.ui.widget_percents_DWQI, "No hay datos cargados")

        # Inicializar comboboxes
        self.ui.comboBox_IWQI.addItem('Sin Eje Secundario')
        self.ui.comboBox_DWQI.addItem('Sin Eje Secundario')

        # Conexiones
        #### Cargar datos
        self.ui.pushButton_menu_load.clicked.connect(self.load_filecsv)

        #### Seleccion en el ComboBox
        self.ui.comboBox_IWQI.currentTextChanged.connect(self.OnChange_second_axis_IWQI)
        self.ui.comboBox_DWQI.currentTextChanged.connect(self.OnChange_second_axis_DWQI)

        ##### Cambio de tab
        self.ui.tabWidget.currentChanged.connect(self.OnChange_tabwidget)

    def OnChange_second_axis_IWQI(self):
        if self.csv_cargado is None:
            return
        
        if self.df_result_IWQI is not None:
            col_sel = self.ui.comboBox_IWQI.currentData()
            self.update_data(self.df_result_IWQI,'IWQI', col_sel)

    def OnChange_second_axis_DWQI(self):
        if self.csv_cargado is None:
            return
        
        if self.df_result_DWQI is not None:
            col_sel = self.ui.comboBox_DWQI.currentData()
            self.update_data(self.df_result_DWQI, 'DWQI', col_sel)
        
        

    def OnChange_tabwidget(self):
        if self.csv_cargado is None:
            return

        # Pestaña activa:
        ## 0 = Pestaña IWQI
        ## 1 = Pestaña DWQI
        actual_index = self.ui.tabWidget.currentIndex()

        if actual_index == 0:
            if self.df_result_IWQI is not None:
                col_sel = self.ui.comboBox_IWQI.currentData()
                self.update_data(self.df_result_IWQI,'IWQI', col_sel)
        # Pestaña DWQI (Nuevo bloque)
        elif actual_index == 1:
            if self.df_result_DWQI is not None:
                col_sel = self.ui.comboBox_DWQI.currentData()
                self.update_data(self.df_result_DWQI, 'DWQI', col_sel)
        ###############
    

    def clean_table(self, table_widget):
        table_widget.setRowCount(0)
        table_widget.setColumnCount(0)
        table_widget.clear()

    def set_placeholder(self, widget_contenedor, msg):
        if widget_contenedor.layout() is None:
            layout = QVBoxLayout(widget_contenedor)
        else:
            layout = widget_contenedor.layout()
            # Borrar widgets viejos del layout
            while layout.count():
                child = layout.takeAt(0)
                if child.widget():
                    child.widget().deleteLater()
        
       
        lbl_placeholder = QLabel(msg)
        lbl_placeholder.setAlignment(QtCore.Qt.AlignCenter)
        # Estilo minimalista para el aviso
        lbl_placeholder.setStyleSheet("""
            QLabel {
                color: #999999;
                font-size: 14px;
                font-family: "Segoe UI";
                font-weight: bold;
            }
        """)
        
        # Agregarlo al contenedor
        layout.addWidget(lbl_placeholder)

    def add_plot(self, widget_contenedor, plot_type):
        # Limpiar layout (borra el Label de "No hay datos")
        layout = widget_contenedor.layout()
        if layout is None:
            layout = QVBoxLayout(widget_contenedor)
        
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        # Instanciar e insertar tu Gráfico (MplCanvas)
        if plot_type == 'MplCanvas':
            plt = MplCanvas(self, width=5, height=4, dpi=100)
        elif plot_type == 'PercentageCanvas':
            plt = PercentageCanvas(self,width=5,height=3,dpi=100)

        layout.addWidget(plt)

        return plt
        

    def load_filecsv(self):
        print("¡Clic recibido! Intentando abrir diálogo...")
        """Cuadro de diálogo para buscar el CSV"""
        path, _ = QtWidgets.QFileDialog.getOpenFileName(
                self, "Abrir CSV de Calidad de Agua", "", "CSV Files (*.csv);;Excel Files (*.xlsx)"
                )
        
        if self.csv_cargado is not None:
            self.csv_cargado = None
            
            self.df_result_IWQI = None
            self.df_result_DWQI = None

            self.ui.comboBox_IWQI.blockSignals(True)
            self.ui.comboBox_IWQI.clear()
            self.ui.comboBox_IWQI.addItem('Sin Eje Secundario','Sin Eje Secundario')
            self.ui.comboBox_IWQI.blockSignals(False)

            self.ui.comboBox_DWQI.blockSignals(True)
            self.ui.comboBox_DWQI.clear()
            self.ui.comboBox_DWQI.addItem('Sin Eje Secundario', 'Sin Eje Secundario')
            self.ui.comboBox_DWQI.blockSignals(False)

        if path:
            try:
                if path.endswith('.csv'):
                    self.csv_cargado = pd.read_csv(path)
                else:
                    self.csv_cargado = pd.read_excel(path)
                
            # Feedback al usuario
                #self.ui.statusbar.showMessage(f"Archivo cargado: {path}")

                self.getIWQI()
                self.getDWQI()

            except Exception as e:
                QtWidgets.QMessageBox.critical(self, "Error al cargar", str(e))

    
    def getIWQI(self):
        if self.csv_cargado is None:
            QtWidgets.QMessageBox.warning(self, "Atención", "Primero carga un archivo CSV.")
            return
        try:
            calc =IWQICalculator()
            print(self.csv_cargado.shape)
            df_result, err_col, err_data = calc.calcIndex(self.csv_cargado)

            if (err_col == '0' and err_data == '0'):

                # Guardar resultado en variable de estado
                self.df_result_IWQI = df_result

                if self.ui.comboBox_IWQI.count() >= 1: 
                    columnas_extra = [c for c in cfg.IWQI_PARAMS['columns_req']]
                    
                    self.ui.comboBox_IWQI.blockSignals(True)
                    self.ui.comboBox_IWQI.clear()
                    self.ui.comboBox_IWQI.addItem('Sin Eje Secundario','Sin Eje Secundario')
                    for c in columnas_extra:
                        styled_name = cfg.NAMES_CONC.get(c, c)
                        self.ui.comboBox_IWQI.addItem(styled_name, c)
                    self.ui.comboBox_IWQI.blockSignals(False)

                actual_eje_sec = self.ui.comboBox_IWQI.currentData()

                
                self.update_data(df_result,'IWQI', actual_eje_sec)

        except ValueError as e:
            # Errores de validación (faltan columnas, etc)
            QtWidgets.QMessageBox.warning(self, "Error en Datos", str(e))
        except Exception as e:
            # Errores de programación o inesperados
            QtWidgets.QMessageBox.critical(self, "Error Crítico", str(e))
            print(e) # Para ver el error en la consola de VS Code

    def getDWQI(self):
        """Lógica espejo a getIWQI pero para DWQI"""
        if self.csv_cargado is None:
            return # O lanzar advertencia si se llama manualmente

        try:
            calc = DWQICalculator()
            # Validar si el CSV tiene las columnas necesarias para DWQI
            # (El calculador lo valida internamente, pero aquí preparamos la UI)
            df_result, err_col, err_data = calc.calcIndex(self.csv_cargado)

            if (err_col == '0' and err_data == '0'):
                # Guardar resultado
                self.df_result_DWQI = df_result
                
                # Llenar ComboBox DWQI
                if self.ui.comboBox_DWQI.count() >= 1: 
                    # Usamos las columnas requeridas definidas en config
                    columnas_extra = [c for c in cfg.DWQI_PARAMS['columns_req']]
                    
                    self.ui.comboBox_DWQI.blockSignals(True)
                    self.ui.comboBox_DWQI.clear()
                    self.ui.comboBox_DWQI.addItem('Sin Eje Secundario', 'Sin Eje Secundario')
                    for c in columnas_extra:
                        if c != "Muestra": # Evitamos duplicar 'Muestra'
                            styled_name = cfg.NAMES_CONC.get(c, c)
                            self.ui.comboBox_DWQI.addItem(styled_name, c)
                    self.ui.comboBox_DWQI.blockSignals(False)

                actual_eje_sec = self.ui.comboBox_DWQI.currentData()
                
                # Actualizar Tablas y Gráficos
                self.update_data(df_result, 'DWQI', actual_eje_sec)
            
            else:
                # Si faltan columnas, simplemente no calculamos DWQI (puede ser un CSV solo para IWQI)
                # Podrías imprimir un log discreto: print(f"No se pudo calcular DWQI: {err_col}")
                pass

        except Exception as e:
            print(f"Error calculando DWQI: {e}")


    def fill_tableWidget(self,table_widget,df, cols = None):

        if cols:
            # Seleccionamos solo las columnas que existen en el DF para evitar errores
            cols_val= [c for c in cols if c in df.columns]
            
            # Creamos un SUB-DataFrame solo con lo que queremos mostrar
            df_final = df[cols_val].copy()
        else:
            df_final = df.copy()

        table_widget.setSortingEnabled(False)
        table_widget.setRowCount(len(df_final))
        table_widget.setColumnCount(len(df_final.columns)) 
        


        styled_headers = []

        for i,c in enumerate(df_final.columns):
            original_name = str(c)

            styled_name =cfg.NAMES_CONC.get(original_name,original_name)

            unit = cfg.UNITS_MAP.get(original_name, "")

            header_item =QtWidgets.QTableWidgetItem(styled_name)

            if unit:
                header_item.setToolTip(unit)

            table_widget.setHorizontalHeaderItem(i, header_item)

        # 3. Llenar celda por celda
        for fila in range(len(df_final)):
            for columna in range(len(df_final.columns)):
                # Obtener el valor
                valor = df_final.iloc[fila, columna]
                
                # Formatear: Si es float, limitar decimales. Si es texto, dejar igual.
                if isinstance(valor, (float, int)):
                    texto_celda = f"{valor:.2f}" # 2 decimales
                else:
                    texto_celda = str(valor)

                # Crear el Item de la tabla
                item = QtWidgets.QTableWidgetItem(texto_celda)
                
                # Alineación centrada (para mantener tu estilo minimalista)
                item.setTextAlignment(QtCore.Qt.AlignCenter)
                
                # Insertar en la tabla
                table_widget.setItem(fila, columna, item)

    def update_data(self, df_r, wqi_index, eje_sec):
        print("metodo: Actualizando gráfico: ", wqi_index)
        
        # DATOS
        x = pd.to_numeric(df_r['Muestra'], errors='coerce').astype('Int64')


        if wqi_index == 'IWQI':
            y_wqi = df_r['IWQI']
            intervals_wqi_config = cfg.IWQI_PARAMS['intervals']
            tableWidget_wqi = self.ui.tableWidget_IWQI

            if self.plotIWQI is None:
                self.plotIWQI = self.add_plot(self.ui.widget_plot_IWQI,"MplCanvas")
            if self.plot_percent_IWQI is None:
                self.plot_percent_IWQI = self.add_plot(self.ui.widget_percents_IWQI,"PercentageCanvas")

            plot_wqi = self.plotIWQI
            plot_percent_iwqi = self.plot_percent_IWQI
            plot_percent_iwqi.update_chart(y_wqi, cfg.IWQI_PARAMS['intervals'])
            cols_tabla = ["Muestra", "Na+", "Cl-", "HCO3-", "RAS", "CE", "IWQI"]
        elif wqi_index == 'DWQI':
            y_wqi = df_r['DWQI']
            intervals_wqi_config = cfg.DWQI_PARAMS['intervals'] # Usar config DWQI
            tableWidget_wqi = self.ui.tableWidget_DWQI # Usar tabla DWQI

            if self.plotDWQI is None:
                self.plotDWQI = self.add_plot(self.ui.widget_plot_DWQI, "MplCanvas")
            if self.plot_percent_DWQI is None:
                self.plot_percent_DWQI = self.add_plot(self.ui.widget_percents_DWQI, "PercentageCanvas")
            
            plot_wqi = self.plotDWQI
            plot_percent_wqi = self.plot_percent_DWQI
            
            # Actualizar gráfico de porcentajes
            plot_percent_wqi.update_chart(y_wqi, intervals_wqi_config)

            cols_tabla = ["Muestra", "K+", "Na+", "Mg++", "Ca++", "HCO3-", "Cl-", "SO4--", "pH", "SDT", "DWQI"]
        #else LWQI....

        if eje_sec != 'Sin Eje Secundario':
            y_sec = df_r[eje_sec]
        else:
            y_sec= None


        self.fill_tableWidget(tableWidget_wqi, df_r, cols_tabla)

        # Actualizacion del grafico
        plot_wqi.update_plot(
            x_data=x, 
            y_data=y_wqi, 
            y_data_2=y_sec, 
            intervals_config=intervals_wqi_config,
            index_label=wqi_index,
            sec_label=eje_sec,
            x_label = 'Muestra'
        )




if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    ventana = WQI_Application()
    ventana.show()
    sys.exit(app.exec_())