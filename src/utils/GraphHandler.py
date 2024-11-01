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
        
        # Configurar el color de las etiquetas y ejes para que sean visibles con fondo blanco
        for plot in [self.flow_time_plot, self.flow_pressure_plot]:
            plot.getAxis('bottom').setPen('k')
            plot.getAxis('left').setPen('k')
            plot.getAxis('bottom').setTextPen('k')
            plot.getAxis('left').setTextPen('k')
    
    def calibrate_time(self, time_value):
        """
        Calibra el tiempo relativo a partir del tiempo absoluto.
        
        Args:
            time_value (float): Valor de tiempo absoluto
            
        Returns:
            float: Valor de tiempo calibrado (relativo al tiempo inicial)
        """
        # Guardar el tiempo inicial en milisegundos si es el primer dato
        if self.initial_time is None:
            self.initial_time = time_value
        
        # Calcular tiempo relativo (en milisegundos)
        relative_time_ms = time_value - self.initial_time
        
        # Convertir a segundos
        relative_time_s = relative_time_ms / 1000.0
        
        return relative_time_s

        
    @Slot(dict)
    def update_data(self, new_data):
        """Actualizar los datos y gráficos"""
        # Guardar datos originales
        for key in ['t', 'p', 'f', 'v']:
            if key in new_data:
                self.data[key].append(new_data[key])
        
        # Calibrar tiempo y actualizar datos de visualización
        calibrated_time = self.calibrate_time(new_data['t'])
        self.display_data['t'].append(calibrated_time)
        
        # Actualizar otros datos de visualización
        for key in ['p', 'f', 'v']:
            if key in new_data:
                self.display_data[key].append(new_data[key])
                
        # Mantener solo los últimos 1000 puntos para visualización
        max_points = 1000
        for key in self.display_data:
            if len(self.display_data[key]) > max_points:
                self.display_data[key] = self.display_data[key][-max_points:]
        
        # Mantener los datos originales sin límite
        # (o implementar un límite mayor si es necesario)
                
        # Actualizar gráficos
        self.update_plots()
        
    def update_plots(self):
        """Actualizar ambos gráficos"""
        if len(self.display_data['t']) > 0:
            # Actualizar Flujo vs Tiempo
            self.flow_time_curve.setData(
                x=self.display_data['t'],
                y=self.display_data['v']
            )
            
            # Actualizar Flujo vs Presión
            self.flow_pressure_curve.setData(
                x=self.display_data['v'],
                y=self.display_data['f']
            )
    
    def clear_data(self):
        """Limpiar todos los datos"""
        # Limpiar datos originales
        for key in self.data:
            self.data[key] = []
            
        # Limpiar datos de visualización
        for key in self.display_data:
            self.display_data[key] = []
            
        # Resetear tiempo inicial
        self.initial_time = None
        
        # Actualizar gráficos
        self.update_plots()