import sys
import pandas as pd
import os

from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import QLabel, QVBoxLayout, QHeaderView

from uiWQI import Ui_MainWindow
from index_calc import IWQICalculator, DWQICalculator
from plotmodules import MplCanvas, PandasModel, PercentageCanvas
import config as cfg

def resource_path(relative_path):
    """ 
    Obtiene la ruta absoluta al recurso. 
    Funciona para desarrollo (VS Code) y para el .exe (PyInstaller).
    """
    try:
        # PyInstaller crea una carpeta temporal llamada _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        # Si no es un exe, usa la ruta actual
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


class WQI_Application(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Configuración inicial de la Interfaz
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.setWindowTitle("Calculadora WQI")
        
        # Asegúrate de usar la función resource_path que definimos antes
        # y que el archivo "icon_app.png" exista en tu carpeta resources
        
        app.setWindowIcon(QtGui.QIcon(resource_path("resources/icon_app.png")))

        # Variable de estado de carga del .csv
        self.csv_cargado = None

        self.df_result_IWQI = None
        self.df_result_DWQI = None

        self.plotIWQI = None
        self.plotDWQI = None

        self.plot_percent_IWQI = None
        self.plot_percent_DWQI = None

        self.filename_original = None

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

        #### Descargar Datos
        self.ui.pushButton_menu_download.clicked.connect(self.save_results)


    def save_results(self):
        # 1. Validar que haya datos cargados
        # 2. Detectar pestaña activa (0=IWQI, 1=DWQI)
        index_tab = self.ui.tabWidget.currentIndex()
        
        # Variables temporales para no repetir código
        df_target = None
        plot_main = None
        plot_perc = None
        suffix = ""

        if index_tab == 0: # Pestaña IWQI
            if self.df_result_IWQI is None:
                QtWidgets.QMessageBox.warning(self, "Aviso", "El índice IWQI no se ha calculado correctamente.")
                return
            df_target = self.df_result_IWQI
            plot_main = self.plotIWQI
            plot_perc = self.plot_percent_IWQI
            suffix = "IWQI"
            
        elif index_tab == 1: # Pestaña DWQI
            if self.df_result_DWQI is None:
                QtWidgets.QMessageBox.warning(self, "Aviso", "El índice DWQI no se ha calculado correctamente.")
                return
            df_target = self.df_result_DWQI
            plot_main = self.plotDWQI
            plot_perc = self.plot_percent_DWQI
            suffix = "DWQI"

        # 3. Pedir al usuario DÓNDE guardar (Seleccionar Carpeta)
        folder_path = QtWidgets.QFileDialog.getExistingDirectory(self, f"Seleccionar carpeta para guardar {suffix}")

        if folder_path:
            try:
                # Construir nombres de archivo basados en el original
                # Ej: Muestras_Rio_IWQI_Tabla.csv
                base_name = f"{self.filename_original}_{suffix}"
                
                path_csv = os.path.join(folder_path, f"{base_name}_Tabla.csv")
                path_plot_main = os.path.join(folder_path, f"{base_name}_Grafico_Principal.png")
                path_plot_perc = os.path.join(folder_path, f"{base_name}_Grafico_Porcentajes.png")

                # A. Guardar CSV
                # index=False para que no guarde el número de fila (0, 1, 2...)
                df_target.to_csv(path_csv, index=False, encoding='utf-8-sig') 

                # B. Guardar Gráfico Principal (MplCanvas)
                # Accedemos a la figura de Matplotlib (.fig) y usamos savefig
                if plot_main is not None:
                    plot_main.fig.savefig(path_plot_main, dpi=300, bbox_inches='tight')

                # C. Guardar Gráfico Porcentajes (PercentageCanvas)
                if plot_perc is not None:
                    plot_perc.fig.savefig(path_plot_perc, dpi=300, bbox_inches='tight')

                # Confirmación
                QtWidgets.QMessageBox.information(self, "Éxito", 
                    f"Archivos guardados correctamente en:\n{folder_path}\n\n"
                    f"1. {os.path.basename(path_csv)}\n"
                    f"2. {os.path.basename(path_plot_main)}\n"
                    f"3. {os.path.basename(path_plot_perc)}")

            except Exception as e:
                QtWidgets.QMessageBox.critical(self, "Error al guardar", f"Ocurrió un error:\n{str(e)}")

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

            self.filename_original = None

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
                filename = os.path.splitext(os.path.basename(path))[0]
                self.filename_original = filename

                self.getIWQI()
                self.getDWQI()

                self.ui.label_name_IWQI.setText(f"🌎{filename}")
                self.ui.label_name_IWQI.setStyleSheet("font-size: 12pt; color: #3C6E71; font-weight: bold;")
                
                self.ui.label_name_DWQI.setText(f"🌎{filename}")
                self.ui.label_name_DWQI.setStyleSheet("font-size: 12pt; color: #3C6E71; font-weight: bold;")

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
                name_col=df_final.columns[columna]
                if name_col in ["Muestra", "Sample", "ID", "id"]:
                    try:
                        # Lo convertimos a int para quitar el .0 y luego a string
                        texto_celda = str(int(valor))
                    except:
                        # Si por alguna razón es texto ("Muestra A"), se deja igual
                        texto_celda = str(valor)
                elif isinstance(valor, (float, int)):
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
    import ctypes
    myappid = 'unsw.tesis.wqicalculator.v1' 
    try:
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    except ImportError:
        pass
    # ----------------------------------------------

    app = QtWidgets.QApplication(sys.argv)
    
    # Cargar el icono TAMBIÉN en la aplicación global
    ruta_icono = resource_path("resources/icon_app.png")
    app.setWindowIcon(QtGui.QIcon(ruta_icono))
    
    window = WQI_Application()
    window.show()
    sys.exit(app.exec_())