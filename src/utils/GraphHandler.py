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
        # Crear layout para los gráficos
        graph_layout = pg.GraphicsLayoutWidget()
        
        # Gráfico Flujo vs Tiempo (2/3 del ancho)
        self.flow_time_plot = graph_layout.addPlot()
        self.flow_time_plot.setLabel('left', 'Flujo', 'L/s')
        self.flow_time_plot.setLabel('bottom', 'Tiempo', 's')
        self.flow_time_plot.showGrid(x=True, y=True)
        
        # Agregar algo de espacio entre los gráficos
        graph_layout.nextColumn()
        
        # Gráfico Flujo vs Presión (1/3 del ancho)
        self.flow_pressure_plot = graph_layout.addPlot()
        self.flow_pressure_plot.setLabel('left', 'Flujo', 'L/s')
        self.flow_pressure_plot.setLabel('bottom', 'Presión', 'Kpa')
        self.flow_pressure_plot.showGrid(x=True, y=True)
        
        # Configurar las proporciones de los gráficos (2:1)
        graph_layout.ci.layout.setColumnStretchFactor(0, 2)
        graph_layout.ci.layout.setColumnStretchFactor(1, 1)
        
        # Agregar el layout de gráficos al layout principal
        self.layout.addWidget(graph_layout)
        
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