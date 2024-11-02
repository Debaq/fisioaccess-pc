import pyqtgraph as pg
from PySide6.QtWidgets import QWidget, QHBoxLayout
from PySide6.QtCore import Slot
import numpy as np

class GraphHandler(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Configurar el layout principal
        self.layout = QHBoxLayout(self)
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        # Crear los gráficos
        self.setup_graphs()

        # minimos y maximos en el volumen
        self.min_max_vol = []
        
        # Datos originales para almacenamiento
        self.data = {
            't': [],
            'p': [],
            'f': [],
            'v': []
        }
        
        # Datos calibrados para visualización
        self.display_data = {
            't': [],
            'p': [],
            'f': [],
            'v': []
        }
        
        # Tiempo inicial para calibración
        self.initial_time = None
        
        # Configurar estilos de las curvas
        self.setup_curve_styles()

        # Agregar líneas verticales móviles
        self.setup_vertical_lines()

        self.graph_record = True
    
    def setup_graphs(self):
        """Configurar los widgets de gráficos"""
        # Crear dos widgets de gráficos separados
        self.flow_time_widget = pg.PlotWidget()
        self.flow_pressure_widget = pg.PlotWidget()
        
        # Configurar el gráfico Flujo vs Tiempo
        self.flow_time_plot = self.flow_time_widget.getPlotItem()
        self.flow_time_plot.setLabel('left', 'Volumen', 'ml')
        self.flow_time_plot.setLabel('bottom', 'Tiempo', 's')
        self.flow_time_plot.showGrid(x=True, y=True)
        
        # Establecer límites en el eje Y
        view_box = self.flow_time_plot.getViewBox()
        view_box.setLimits(yMin=-6000, yMax=6000)
        view_box.setYRange(0, 6000, padding=0)
        
        # Configurar el gráfico Flujo vs Presión
        self.flow_pressure_plot = self.flow_pressure_widget.getPlotItem()
        self.flow_pressure_plot.setLabel('left', 'Flujo', 'L/s')
        self.flow_pressure_plot.setLabel('bottom', 'Volumen', 'L')
        self.flow_pressure_plot.showGrid(x=True, y=True)
        
        # Configurar el fondo de los gráficos
        self.flow_time_widget.setBackground('w')
        self.flow_pressure_widget.setBackground('w')
        
        # Agregar los widgets al layout con la proporción correcta
        self.layout.addWidget(self.flow_time_widget, stretch=2)
        self.layout.addWidget(self.flow_pressure_widget, stretch=1)


    def setup_vertical_lines(self):
        """Configurar las líneas verticales móviles"""
        # Crear las líneas verticales para el gráfico Flujo vs Tiempo
        self.vLine1 = pg.InfiniteLine(
            pos=0, 
            angle=90, 
            movable=True,
            pen=pg.mkPen('r', width=2)
        )
        self.vLine2 = pg.InfiniteLine(
            pos=1, 
            angle=90, 
            movable=True,
            pen=pg.mkPen('g', width=2)
        )
        
        # Configurar los límites después de crear las líneas
        view_range = self.flow_time_plot.getViewBox().viewRange()
        self.vLine1.setBounds((None, None))  # Solo limitar movimiento horizontal si es necesario
        self.vLine2.setBounds((None, None))
        
        # Crear etiquetas para las líneas
        self.label1 = pg.TextItem(text='', color='r', anchor=(0, 1))
        self.label2 = pg.TextItem(text='', color='g', anchor=(0, 1))
        
        # Crear etiqueta para la diferencia
        self.diff_label = pg.TextItem(text='', color='b', anchor=(0, 0))
        
        # Agregar las líneas y etiquetas al gráfico
        self.flow_time_plot.addItem(self.vLine1)
        self.flow_time_plot.addItem(self.vLine2)
        self.flow_time_plot.addItem(self.label1)
        self.flow_time_plot.addItem(self.label2)
        self.flow_time_plot.addItem(self.diff_label)
        
        # Conectar señales para actualizar cuando las líneas se muevan
        self.vLine1.sigPositionChanged.connect(self.update_line_info)
        self.vLine2.sigPositionChanged.connect(self.update_line_info)

    def setup_curve_styles(self):
        """Configurar las curvas de los gráficos"""
        # Curva para Flujo vs Tiempo
        self.flow_time_curve = self.flow_time_plot.plot(
            pen=pg.mkPen('b', width=2)
        )
        
        # Curva para Flujo vs Presión
        self.flow_pressure_curve = self.flow_pressure_plot.plot(
            pen=pg.mkPen('r', width=2)
        )
        
        # Configurar el color de las etiquetas y ejes
        for plot in [self.flow_time_plot, self.flow_pressure_plot]:
            plot.getAxis('bottom').setPen('k')
            plot.getAxis('left').setPen('k')
            plot.getAxis('bottom').setTextPen('k')
            plot.getAxis('left').setTextPen('k')

    def get_y_value_at_x(self, x_pos):
        """Obtener el valor Y en la posición X de la curva"""
        if not self.display_data['t'] or not self.display_data['v']:
            return None

        x_data = np.array(self.display_data['t'])
        y_data = np.array(self.display_data['v'])

        # Verificar rango
        if x_pos < x_data[0] or x_pos > x_data[-1]:
            return None

        # Interpolación
        idx = np.searchsorted(x_data, x_pos)
        if idx > 0:
            x0, x1 = x_data[idx-1], x_data[idx]
            y0, y1 = y_data[idx-1], y_data[idx]
            
            if x1 == x0:
                return y0
                
            y_interp = y0 + (y1 - y0) * (x_pos - x0) / (x1 - x0)
            return y_interp

        return None

    def update_line_info(self):
        """Actualizar la información de las líneas"""
        try:
            # Obtener valores x
            x1 = self.vLine1.value()
            x2 = self.vLine2.value()
            
            # Obtener valores y
            y1 = self.get_y_value_at_x(x1)
            y2 = self.get_y_value_at_x(x2)

            # Actualizar etiquetas de líneas
            if y1 is not None:
                self.label1.setPos(x1, y1)
                self.label1.setText(f'X: {x1:.2f}\nY: {y1:.2f}')
            
            if y2 is not None:
                self.label2.setPos(x2, y2)
                self.label2.setText(f'X: {x2:.2f}\nY: {y2:.2f}')

            # Actualizar etiqueta de diferencia
            if y1 is not None and y2 is not None:
                x_diff = abs(x2 - x1)
                y_diff = abs(y2 - y1)
                x_mid = min(x1, x2) + x_diff/2
                y_position = self.flow_time_plot.getViewBox().viewRange()[1][1] * 0.9
                
                self.diff_label.setPos(x_mid, y_position)
                self.diff_label.setText(
                    f'ΔX: {x_diff:.2f} s\n'
                    f'ΔY: {y_diff:.2f} ml'
                )
        except Exception as e:
            print(f"Error actualizando líneas: {e}")

    def calibrate_time(self, time_value):
        """Calibrar el tiempo relativo"""
        if self.initial_time is None:
            self.initial_time = time_value
        return (time_value - self.initial_time) / 1000.0

    @Slot(dict)
    def update_data(self, new_data):
        """Actualizar los datos y gráficos"""
        if not self.graph_record:
            return

        try:
            # Actualizar datos
            for key in ['t', 'p', 'f', 'v']:
                if key in new_data:
                    self.data[key].append(new_data[key])

            # Actualizar datos de visualización
            self.display_data['t'].append(self.calibrate_time(new_data['t']))
            for key in ['p', 'f', 'v']:
                if key in new_data:
                    self.display_data[key].append(new_data[key])

            # Mantener solo los últimos 1000 puntos
            max_points = 1000
            for key in self.display_data:
                if len(self.display_data[key]) > max_points:
                    self.display_data[key] = self.display_data[key][-max_points:]

            # Actualizar gráficos
            self.update_plots()

        except Exception as e:
            print(f"Error en update_data: {e}")

    def update_plots(self):
        """Actualizar ambos gráficos"""
        self.max_value_f_v()
        if len(self.display_data['t']) > 0:
            self.flow_time_curve.setData(
                x=self.display_data['t'],
                y=self.display_data['v']
            )
            self.flow_pressure_curve.setData(
                x=self.display_data['v'],
                y=self.display_data['f']
            )
            self.update_line_info()

    def clear_data(self):
        """Limpiar todos los datos"""
        for key in self.data:
            self.data[key] = []
        for key in self.display_data:
            self.display_data[key] = []
            
        self.initial_time = None
        self.update_plots()
        
        self.vLine1.setValue(0)
        self.vLine2.setValue(1)
        self.label1.setText('')
        self.label2.setText('')
        self.diff_label.setText('')
        
        self.graph_record = True

    def stop_record(self):
        self.graph_record = False

    def max_value_f_v(self):
        if self.display_data['v'] and isinstance(self.display_data['v'], list):
            max_value = max(self.display_data['v'])
            min_value = min(self.display_data['v'])
            self.min_max_vol = [min_value, max_value]