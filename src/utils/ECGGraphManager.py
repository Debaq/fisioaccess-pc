import pyqtgraph as pg
from PySide6.QtCore import Slot
import numpy as np

from utils.BaseGraphManager import BaseGraphManager, DataManager

class ECGGraphManager(BaseGraphManager):
    """
    Gestor de gráficos específico para la visualización de datos de electrocardiograma (ECG).
    """
    def __init__(self, parent=None):
        # Definir constantes para los límites del ROI
        self.LIMIT_MIN = 0
        self.LIMIT_MAX = 60
        # Tamaño inicial del ROI (en segundos)
        self.roi_size = 5
        # Llamar al constructor de la clase base después de definir las constantes
        super().__init__(parent, layout_type='vertical')

    def setup_data_manager(self):
        """Inicializa el gestor de datos con configuración mínima para ECG"""
        # Por defecto solo gestionamos tiempo y una derivación
        self.data_manager = DataManager(['t', 'ecg'])
        # Metadatos específicos para ECG
        self.data_manager.metadata['qrs_intervals'] = []
        self.data_manager.metadata['heart_rate'] = 0

    def setup_graphs(self):
        """Configurar los widgets de gráficos para ECG"""
        # Crear el widget principal para el ECG
        self.ecg_widget = pg.PlotWidget()
        
        # Configurar el gráfico ECG vs Tiempo
        self.ecg_plot = self.ecg_widget.getPlotItem()
        self.ecg_plot.setLabel('left', 'Amplitud', 'mV')
        self.ecg_plot.setLabel('bottom', 'Tiempo', 's')
        self.ecg_plot.showGrid(x=True, y=True)
        
        # Establecer límites en el eje Y
        view_box = self.ecg_plot.getViewBox()
        view_box.setLimits(yMin=-3, yMax=3)  # Valores típicos para ECG en mV
        view_box.setYRange(-2, 2, padding=0)
        
        # Configurar el fondo del gráfico
        self.ecg_widget.setBackground('w')
        
        # Widget para el ritmo continuo
        self.rhythm_widget = pg.PlotWidget()
        self.rhythm_plot = self.rhythm_widget.getPlotItem()
        self.rhythm_plot.setLabel('left', 'ECG', 'mV')
        self.rhythm_plot.setLabel('bottom', 'Tiempo', 's')
        self.rhythm_plot.showGrid(x=True, y=True)
        self.rhythm_widget.setBackground('w')
        self.rhythm_plot.setXRange(0, self.LIMIT_MAX)
        
        # Reducir el margen para la etiqueta y del gráfico de ritmo
        self.rhythm_plot.getAxis('left').setWidth(40)
        
        # Configurar layout para mostrar el gráfico de ritmo debajo del ECG principal
        self.layout.addWidget(self.ecg_widget, stretch=7)
        self.layout.addWidget(self.rhythm_widget, stretch=3)
        
        # Añadir ROI al gráfico de ritmo
        self.setup_roi()

    def setup_roi(self):
        """Configurar la región de interés (ROI) en el gráfico de ritmo como un intervalo de tamaño fijo"""
        # Crear un LinearRegionItem (región seleccionable)
        self.roi = pg.LinearRegionItem()
        self.roi.setZValue(10)  # Asegurar que esté por encima de las curvas
        
        # Configurar colores para que sea visible con el fondo blanco
        self.roi.setBrush(pg.mkBrush(color=(100, 100, 255, 50)))
        self.roi.setRegion([0, self.roi_size])  # Valores iniciales
        
        # Establecer límites para el ROI
        self.roi.setBounds([self.LIMIT_MIN, self.LIMIT_MAX])
        
        # Añadir ROI al gráfico de ritmo
        self.rhythm_plot.addItem(self.roi)
        
        # Deshabilitar la capacidad de redimensionar el ROI modificando su implementación interna
        # Esto hace que los bordes no sean interactivos, solo se puede mover como unidad
        for line in self.roi.lines:
            line.setMovable(False)
        
        # Conectar la señal de cambio de región para monitorear movimientos del ROI
        self.roi.sigRegionChanged.connect(self.maintain_roi_size)
        self.roi.sigRegionChanged.connect(self.update_roi)

    def maintain_roi_size(self):
        """Asegura que el ROI mantenga un tamaño fijo al ser movido"""
        min_x, max_x = self.roi.getRegion()
        current_size = max_x - min_x
        
        # Si el tamaño ha cambiado (por alguna razón), restaurarlo
        if abs(current_size - self.roi_size) > 0.001:  # Pequeña tolerancia para errores de coma flotante
            # Calcular el punto medio
            mid_point = (min_x + max_x) / 2
            
            # Calcular los nuevos límites manteniendo el punto medio
            new_min = mid_point - self.roi_size / 2
            new_max = mid_point + self.roi_size / 2
            
            # Asegurar que los límites están dentro del rango permitido
            if new_min < self.LIMIT_MIN:
                new_min = self.LIMIT_MIN
                new_max = new_min + self.roi_size
            elif new_max > self.LIMIT_MAX:
                new_max = self.LIMIT_MAX
                new_min = new_max - self.roi_size
            
            # Establecer la nueva región sin activar esta misma función (para evitar recursión)
            self.roi.blockSignals(True)
            self.roi.setRegion([new_min, new_max])
            self.roi.blockSignals(False)

    def set_size_roi(self, size_seconds):
        """
        Establece el tamaño del ROI en segundos
        
        Args:
            size_seconds (float): Tamaño del ROI en segundos
        """
        # Validar tamaño
        if size_seconds <= 0:
            print("El tamaño del ROI debe ser positivo")
            return
        
        # Limitar el tamaño máximo al rango disponible
        if size_seconds > self.LIMIT_MAX - self.LIMIT_MIN:
            size_seconds = self.LIMIT_MAX - self.LIMIT_MIN
            print(f"Tamaño del ROI limitado a {size_seconds} segundos")
        
        # Guardar el nuevo tamaño
        self.roi_size = size_seconds
        
        # Obtener la posición actual del ROI
        min_x, max_x = self.roi.getRegion()
        mid_point = (min_x + max_x) / 2
        
        # Calcular los nuevos límites manteniendo el punto medio
        new_min = mid_point - size_seconds / 2
        new_max = mid_point + size_seconds / 2
        
        # Asegurar que los límites están dentro del rango permitido
        if new_min < self.LIMIT_MIN:
            new_min = self.LIMIT_MIN
            new_max = new_min + size_seconds
        elif new_max > self.LIMIT_MAX:
            new_max = self.LIMIT_MAX
            new_min = new_max - size_seconds
        
        # Establecer la nueva región
        self.roi.blockSignals(True)
        self.roi.setRegion([new_min, new_max])
        self.roi.blockSignals(False)
        
        # Actualizar el gráfico principal
        self.update_roi()

    def update_roi(self):
        """Actualizar el gráfico principal cuando cambia la ROI"""
        # Obtener los límites de la región seleccionada
        min_x, max_x = self.roi.getRegion()
        
        # Aplicar esos límites al gráfico principal
        self.ecg_plot.setXRange(min_x, max_x, padding=0)

    def setup_curve_styles(self):
        """Configurar las curvas de los gráficos para ECG"""
        # Por defecto solo tenemos una derivación
        self.leads = ['ecg']
        self.lead_colors = ['r']
        
        # Derivación activa (por defecto la única disponible)
        self.active_lead = 'ecg'
        
        # Curva principal para la derivación activa
        self.ecg_curve = self.ecg_plot.plot(
            pen=pg.mkPen('r', width=2)
        )
        
        # Curva para el ritmo (misma derivación)
        self.rhythm_curve = self.rhythm_plot.plot(
            pen=pg.mkPen('b', width=2)
        )
        
        # Configurar el color de las etiquetas y ejes
        for plot in [self.ecg_plot, self.rhythm_plot]:
            plot.getAxis('bottom').setPen('k')
            plot.getAxis('left').setPen('k')
            plot.getAxis('bottom').setTextPen('k')
            plot.getAxis('left').setTextPen('k')

    def setup_markers(self):
        """Configurar los marcadores para ECG"""
        # Crear las líneas verticales para marcar intervalos
        self.qrs_line1 = pg.InfiniteLine(
            pos=0, 
            angle=90, 
            movable=True,
            pen=pg.mkPen('r', width=2)
        )
        self.qrs_line2 = pg.InfiniteLine(
            pos=1, 
            angle=90, 
            movable=True,
            pen=pg.mkPen('g', width=2)
        )
        
        # Línea horizontal para el nivel de base
        self.baseline = pg.InfiniteLine(
            pos=0, 
            angle=0, 
            movable=True,
            pen=pg.mkPen('b', width=1, style=pg.QtCore.Qt.DashLine)
        )
        
        # Configurar los límites
        self.qrs_line1.setBounds((None, None))
        self.qrs_line2.setBounds((None, None))
        
        # Crear etiquetas para los intervalos
        self.qrs_label = pg.TextItem(text='', color='r', anchor=(0.5, 0))
        self.hr_label = pg.TextItem(text='', color='g', anchor=(0, 0))
        
        # Agregar las líneas y etiquetas al gráfico
        self.ecg_plot.addItem(self.qrs_line1)
        self.ecg_plot.addItem(self.qrs_line2)
        self.ecg_plot.addItem(self.baseline)
        self.ecg_plot.addItem(self.qrs_label)
        self.ecg_plot.addItem(self.hr_label)
        
        # Conectar señales para actualizar cuando las líneas se muevan
        self.qrs_line1.sigPositionChanged.connect(self.update_interval_info)
        self.qrs_line2.sigPositionChanged.connect(self.update_interval_info)

    def update_interval_info(self):
        """Actualizar la información de los intervalos QRS"""
        try:
            # Obtener valores x (tiempos)
            x1 = self.qrs_line1.value()
            x2 = self.qrs_line2.value()
            
            # Calcular intervalo RR en segundos
            rr_interval = abs(x2 - x1)
            
            # Calcular frecuencia cardíaca a partir del intervalo RR
            if rr_interval > 0:
                heart_rate = 60 / rr_interval  # HR = 60 / RR (en segundos)
            else:
                heart_rate = 0
            
            # Actualizar metadatos
            self.data_manager.metadata['heart_rate'] = heart_rate
            
            # Verificar que la derivación activa existe
            if self.active_lead in self.data_manager.display_data:
                # Obtener valores y (amplitud)
                y1 = self.data_manager.get_y_value_at_x('t', self.active_lead, x1)
                y2 = self.data_manager.get_y_value_at_x('t', self.active_lead, x2)
                
                # Posicionar etiquetas
                x_mid = min(x1, x2) + rr_interval/2
                y_position = self.ecg_plot.getViewBox().viewRange()[1][1] * 0.9
                
                # Actualizar etiquetas
                self.qrs_label.setPos(x_mid, y_position)
                self.qrs_label.setText(
                    f'RR: {rr_interval*1000:.0f} ms\n'
                    f'HR: {heart_rate:.0f} bpm'
                )
                
                # Actualizar etiqueta de frecuencia cardíaca en la esquina
                self.hr_label.setPos(self.ecg_plot.getViewBox().viewRange()[0][0], 
                                    self.ecg_plot.getViewBox().viewRange()[1][1] * 0.8)
                self.hr_label.setText(f'Heart Rate: {heart_rate:.0f} bpm')
            
        except Exception as e:
            print(f"Error actualizando intervalos: {e}")

    def update_plots(self):
        """Actualizar los gráficos de ECG"""
        if len(self.data_manager.display_data['t']) > 0:
            # Actualizar gráfico principal con la derivación activa
            self.ecg_curve.setData(
                x=self.data_manager.display_data['t'],
                y=self.data_manager.display_data[self.active_lead]
            )
            
            # Actualizar gráfico de ritmo con la misma derivación
            self.rhythm_curve.setData(
                x=self.data_manager.display_data['t'],
                y=self.data_manager.display_data[self.active_lead]
            )
            
            # Actualizar información de los intervalos
            self.update_interval_info()

    def set_leads(self, lead_names):
        """
        Configura las derivaciones disponibles
        
        Args:
            lead_names (list): Lista de nombres de derivaciones
        """
        # Verificar que exista al menos una derivación
        if not lead_names:
            return
            
        # Actualizar gestor de datos con las nuevas derivaciones
        old_data_types = list(self.data_manager.data.keys())
        new_data_types = ['t'] + lead_names
        
        # Crear nuevo gestor de datos con las derivaciones especificadas
        new_data_manager = DataManager(new_data_types)
        
        # Copiar datos existentes si es posible
        for key in old_data_types:
            if key in new_data_types:
                new_data_manager.data[key] = self.data_manager.data[key].copy()
                new_data_manager.display_data[key] = self.data_manager.display_data[key].copy()
        
        # Copiar metadatos
        new_data_manager.metadata = self.data_manager.metadata.copy()
        new_data_manager.initial_time = self.data_manager.initial_time
        new_data_manager.record = self.data_manager.record
        
        # Reemplazar el gestor de datos
        self.data_manager = new_data_manager
        
        # Actualizar lista de derivaciones
        self.leads = lead_names
        
        # Asignar colores
        default_colors = ['r', 'g', 'b', 'c', 'm', 'y']
        self.lead_colors = default_colors[:len(lead_names)]
        
        # Establecer la primera derivación como activa
        self.set_active_lead(lead_names[0])
        
    def set_active_lead(self, lead_name):
        """
        Cambia la derivación activa que se muestra en el gráfico principal
        
        Args:
            lead_name (str): Nombre de la derivación
        """
        if lead_name in self.leads and lead_name in self.data_manager.display_data:
            self.active_lead = lead_name
            self.update_plots()
            
            # Actualizar etiqueta del eje Y
            self.ecg_plot.setLabel('left', lead_name.replace('_', ' '), 'mV')

    def reset_markers(self):
        """Restablecer los marcadores a su posición inicial"""
        self.qrs_line1.setValue(0)
        self.qrs_line2.setValue(1)
        self.baseline.setValue(0)
        self.qrs_label.setText('')
        self.hr_label.setText('Heart Rate: -- bpm')
        
        # Restablecer ROI
        if hasattr(self, 'roi'):
            # Establecer ROI al inicio pero manteniendo su tamaño
            self.roi.blockSignals(True)
            self.roi.setRegion([0, self.roi_size])
            self.roi.blockSignals(False)
            self.update_roi()