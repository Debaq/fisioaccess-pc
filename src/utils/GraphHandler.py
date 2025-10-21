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
        self.flow_pressure_plot.setYRange(0, grafico_flujo_volumen_y, padding=0)
        self.flow_pressure_plot.getViewBox().setLimits(xMin=-8, xMax=grafico_flujo_volumen_x, yMin=-8, yMax=grafico_flujo_volumen_y)
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
        """Configurar las líneas verticales con identificadores simples"""
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
        
        # Gráfico derecho: líneas PEF, FEF y FVC con identificadores
        self.v_line_pef = pg.InfiniteLine(
            pos=0, 
            angle=90, 
            movable=True,
            pen=pg.mkPen('b', width=2),
            bounds=(0, 7),
            label="A",
            labelOpts={
                "position": 0.95,
                "color": (0, 0, 255),
                "fill": (255, 255, 255, 200)
            }
        )
        self.v_line_pef.setZValue(10)

        self.v_line_fef025 = pg.InfiniteLine(
            pos=1, 
            angle=90, 
            movable=False,
            pen=pg.mkPen('r', width=2),
            bounds=(0, 7),
            label="B",
            labelOpts={
                "position": 0.85,
                "color": (255, 0, 0),
                "fill": (255, 255, 255, 200)
            }
        )
        self.v_line_fef025.setZValue(10)

        self.v_line_fef050 = pg.InfiniteLine(
            pos=2, 
            angle=90, 
            movable=False,
            pen=pg.mkPen('b', width=2),
            bounds=(0, 7),
            label="C",
            labelOpts={
                "position": 0.75,
                "color": (0, 0, 255),
                "fill": (255, 255, 255, 200)
            }
        )
        self.v_line_fef050.setZValue(10)

        self.v_line_fef075 = pg.InfiniteLine(
            pos=3, 
            angle=90, 
            movable=False,
            pen=pg.mkPen('g', width=2),
            bounds=(0, 7),
            label="D",
            labelOpts={
                "position": 0.65,
                "color": (0, 255, 0),
                "fill": (255, 255, 255, 200)
            }
        )
        self.v_line_fef075.setZValue(10)

        self.v_line_fvc = pg.InfiniteLine(
            pos=4, 
            angle=90, 
            movable=True,
            pen=pg.mkPen('r', width=2),
            bounds=(0, 7),
            label="E",
            labelOpts={
                "position": 0.55,
                "color": (255, 0, 0),
                "fill": (255, 255, 255, 200)
            }
        )
        self.v_line_fvc.setZValue(10)
        
        # Agregar líneas a los gráficos
        self.flow_time_plot.addItem(self.vLine1)
        self.flow_time_plot.addItem(self.vLine2)
        
        self.flow_pressure_plot.addItem(self.v_line_pef)
        self.flow_pressure_plot.addItem(self.v_line_fef025)
        self.flow_pressure_plot.addItem(self.v_line_fef050)
        self.flow_pressure_plot.addItem(self.v_line_fef075)
        self.flow_pressure_plot.addItem(self.v_line_fvc)
        
        # Conectar señales
        self.vLine1.sigPositionChanged.connect(self.update_results_display)
        self.vLine2.sigPositionChanged.connect(self.update_results_display)
        self.v_line_pef.sigPositionChanged.connect(self.update_line_pef_fvc)
        self.v_line_fvc.sigPositionChanged.connect(self.update_line_pef_fvc)

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

    def update_line_pef_fvc(self):
        """Actualizar las líneas FEF cuando cambian PEF o FVC"""
        try:
            pef_vol = self.v_line_pef.value()
            fvc_vol = self.v_line_fvc.value()
            
            # Calcular posiciones de FEF
            diff = (fvc_vol - pef_vol) / 4
            
            self.v_line_fef025.setValue(pef_vol + diff)
            self.v_line_fef050.setValue(pef_vol + diff * 2)
            self.v_line_fef075.setValue(pef_vol + diff * 3)
            
            # Actualizar display de resultados
            self.update_results_display()
                
        except Exception as e:
            print(f"Error actualizando líneas PEF/FVC: {e}")

    def update_results_display(self):
        """Actualizar la lista de resultados"""
        self.results_list.clear()
        
        try:
            # Gráfico izquierdo (Volumen vs Tiempo)
            self.results_list.addItem("=== Gráfico 1 ===")
            
            x1 = self.vLine1.value()
            x2 = self.vLine2.value()
            y1 = self.get_y_value_at_x(x1)
            y2 = self.get_y_value_at_x(x2)
            
            if y1 is not None and y2 is not None:
                fev1 = abs(y2 - y1)
                self.results_list.addItem(f"Línea 1: {x1:.2f} s")
                self.results_list.addItem(f"Línea 2: {x2:.2f} s")
                self.results_list.addItem(f"FEV1: {fev1:.2f} L")
                self.results_list.addItem("")
            
            # Gráfico derecho (Flujo vs Volumen)
            self.results_list.addItem("=== Gráfico 2 ===")
            
            pef_vol = self.v_line_pef.value()
            fvc_vol = self.v_line_fvc.value()
            
            pef_flow = self.get_flow_at_volume(pef_vol)
            fef25_flow = self.get_flow_at_volume(self.v_line_fef025.value())
            fef50_flow = self.get_flow_at_volume(self.v_line_fef050.value())
            fef75_flow = self.get_flow_at_volume(self.v_line_fef075.value())
            
            if pef_flow is not None:
                self.results_list.addItem(f"A - PEF: {pef_flow:.2f} L/s")
            if fef25_flow is not None:
                self.results_list.addItem(f"B - FEF25: {fef25_flow:.2f} L/s")
            if fef50_flow is not None:
                self.results_list.addItem(f"C - FEF50: {fef50_flow:.2f} L/s")
            if fef75_flow is not None:
                self.results_list.addItem(f"D - FEF75: {fef75_flow:.2f} L/s")
            
            self.results_list.addItem(f"E - FVC: {fvc_vol:.2f} L")
            
            # Calcular FEV1/FVC si hay datos
            if y1 is not None and y2 is not None and fvc_vol > 0:
                fev1 = abs(y2 - y1)
                ratio = (fev1 / fvc_vol) * 100
                self.results_list.addItem("")
                self.results_list.addItem(f"FEV1/FVC: {ratio:.1f}%")
                
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
        for i, recording in enumerate(self.stored_recordings):
            if recording['recording_number'] == recording_number:
                del self.stored_recordings[i]
                break
        else:
            return False

        self.flow_time_plot.clear()
        self.flow_pressure_plot.clear()
        self.stored_curves = []

        for recording in self.stored_recordings:
            self.add_permanent_curve(recording)
            
        self.display_data = {'t': [], 'p': [], 'f': [], 'v': []}
        self.setup_curve_styles()
        self.setup_vertical_lines()
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

        self.update_plots()

        self.vLine1.setValue(0.5)
        self.vLine2.setValue(1.5)
        
        self.graph_record = True
        self.update_results_display()

    def stop_record(self):
        """Detener grabación"""
        self.graph_record = False