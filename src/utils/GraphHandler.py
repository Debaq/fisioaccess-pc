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
        
        # Datos para los gráficos
        self.data = {
            't': [],
            'p': [],
            'f': [],
            'v': []
        }
        
        # Configurar estilos de las curvas
        self.setup_curve_styles()
        
    def setup_graphs(self):
        """Configurar los widgets de gráficos"""
        # Crear dos widgets de gráficos separados
        self.flow_time_widget = pg.PlotWidget()
        self.flow_pressure_widget = pg.PlotWidget()
        
        # Configurar el gráfico Flujo vs Tiempo
        self.flow_time_plot = self.flow_time_widget.getPlotItem()
        self.flow_time_plot.setLabel('left', 'Flujo', 'L/s')
        self.flow_time_plot.setLabel('bottom', 'Tiempo', 's')
        self.flow_time_plot.showGrid(x=True, y=True)
        
        # Configurar el gráfico Flujo vs Presión
        self.flow_pressure_plot = self.flow_pressure_widget.getPlotItem()
        self.flow_pressure_plot.setLabel('left', 'Flujo', 'L/s')
        self.flow_pressure_plot.setLabel('bottom', 'Presión', 'Kpa')
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
        
    @Slot(dict)
    def update_data(self, new_data):
        """Actualizar los datos y gráficos"""
        # Agregar nuevos datos
        for key in ['t', 'p', 'f', 'v']:
            if key in new_data:
                self.data[key].append(new_data[key])
                
        # Mantener solo los últimos 1000 puntos
        max_points = 1000
        for key in self.data:
            if len(self.data[key]) > max_points:
                self.data[key] = self.data[key][-max_points:]
                
        # Actualizar gráficos
        self.update_plots()
        
    def update_plots(self):
        """Actualizar ambos gráficos"""
        if len(self.data['t']) > 0:
            # Actualizar Flujo vs Tiempo
            self.flow_time_curve.setData(
                x=self.data['t'],
                y=self.data['f']
            )
            
            # Actualizar Flujo vs Presión
            self.flow_pressure_curve.setData(
                x=self.data['p'],
                y=self.data['f']
            )
            
    def clear_data(self):
        """Limpiar todos los datos"""
        for key in self.data:
            self.data[key] = []
        self.update_plots()