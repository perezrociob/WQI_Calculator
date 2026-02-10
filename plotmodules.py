import matplotlib
import mplcursors
import config as cfg
matplotlib.use('Qt5Agg')
from PyQt5 import QtWidgets
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.ticker import MaxNLocator
from matplotlib.figure import Figure
from PyQt5.QtCore import QAbstractTableModel, Qt
import numpy as np

# Clase auxiliar para mostrar DataFrames en QTableView.
class PandasModel(QAbstractTableModel):
    def __init__(self, data):
        super(PandasModel, self).__init__()
        self._data = data

    def rowCount(self, parent=None):
        return self._data.shape[0]

    def columnCount(self, parent=None):
        return self._data.shape[1]

    def data(self, index, role=Qt.DisplayRole):
        if index.isValid():
            if role == Qt.DisplayRole:
                # Retorna el valor de la celda como texto
                return str(self._data.iloc[index.row(), index.column()])
        return None

    def headerData(self, col, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self._data.columns[col]
        return None

# Clase Canvas (Gráfico MatplotLib)
class MplCanvas(FigureCanvasQTAgg):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi,constrained_layout=True)
        self.axes = fig.add_subplot(111)
        super().__init__(fig)

    def plot_intervals(self, intervals):
        """
        Recibe la lista de diccionarios y dibuja las franjas con sus nombres.
        """
        for i in intervals:
            color_mpl = i["color"]
            y_min = i["start"]
            y_max = i["end"]
            texto = i["label"] # Ej: "Sin Restricción (NR)"
            
            # 1. Dibujar franja (Fondo)
            self.axes.axhspan(
                ymin=y_min,
                ymax=y_max,
                color=color_mpl,
                zorder=0 # Se asegura que quede al fondo
            )

            # 2. Dibujar Texto (Marca de agua)
            self.axes.text(
                x=0.99,                 # 99% del ancho (casi al borde derecho)
                y=(y_min + y_max) / 2,  # Altura: Justo en el medio de la franja
                s=texto,                # El texto a mostrar
                
                # --- ESTILO ---
                color='#333333',        # Gris oscuro (no negro puro)
                alpha=0.5,              # 50% transparente (tenue)
                fontsize=8,             # Letra chica
                fontstyle='italic',     # Cursiva
                ha='right',             # Alineado a la derecha
                va='center',            # Centrado verticalmente
                
                # Esto es clave: X es coordenadas de Eje (0-1), Y es valor real (0-100)
                transform=self.axes.get_yaxis_transform() 
            )

    def update_plot(self, x_data, y_data, y_data_2=None,
                     intervals_config=None,
                     index_label = 'Index',
                     sec_label   = 'var_2',
                     x_label     = 'x'):
        
        self.axes.cla()

        if hasattr(self, 'axes_right') and self.axes_right is not None:
            self.axes_right.remove()
            self.axes_right = None

        show_axis_2 = (y_data_2 is not None) and (sec_label != "Sin Eje Secundario")

        if show_axis_2:
            self.axes_right = self.axes.twinx()
            styled_name_sec=cfg.NAMES_CONC.get(sec_label,sec_label)
            unit_name_sec=cfg.UNITS_MAP.get(sec_label,"")

            if unit_name_sec and unit_name_sec != "":
                label_axis_right = f"{styled_name_sec} [{unit_name_sec}]"
            else:
                label_axis_right = styled_name_sec
        else:
            self.axes_right = None

        # Desactivar cursores que pueden llegar a estar activos
        if self.cursor is not None:
            try:
                self.cursor.remove()
            except Exception:
                pass 
            self.cursor = None
    

        max_limit = 100 # Valor por defecto

        if intervals_config:
            self.plot_intervals(intervals_config)
            # Buscamos el valor 'end' más alto en la configuración
            # Ej: Para IWQI será 100, para DWQI será 1000 (según config)
            max_limit = max(item['end'] for item in intervals_config)

        self.axes.set_xlabel(x_label, fontweight='bold')
        # GRAFICAR EJE IZQUIERDO (WQI)
        color_wqi = 'black' 
        # Se grafican y se capturan las lineas
        line_index,= self.axes.plot(x_data, y_data, color=color_wqi, marker='o', label=index_label)
        line_cursor = [line_index]

        self.axes.set_ylabel(index_label, color=color_wqi, fontweight='bold')
        self.axes.set_ylim(0, 100)
        self.axes.tick_params(axis='y', labelcolor=color_wqi) # Colorea los números del eje
        self.axes.grid(True, linestyle='--', alpha=0.5)

        if show_axis_2:
            color_sec = '#D35400' # Naranja
            
            # Notar que usamos 'axes_right' aquí
            line_sec, = self.axes_right.plot(x_data, y_data_2, color=color_sec, 
                                 marker='s', linestyle='--', label=styled_name_sec)
            line_cursor.append(line_sec)
            
            self.axes_right.set_ylabel(label_axis_right, color=color_sec, fontweight='bold')
            self.axes_right.tick_params(axis='y', labelcolor=color_sec) # Colorea los números
            self.axes_right.yaxis.set_label_position("right") 
            self.axes_right.yaxis.tick_right()

        self.cursor = mplcursors.cursor(line_cursor, hover=True)

        @self.cursor.connect("add")
        def on_add(sel):
            # OBTENER DATOS
            # sel.target[0] es X, sel.target[1] es Y
            x_val = sel.target[0] 
            y_val = sel.target[1]
            
            # Nombre de la serie (WQI, pH, etc.)
            label_line = sel.artist.get_label()


            try: x_txt = f"{int(x_val)}"
            except: x_txt = f"{x_val}"

            if unit_name_sec and unit_name_sec != "":
                txt_valor = f"Valor: {y_val:.2f} [{unit_name_sec}]"
            else:
                txt_valor = f"Valor: {y_val:.2f}"

            # TEXTO
            sel.annotation.set_text(f"{label_line}\n{x_label}: {int(x_txt)}\n{txt_valor}")

            # Tooltip
            sel.annotation.get_bbox_patch().set(
                fc="#34495E",       # Color de fondo (Azul oscuro)
                ec="none",          # Sin borde
                alpha=0.9,          # Transparencia
                boxstyle="round,pad=0.5" # Bordes redondeados y relleno interno
            )

            # DISEÑO DEL TEXTO
            sel.annotation.set(
                color="white",      # Letras blancas
                fontsize=9         # Tamaño 
            )

            # DISEÑO DE LA FLECHA
            sel.annotation.arrow_patch.set_visible(False)

        self.axes.relim()
        self.axes.autoscale_view()
        self.axes.set_ylim(0, max_limit) # Ajustar limites para ver todos los intervalos

        self.axes.xaxis.set_major_locator(MaxNLocator(integer=True))

        self.draw()

