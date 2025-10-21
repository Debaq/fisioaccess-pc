import pyqtgraph as pg
from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QListWidget, QLabel, QFrame
from PySide6.QtCore import Slot, Signal, Qt
from PySide6.QtGui import QFont
import numpy as np

class GraphHandler(QWidget):
    # Señal para notificar nueva grabación
    new_recording_created = Signal(int, dict)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Layout principal horizontal
        self.main_layout = QHBoxLayout(self)
        self.main_layout.setSpacing(5)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Crear secciones
        self.setup_graphs_section()
        self.setup_results_section()

        # Datos para visualización actual
        self.display_data = {
            't': [],
            'p': [],
            'f': [],
            'v': []
        }

        # Variables de grabación
        self.recording_started = False
        self.start_time = None
        self.recording_count = 0
        self.max_recordings = 9
        self.recording_duration = 6.0
        self.ready_for_new_recording = False
        
        # Almacenar todas las grabaciones
        self.stored_recordings = []
        self.recording_colors = ['b', 'r', 'g', 'm', 'c', 'y', 'orange', 'purple', 'brown', 'pink']
        
        # Curvas para grabaciones almacenadas
        self.stored_curves = []
        
        # Curva activa
        self.active_recording_number = None
        
        # Diccionario para guardar posiciones de líneas por grabación
        self.line_positions = {}

        # Configurar estilos de las curvas
        self.setup_curve_styles()
        
        # Agregar líneas verticales
        self.setup_vertical_lines()

        self.graph_record = True
    
    def setup_graphs_section(self):
        """Configurar sección de gráficos (centro)"""
        graphs_layout = QHBoxLayout()
        graphs_layout.setSpacing(5)
        
        # Gráfico izquierdo: Volumen vs Tiempo
        self.flow_time_widget = pg.PlotWidget()
        self.flow_time_plot = self.flow_time_widget.getPlotItem()
        self.flow_time_plot.setLabel('left', 'Volumen', 'L')
        self.flow_time_plot.setLabel('bottom', 'Tiempo', 's')
        self.flow_time_plot.showGrid(x=True, y=True)
        
        grafico_volumen_tiempo_x = 17
        grafico_volumen_tiempo_y = 6
        self.flow_time_plot.setXRange(0, grafico_volumen_tiempo_x, padding=0)
        self.flow_time_plot.setYRange(-4, grafico_volumen_tiempo_y, padding=0)
        self.flow_time_plot.getViewBox().setLimits(xMin=0, xMax=grafico_volumen_tiempo_x, yMin=-4, yMax=grafico_volumen_tiempo_y)
        self.flow_time_plot.getViewBox().setMouseEnabled(x=False, y=False)
        self.flow_time_widget.setBackground('w')
        
        # Gráfico derecho: Flujo vs Volumen
        self.flow_pressure_widget = pg.PlotWidget()
        self.flow_pressure_plot = self.flow_pressure_widget.getPlotItem()
        self.flow_pressure_plot.setLabel('left', 'Flujo', 'L/s')
        self.flow_pressure_plot.setLabel('bottom', 'Volumen', 'L')
        self.flow_pressure_plot.showGrid(x=True, y=True)
        
        grafico_flujo_volumen_x = 8
        grafico_flujo_volumen_y = 10
        self.flow_pressure_plot.setXRange(0, grafico_flujo_volumen_x, padding=0)
        self.flow_pressure_plot.setYRange(-10, grafico_flujo_volumen_y, padding=0)
        self.flow_pressure_plot.getViewBox().setLimits(xMin=-8, xMax=grafico_flujo_volumen_x, yMin=-10, yMax=grafico_flujo_volumen_y)
        self.flow_pressure_plot.getViewBox().setMouseEnabled(x=False, y=False)
        self.flow_pressure_widget.setBackground('w')
        
        # Agregar gráficos al layout
        graphs_layout.addWidget(self.flow_time_widget, stretch=2)
        graphs_layout.addWidget(self.flow_pressure_widget, stretch=1)
        
        self.main_layout.addLayout(graphs_layout, stretch=3)
    
    def setup_results_section(self):
        """Configurar sección de resultados (derecha)"""
        results_frame = QFrame()
        results_frame.setFrameShape(QFrame.StyledPanel)
        results_frame.setMaximumWidth(250)
        results_frame.setMinimumWidth(200)
        
        results_layout = QVBoxLayout(results_frame)
        results_layout.setSpacing(5)
        results_layout.setContentsMargins(5, 5, 5, 5)
        
        # Título
        title_label = QLabel("Resultados")
        title_font = QFont()
        title_font.setBold(True)
        title_font.setPointSize(12)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        results_layout.addWidget(title_label)
        
        # Separador
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        results_layout.addWidget(line)
        
        # Lista de resultados
        self.results_list = QListWidget()
        self.results_list.setFont(QFont("Monospace", 10))
        results_layout.addWidget(self.results_list)
        
        # Agregar valores iniciales
        self.update_results_display()
        
        self.main_layout.addWidget(results_frame, stretch=1)
    
    def setup_vertical_lines(self):
        """Configurar las líneas verticales - 5 líneas en total"""
        # Gráfico izquierdo: solo FEV1 (líneas 1 y 2)
        self.vLine1 = pg.InfiniteLine(
            pos=0.5, 
            angle=90, 
            movable=True,
            pen=pg.mkPen('r', width=2),
            bounds=(0, 16),
            label="1",
            labelOpts={
                "position": 0.95,
                "color": (255, 0, 0),
                "fill": (255, 255, 255, 200)
            }
        )
        self.vLine1.setZValue(10)
        
        self.vLine2 = pg.InfiniteLine(
            pos=1.5, 
            angle=90, 
            movable=True,
            pen=pg.mkPen('g', width=2),
            bounds=(0, 16),
            label="2",
            labelOpts={
                "position": 0.95,
                "color": (0, 255, 0),
                "fill": (255, 255, 255, 200)
            }
        )
        self.vLine2.setZValue(10)
        
        # Gráfico derecho: 5 líneas compartidas
        # 1. PEF - solo espiratoria
        self.v_line_pef = pg.InfiniteLine(
            pos=0, 
            angle=90, 
            movable=True,
            pen=pg.mkPen('b', width=2),
            bounds=(0, 7),
            label="PEF",
            labelOpts={
                "position": 0.95,
                "color": (0, 0, 255),
                "fill": (255, 255, 255, 200)
            }
        )
        self.v_line_pef.setZValue(10)

        # 2. FEF25/FIF25 - compartida
        self.v_line_fef25 = pg.InfiniteLine(
            pos=1, 
            angle=90, 
            movable=False,
            pen=pg.mkPen('r', width=2),
            bounds=(0, 7),
            label="25%",
            labelOpts={
                "position": 0.5,
                "color": (255, 0, 0),
                "fill": (255, 255, 255, 200)
            }
        )
        self.v_line_fef25.setZValue(10)

        # 3. FEF50/FIF50 - compartida
        self.v_line_fef50 = pg.InfiniteLine(
            pos=2, 
            angle=90, 
            movable=False,
            pen=pg.mkPen('g', width=2),
            bounds=(0, 7),
            label="50%",
            labelOpts={
                "position": 0.5,
                "color": (0, 255, 0),
                "fill": (255, 255, 255, 200)
            }
        )
        self.v_line_fef50.setZValue(10)

        # 4. FEF75/FIF75 - compartida
        self.v_line_fef75 = pg.InfiniteLine(
            pos=3, 
            angle=90, 
            movable=False,
            pen=pg.mkPen('m', width=2),
            bounds=(0, 7),
            label="75%",
            labelOpts={
                "position": 0.5,
                "color": (255, 0, 255),
                "fill": (255, 255, 255, 200)
            }
        )
        self.v_line_fef75.setZValue(10)

        # 5. FVC - solo espiratoria
        self.v_line_fvc = pg.InfiniteLine(
            pos=4, 
            angle=90, 
            movable=True,
            pen=pg.mkPen('orange', width=2),
            bounds=(0, 7),
            label="FVC",
            labelOpts={
                "position": 0.95,
                "color": (255, 165, 0),
                "fill": (255, 255, 255, 200)
            }
        )
        self.v_line_fvc.setZValue(10)
        
        # Agregar líneas a los gráficos
        self.flow_time_plot.addItem(self.vLine1)
        self.flow_time_plot.addItem(self.vLine2)
        
        self.flow_pressure_plot.addItem(self.v_line_pef)
        self.flow_pressure_plot.addItem(self.v_line_fef25)
        self.flow_pressure_plot.addItem(self.v_line_fef50)
        self.flow_pressure_plot.addItem(self.v_line_fef75)
        self.flow_pressure_plot.addItem(self.v_line_fvc)
        
        # Conectar señales
        self.vLine1.sigPositionChanged.connect(self.update_results_display)
        self.vLine2.sigPositionChanged.connect(self.update_results_display)
        self.v_line_pef.sigPositionChanged.connect(self.update_fef_lines)
        self.v_line_fvc.sigPositionChanged.connect(self.update_fef_lines)

    def get_flow_at_volume(self, volume_pos):
        """Obtener el valor de flujo en una posición de volumen específica"""
        if not self.display_data['v'] or not self.display_data['f']:
            return None

        v_data = np.array(self.display_data['v'])
        f_data = np.array(self.display_data['f'])

        if volume_pos < v_data.min() or volume_pos > v_data.max():
            return None

        idx = np.searchsorted(v_data, volume_pos)
        if idx > 0 and idx < len(v_data):
            v0, v1 = v_data[idx-1], v_data[idx]
            f0, f1 = f_data[idx-1], f_data[idx]
            
            if v1 == v0:
                return f0
                
            f_interp = f0 + (f1 - f0) * (volume_pos - v0) / (v1 - v0)
            return f_interp

        return None

    def get_flow_intersections_at_volume(self, volume_pos):
        """
        Obtener ambas intersecciones de flujo (positiva y negativa) en una posición de volumen.
        Retorna (flujo_positivo, flujo_negativo) o (None, None) si no hay datos
        """
        if not self.display_data['v'] or not self.display_data['f']:
            return None, None

        v_data = np.array(self.display_data['v'])
        f_data = np.array(self.display_data['f'])

        # Encontrar todas las intersecciones cercanas a este volumen
        intersections = []
        tolerance = 0.05  # Tolerancia para considerar el mismo volumen
        
        for i in range(1, len(v_data)):
            # Si el volumen está entre v[i-1] y v[i]
            if min(v_data[i-1], v_data[i]) <= volume_pos <= max(v_data[i-1], v_data[i]):
                # Interpolar el flujo
                if v_data[i] != v_data[i-1]:
                    t = (volume_pos - v_data[i-1]) / (v_data[i] - v_data[i-1])
                    flow_interp = f_data[i-1] + t * (f_data[i] - f_data[i-1])
                    intersections.append(flow_interp)
        
        if not intersections:
            return None, None
        
        # Separar en positivos y negativos
        positive_flows = [f for f in intersections if f > 0]
        negative_flows = [f for f in intersections if f < 0]
        
        # Tomar el máximo positivo y el mínimo negativo (más negativo)
        flow_positive = max(positive_flows) if positive_flows else None
        flow_negative = min(negative_flows) if negative_flows else None
        
        return flow_positive, flow_negative

    def setup_curve_styles(self):
        """Configurar las curvas de los gráficos"""
        self.flow_time_curve = self.flow_time_plot.plot(pen=pg.mkPen('b', width=3))
        self.flow_pressure_curve = self.flow_pressure_plot.plot(pen=pg.mkPen('r', width=3))
        
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

        if x_pos < x_data[0] or x_pos > x_data[-1]:
            return None

        idx = np.searchsorted(x_data, x_pos)
        if idx > 0 and idx < len(x_data):
            x0, x1 = x_data[idx-1], x_data[idx]
            y0, y1 = y_data[idx-1], y_data[idx]
            
            if x1 == x0:
                return y0
                
            y_interp = y0 + (y1 - y0) * (x_pos - x0) / (x1 - x0)
            return y_interp

        return None

    def update_fef_lines(self):
        """Actualizar las líneas FEF cuando cambian PEF o FVC"""
        try:
            pef_vol = self.v_line_pef.value()
            fvc_vol = self.v_line_fvc.value()
            
            # Calcular posiciones de FEF
            diff = (fvc_vol - pef_vol) / 4
            
            self.v_line_fef25.setValue(pef_vol + diff)
            self.v_line_fef50.setValue(pef_vol + diff * 2)
            self.v_line_fef75.setValue(pef_vol + diff * 3)
            
            # Actualizar display de resultados
            self.update_results_display()
                
        except Exception as e:
            print(f"Error actualizando líneas FEF: {e}")

    def save_line_positions(self, recording_number):
        """Guardar las posiciones actuales de las líneas para una grabación"""
        if recording_number is None:
            return
            
        self.line_positions[recording_number] = {
            'vLine1': self.vLine1.value(),
            'vLine2': self.vLine2.value(),
            'v_line_pef': self.v_line_pef.value(),
            'v_line_fvc': self.v_line_fvc.value()
        }

    def restore_line_positions(self, recording_number):
        """Restaurar las posiciones de las líneas para una grabación"""
        if recording_number not in self.line_positions:
            # Posiciones por defecto si no hay guardadas
            self.vLine1.setValue(0.5)
            self.vLine2.setValue(1.5)
            self.v_line_pef.setValue(0)
            self.v_line_fvc.setValue(4)
            return
            
        positions = self.line_positions[recording_number]
        self.vLine1.setValue(positions['vLine1'])
        self.vLine2.setValue(positions['vLine2'])
        self.v_line_pef.setValue(positions['v_line_pef'])
        self.v_line_fvc.setValue(positions['v_line_fvc'])
        
        # Esto actualizará automáticamente las líneas dependientes
        self.update_fef_lines()

    def set_active_recording(self, recording_number):
        """Establecer una grabación como activa y actualizar visualización"""
        # Guardar posiciones de la grabación anterior
        if self.active_recording_number is not None:
            self.save_line_positions(self.active_recording_number)
        
        # Establecer nueva grabación activa
        self.active_recording_number = recording_number
        
        # Buscar la grabación
        recording_data = None
        for rec in self.stored_recordings:
            if rec['recording_number'] == recording_number:
                recording_data = rec
                break
        
        if recording_data is None:
            return
        
        # Cargar datos en display_data
        self.display_data = {
            't': recording_data['data']['t'].copy(),
            'p': recording_data['data']['p'].copy(),
            'f': recording_data['data']['f'].copy(),
            'v': recording_data['data']['v'].copy()
        }
        
        # Restaurar posiciones de líneas
        self.restore_line_positions(recording_number)
        
        # Actualizar estilo de las curvas
        self.update_curve_styles()
        
        # Actualizar gráficos
        self.update_plots()

    def update_curve_styles(self):
        """Actualizar el estilo visual de las curvas según cuál está activa"""
        for curve_data in self.stored_curves:
            recording_num = curve_data['recording_number']
            
            if recording_num == self.active_recording_number:
                # Curva activa: color original, opaca
                color_idx = (recording_num - 1) % len(self.recording_colors)
                color = self.recording_colors[color_idx]
                pen = pg.mkPen(color, width=3)
                
                curve_data['curve_time'].setPen(pen)
                if curve_data['curve_pressure']:
                    curve_data['curve_pressure'].setPen(pen)
            else:
                # Curvas inactivas: grises, semi-transparentes
                pen = pg.mkPen((150, 150, 150, 100), width=2, style=pg.QtCore.Qt.DashLine)
                
                curve_data['curve_time'].setPen(pen)
                if curve_data['curve_pressure']:
                    curve_data['curve_pressure'].setPen(pen)

    def calculate_averages(self):
        """Calcular promedios de todas las grabaciones almacenadas"""
        if not self.stored_recordings:
            return None
        
        metrics = {
            'fev1': [],
            'pef': [],
            'fef25': [],
            'fef50': [],
            'fef75': [],
            'fvc': [],
            'fif25': [],
            'fif50': [],
            'fif75': [],
            'fev1_fvc_ratio': []
        }
        
        # Calcular métricas para cada grabación
        for rec in self.stored_recordings:
            rec_num = rec['recording_number']
            
            # Cargar datos temporalmente
            temp_display = self.display_data.copy()
            self.display_data = rec['data'].copy()
            
            # Restaurar posiciones de líneas para esta grabación
            if rec_num in self.line_positions:
                positions = self.line_positions[rec_num]
                
                # FEV1
                x1 = positions['vLine1']
                x2 = positions['vLine2']
                y1 = self.get_y_value_at_x(x1)
                y2 = self.get_y_value_at_x(x2)
                if y1 is not None and y2 is not None:
                    metrics['fev1'].append(abs(y2 - y1))
                
                # PEF y FVC
                pef_vol = positions['v_line_pef']
                fvc_vol = positions['v_line_fvc']
                
                pef_flow, _ = self.get_flow_intersections_at_volume(pef_vol)
                if pef_flow is not None:
                    metrics['pef'].append(pef_flow)
                
                metrics['fvc'].append(fvc_vol)
                
                # Calcular posiciones FEF/FIF
                diff = (fvc_vol - pef_vol) / 4
                fef25_vol = pef_vol + diff
                fef50_vol = pef_vol + diff * 2
                fef75_vol = pef_vol + diff * 3
                
                # FEF25/FIF25
                fef25_flow, fif25_flow = self.get_flow_intersections_at_volume(fef25_vol)
                if fef25_flow is not None:
                    metrics['fef25'].append(fef25_flow)
                if fif25_flow is not None:
                    metrics['fif25'].append(abs(fif25_flow))
                
                # FEF50/FIF50
                fef50_flow, fif50_flow = self.get_flow_intersections_at_volume(fef50_vol)
                if fef50_flow is not None:
                    metrics['fef50'].append(fef50_flow)
                if fif50_flow is not None:
                    metrics['fif50'].append(abs(fif50_flow))
                
                # FEF75/FIF75
                fef75_flow, fif75_flow = self.get_flow_intersections_at_volume(fef75_vol)
                if fef75_flow is not None:
                    metrics['fef75'].append(fef75_flow)
                if fif75_flow is not None:
                    metrics['fif75'].append(abs(fif75_flow))
                
                # FEV1/FVC ratio
                if metrics['fev1'] and metrics['fvc'][-1] > 0:
                    ratio = (metrics['fev1'][-1] / metrics['fvc'][-1]) * 100
                    metrics['fev1_fvc_ratio'].append(ratio)
            
            # Restaurar datos originales
            self.display_data = temp_display
        
        # Calcular promedios
        averages = {}
        for key, values in metrics.items():
            if values:
                averages[key] = np.mean(values)
            else:
                averages[key] = None
        
        return averages

    def update_results_display(self):
        """Actualizar la lista de resultados"""
        self.results_list.clear()
        
        try:
            # Resultados de curva actual
            if self.active_recording_number is not None:
                self.results_list.addItem(f"=== Prueba {self.active_recording_number} ===")
            else:
                self.results_list.addItem("=== Curva Actual ===")
            
            # Gráfico izquierdo (Volumen vs Tiempo)
            self.results_list.addItem("--- FEV1 ---")
            
            x1 = self.vLine1.value()
            x2 = self.vLine2.value()
            y1 = self.get_y_value_at_x(x1)
            y2 = self.get_y_value_at_x(x2)
            
            if y1 is not None and y2 is not None:
                fev1 = abs(y2 - y1)
                self.results_list.addItem(f"Línea 1: {x1:.2f} s")
                self.results_list.addItem(f"Línea 2: {x2:.2f} s")
                self.results_list.addItem(f"FEV1: {fev1:.3f} L")
                self.results_list.addItem("")
            
            # Gráfico derecho (Flujo vs Volumen)
            self.results_list.addItem("--- Espirometría ---")
            
            # PEF
            pef_vol = self.v_line_pef.value()
            pef_flow, _ = self.get_flow_intersections_at_volume(pef_vol)
            if pef_flow is not None:
                self.results_list.addItem(f"PEF: {pef_flow:.3f} L/s")
            
            # FEF25/FIF25
            fef25_vol = self.v_line_fef25.value()
            fef25_flow, fif25_flow = self.get_flow_intersections_at_volume(fef25_vol)
            if fef25_flow is not None:
                self.results_list.addItem(f"FEF25: {fef25_flow:.3f} L/s")
            if fif25_flow is not None:
                self.results_list.addItem(f"FIF25: {abs(fif25_flow):.3f} L/s")
            
            # FEF50/FIF50
            fef50_vol = self.v_line_fef50.value()
            fef50_flow, fif50_flow = self.get_flow_intersections_at_volume(fef50_vol)
            if fef50_flow is not None:
                self.results_list.addItem(f"FEF50: {fef50_flow:.3f} L/s")
            if fif50_flow is not None:
                self.results_list.addItem(f"FIF50: {abs(fif50_flow):.3f} L/s")
            
            # FEF75/FIF75
            fef75_vol = self.v_line_fef75.value()
            fef75_flow, fif75_flow = self.get_flow_intersections_at_volume(fef75_vol)
            if fef75_flow is not None:
                self.results_list.addItem(f"FEF75: {fef75_flow:.3f} L/s")
            if fif75_flow is not None:
                self.results_list.addItem(f"FIF75: {abs(fif75_flow):.3f} L/s")
            
            # FVC
            fvc_vol = self.v_line_fvc.value()
            self.results_list.addItem(f"FVC: {fvc_vol:.3f} L")
            self.results_list.addItem("")
            
            # Calcular FEV1/FVC si hay datos
            if y1 is not None and y2 is not None and fvc_vol > 0:
                fev1 = abs(y2 - y1)
                ratio = (fev1 / fvc_vol) * 100
                self.results_list.addItem(f"FEV1/FVC: {ratio:.1f}%")
                self.results_list.addItem("")
            
            # Promedios de todas las curvas
            if len(self.stored_recordings) > 1:
                self.results_list.addItem("=== PROMEDIOS ===")
                averages = self.calculate_averages()
                
                if averages:
                    if averages['fev1'] is not None:
                        self.results_list.addItem(f"FEV1: {averages['fev1']:.3f} L")
                    if averages['pef'] is not None:
                        self.results_list.addItem(f"PEF: {averages['pef']:.3f} L/s")
                    
                    if averages['fef25'] is not None:
                        self.results_list.addItem(f"FEF25: {averages['fef25']:.3f} L/s")
                    if averages['fif25'] is not None:
                        self.results_list.addItem(f"FIF25: {averages['fif25']:.3f} L/s")
                    
                    if averages['fef50'] is not None:
                        self.results_list.addItem(f"FEF50: {averages['fef50']:.3f} L/s")
                    if averages['fif50'] is not None:
                        self.results_list.addItem(f"FIF50: {averages['fif50']:.3f} L/s")
                    
                    if averages['fef75'] is not None:
                        self.results_list.addItem(f"FEF75: {averages['fef75']:.3f} L/s")
                    if averages['fif75'] is not None:
                        self.results_list.addItem(f"FIF75: {averages['fif75']:.3f} L/s")
                    
                    if averages['fvc'] is not None:
                        self.results_list.addItem(f"FVC: {averages['fvc']:.3f} L")
                    
                    self.results_list.addItem("")
                    
                    if averages['fev1_fvc_ratio'] is not None:
                        self.results_list.addItem(f"FEV1/FVC: {averages['fev1_fvc_ratio']:.1f}%")
                    
                    self.results_list.addItem(f"(n={len(self.stored_recordings)})")
                
        except Exception as e:
            print(f"Error actualizando resultados: {e}")

    def prepare_new_recording(self):
        """Preparar el sistema para una nueva grabación"""
        if self.recording_count >= self.max_recordings:
            return False
        
        if self.recording_started:
            return False
        
        self.display_data = {'t': [], 'p': [], 'f': [], 'v': []}
        self.recording_started = False
        self.start_time = None
        self.ready_for_new_recording = True
        
        if hasattr(self, 'last_timestamp'):
            delattr(self, 'last_timestamp')
        
        return True

    def store_current_recording(self):
        """Almacenar la grabación actual"""
        if self.display_data['t']:
            recording_data = {
                'recording_number': len(self.stored_recordings) + 1,
                'data': {
                    't': self.display_data['t'].copy(),
                    'p': self.display_data['p'].copy(),
                    'f': self.display_data['f'].copy(),
                    'v': self.display_data['v'].copy()
                }
            }
            self.stored_recordings.append(recording_data)
            self.add_permanent_curve(recording_data)
            
            # Guardar posiciones de líneas para esta grabación
            self.save_line_positions(recording_data['recording_number'])
            
            self.flow_time_plot.autoRange()
            self.flow_pressure_plot.autoRange()
            
            self.new_recording_created.emit(
                recording_data['recording_number'], 
                recording_data['data']
            )

    def add_permanent_curve(self, recording_data):
        """Agregar curva permanente de la grabación al gráfico"""
        color_idx = (recording_data['recording_number'] - 1) % len(self.recording_colors)
        color = self.recording_colors[color_idx]
        
        curve_time = self.flow_time_plot.plot(
            x=recording_data['data']['t'],
            y=recording_data['data']['v'],
            pen=pg.mkPen(color, width=2, style=pg.QtCore.Qt.DashLine),
            name=f'Grabación {recording_data["recording_number"]}'
        )
        
        curve_pressure = None
        if recording_data['data']['f']:
            curve_pressure = self.flow_pressure_plot.plot(
                x=recording_data['data']['v'],
                y=recording_data['data']['f'],
                pen=pg.mkPen(color, width=2, style=pg.QtCore.Qt.DashLine),
                name=f'Grabación {recording_data["recording_number"]}'
            )
        
        self.stored_curves.append({
            'recording_number': recording_data['recording_number'],
            'curve_time': curve_time,
            'curve_pressure': curve_pressure
        })

    def delete_recording(self, recording_number):
        """Eliminar grabación específica por número"""
        # Eliminar posiciones de líneas guardadas
        if recording_number in self.line_positions:
            del self.line_positions[recording_number]
        
        # Si se elimina la curva activa, desactivar
        if self.active_recording_number == recording_number:
            self.active_recording_number = None
            self.display_data = {'t': [], 'p': [], 'f': [], 'v': []}
        
        # Eliminar de stored_recordings
        for i, recording in enumerate(self.stored_recordings):
            if recording['recording_number'] == recording_number:
                del self.stored_recordings[i]
                break
        else:
            return False

        # Limpiar gráficos
        self.flow_time_plot.clear()
        self.flow_pressure_plot.clear()
        self.stored_curves = []

        # Re-agregar curvas restantes
        for recording in self.stored_recordings:
            self.add_permanent_curve(recording)
        
        # Restaurar estilos
        self.setup_curve_styles()
        self.setup_vertical_lines()
        self.update_curve_styles()
        self.update_plots()

        return True

    def get_recording_list(self):
        """Obtener lista de números de grabaciones almacenadas"""
        return [rec['recording_number'] for rec in self.stored_recordings]

    def get_stored_recordings(self):
        """Obtener todas las grabaciones almacenadas"""
        return self.stored_recordings

    def reset_data(self):
        """Reset manual - usado después de calibración"""
        self.display_data = {'t': [], 'p': [], 'f': [], 'v': []}
        self.recording_started = False
        self.start_time = None
        self.ready_for_new_recording = False
        self.active_recording_number = None

    @Slot(dict)
    def update_data(self, new_data):
        try:
            if not self.graph_record:
                return

            if self.recording_count >= self.max_recordings:
                return

            volume = new_data.get('v', 0)
            t_raw = new_data.get('t', 0)
            self.last_timestamp = t_raw

            if not self.recording_started:
                if volume > 0.01 and self.ready_for_new_recording:
                    self.recording_started = True
                    self.start_time = t_raw
                return

            t_rel = (t_raw - self.start_time) / 1000.0

            if t_rel < 0:
                return

            if t_rel >= self.recording_duration:
                self.store_current_recording()
                self.recording_started = False
                self.start_time = None
                self.ready_for_new_recording = False
                self.recording_count += 1
                return

            self.display_data['t'].append(t_rel)
            self.display_data['v'].append(volume)

            for key in ['p', 'f']:
                if key in new_data:
                    self.display_data[key].append(new_data[key])

            self.update_plots()

        except Exception as e:
            print(f"Error en update_data: {e}")

    def update_plots(self):
        """Actualizar ambos gráficos"""
        if len(self.display_data['t']) > 0:
            self.flow_time_curve.setData(
                x=self.display_data['t'],
                y=self.display_data['v']
            )
            if len(self.display_data['f']) > 0:
                self.flow_pressure_curve.setData(
                    x=self.display_data['v'],
                    y=self.display_data['f']
                )
            self.update_results_display()

    def clear_data(self):
        """Limpiar todo - datos actuales y grabaciones"""
        for key in self.display_data:
            self.display_data[key] = []

        for curve_data in self.stored_curves:
            self.flow_time_plot.removeItem(curve_data['curve_time'])
            if curve_data['curve_pressure']:
                self.flow_pressure_plot.removeItem(curve_data['curve_pressure'])

        self.start_time = None
        self.recording_started = False
        self.recording_count = 0
        self.ready_for_new_recording = False
        self.stored_recordings = []
        self.stored_curves = []
        self.active_recording_number = None
        self.line_positions = {}

        self.update_plots()

        self.vLine1.setValue(0.5)
        self.vLine2.setValue(1.5)
        self.v_line_pef.setValue(0)
        self.v_line_fvc.setValue(4)
        
        self.graph_record = True
        self.update_results_display()

    def stop_record(self):
        """Detener grabación"""
        self.graph_record = False