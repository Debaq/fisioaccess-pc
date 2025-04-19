import pyqtgraph as pg
from PySide6.QtCore import Slot
import numpy as np

from utils.BaseGraphManager import BaseGraphManager, DataManager

class SpirometryGraphManager(BaseGraphManager):
    """
    Gestor de gráficos específico para la visualización de datos de espirometría.
    """
    def setup_data_manager(self):
        """Inicializa el gestor de datos con los tipos específicos para espirometría"""
        self.data_manager = DataManager(['t', 'p', 'f', 'v'])
        # Almacenar min/max de volumen como metadatos
        self.data_manager.metadata['min_max_vol'] = []

    def setup_graphs(self):
        """Configurar los widgets de gráficos para espirometría"""
        # Crear dos widgets de gráficos separados
        self.flow_time_widget = pg.PlotWidget()
        self.flow_pressure_widget = pg.PlotWidget()
        
        # Configurar el gráfico Volumen vs Tiempo
        self.flow_time_plot = self.flow_time_widget.getPlotItem()
        self.flow_time_plot.setLabel('left', 'Volumen', 'L')
        self.flow_time_plot.setLabel('bottom', 'Tiempo', 's')
        self.flow_time_plot.showGrid(x=True, y=True)
        
        # Establecer límites en el eje Y
        view_box = self.flow_time_plot.getViewBox()
        view_box.setLimits(yMin=-6000, yMax=6000)
        view_box.setYRange(0, 6000, padding=0)
        
        # Configurar el gráfico Flujo vs Volumen
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
        """Configurar las curvas de los gráficos para espirometría"""
        # Curva para Volumen vs Tiempo
        self.flow_time_curve = self.flow_time_plot.plot(
            pen=pg.mkPen('b', width=2)
        )
        
        # Curva para Flujo vs Volumen
        self.flow_pressure_curve = self.flow_pressure_plot.plot(
            pen=pg.mkPen('r', width=2)
        )
        
        # Configurar el color de las etiquetas y ejes
        for plot in [self.flow_time_plot, self.flow_pressure_plot]:
            plot.getAxis('bottom').setPen('k')
            plot.getAxis('left').setPen('k')
            plot.getAxis('bottom').setTextPen('k')
            plot.getAxis('left').setTextPen('k')

    def setup_markers(self):
        """Configurar las líneas verticales móviles y etiquetas para espirometría"""
        # Crear las líneas verticales para el gráfico Volumen vs Tiempo
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

    def update_line_info(self):
        """Actualizar la información de las líneas marcadoras"""
        try:
            # Obtener valores x
            x1 = self.vLine1.value()
            x2 = self.vLine2.value()
            
            # Obtener valores y (volumen)
            y1 = self.data_manager.get_y_value_at_x('t', 'v', x1)
            y2 = self.data_manager.get_y_value_at_x('t', 'v', x2)

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
                    f'ΔY: {y_diff:.2f} L'
                )
        except Exception as e:
            print(f"Error actualizando líneas: {e}")

    def update_plots(self):
        """Actualizar ambos gráficos de espirometría"""
        self.update_min_max_vol()
        
        if len(self.data_manager.display_data['t']) > 0:
            # Actualizar gráfico Volumen vs Tiempo
            self.flow_time_curve.setData(
                x=self.data_manager.display_data['t'],
                y=self.data_manager.display_data['v']
            )
            
            # Actualizar gráfico Flujo vs Volumen
            self.flow_pressure_curve.setData(
                x=self.data_manager.display_data['v'],
                y=self.data_manager.display_data['f']
            )
            
            # Actualizar información de las líneas
            self.update_line_info()

    def update_min_max_vol(self):
        """Actualizar los valores mínimo y máximo de volumen"""
        min_vol, max_vol = self.data_manager.get_min_max('v')
        if min_vol is not None and max_vol is not None:
            self.data_manager.metadata['min_max_vol'] = [min_vol, max_vol]

    def reset_markers(self):
        """Restablecer los marcadores a su posición inicial"""
        self.vLine1.setValue(0)
        self.vLine2.setValue(1)
        self.label1.setText('')
        self.label2.setText('')
        self.diff_label.setText('')