class PercentageCanvas(FigureCanvasQTAgg):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        # Configuración del lienzo
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)
        
        # Márgenes para que entren los textos
        #######self.fig.subplots_adjust(bottom=0.2, top=0.9, left=0.15, right=0.95)
        
        super(PercentageCanvas, self).__init__(self.fig)
        self.setParent(parent)
        self.axes.set_facecolor('white') 

    def update_chart(self, values, intervals_config):
        """
        Recibe los valores crudos y la configuración de intervalos.
        Calcula los porcentajes internamente y grafica.
        """
        self.axes.cla() # Limpiar gráfico anterior

        # Validación rápida
        if values is None or len(values) == 0 or not intervals_config:
            self.draw()
            return

        # ---------------------------------------------------------
        # 1. LÓGICA DE CÁLCULO (Lo que tenías armado)
        # ---------------------------------------------------------
        
        # A. Preparamos los contenedores ordenados según tu lista
        ids_categorias = [i['id'] for i in intervals_config] # ['NR', 'LR', 'MR', ...]
        conteo = {id_cat: 0 for id_cat in ids_categorias}
        colores_finales = []

        # B. Preparamos los colores (Quitamos la transparencia 0.3 para que se vean bien)
        for i in intervals_config:
            c = i['color']
            # Usamos R, G, B originales, pero Alpha en 0.9 (casi solido)
            colores_finales.append((c[0], c[1], c[2], 0.4))

        # C. Clasificación de cada muestra (Binning)
        # Recorremos cada valor de la lista de datos (IWQI)
        for val in values:
            for intervalo in intervals_config:
                # Tu lógica de intervalos: start <= valor <= end
                if intervalo['start'] <= val <= intervalo['end']:
                    conteo[intervalo['id']] += 1
                    break # Ya encontramos su categoría, pasamos al siguiente valor

        # D. Convertir a Porcentajes
        total = len(values)
        porcentajes = []
        for id_cat in ids_categorias:
            if total > 0:
                pct = (conteo[id_cat] / total) * 100
            else:
                pct = 0
            porcentajes.append(pct)

        # ---------------------------------------------------------
        # 2. GRAFICADO
        # ---------------------------------------------------------
        x_pos = np.arange(len(ids_categorias))
        
        # Dibujar barras
        barras = self.axes.bar(x_pos, porcentajes, 
                               color=colores_finales, 
                               edgecolor='black', 
                               width=0.6,
                               zorder=3) # zorder para que quede encima de la grilla

        # ---------------------------------------------------------
        # 3. ESTÉTICA
        # ---------------------------------------------------------
        self.axes.set_xticks(x_pos)
        self.axes.set_xticklabels(
            ids_categorias, 
            fontweight='light', 
            fontsize=7,           # Letra más chica
            ha='center'           # Alineación: Vital para que quede prolij
        )
        
        ########self.axes.set_ylabel('Porcentaje (%)', fontweight='bold')
        self.axes.set_ylabel('')    # Sin texto "Porcentaje"
        self.axes.set_yticks([])    # Sin números (0, 20, 40...)
        
        # Limpieza visual (estilo Tufte)
        self.axes.spines['top'].set_visible(False)
        self.axes.spines['right'].set_visible(False)
        self.axes.spines['left'].set_visible(False)
        self.axes.grid(axis='y', linestyle='--', alpha=0.4, zorder=0)


        # 4. Etiquetas de texto sobre las barras
        for bar in barras:
            height = bar.get_height()
            if height >= 0:
                self.axes.text(bar.get_x() + bar.get_width()/2., height + 1,
                               f'{height:.1f}%',
                               ha='center', va='bottom', 
                               fontsize=8, fontweight='light', color='#333333')
        self.fig.tight_layout()
        self.draw()