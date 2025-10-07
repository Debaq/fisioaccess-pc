import pyqtgraph as pg
from PySide6.QtWidgets import QWidget, QHBoxLayout
from PySide6.QtCore import Slot, Signal
import numpy as np

class GraphHandler(QWidget):
    # Señal para notificar nueva grabación
    new_recording_created = Signal(int, dict)  # (número_grabación, datos)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Configurar el layout principal
        self.layout = QHBoxLayout(self)
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        # Crear los gráficos
        self.setup_graphs()

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
        self.recording_duration = 6.0  # Ajustar tiempo de duracion de la prueba
        self.ready_for_new_recording = False  # Control manual de grabaciones
        
        # Almacenar todas las grabaciones
        self.stored_recordings = []
        self.recording_colors = ['b', 'r', 'g', 'm', 'c', 'y', 'orange', 'purple', 'brown', 'pink']
        
        # Configurar estilos de las curvas
        self.setup_curve_styles()
        
        # Curvas para grabaciones almacenadas
        self.stored_curves = []

        # Agregar líneas verticales móviles
        self.setup_vertical_lines()

        self.graph_record = True
    
    def setup_graphs(self):
        """Configurar los widgets de gráficos con escalas fijas"""
        # Crear dos widgets de gráficos separados
        self.flow_time_widget = pg.PlotWidget()
        self.flow_pressure_widget = pg.PlotWidget()
        
        # Configurar el gráfico Volumen vs Tiempo (IZQUIERDO)
        self.flow_time_plot = self.flow_time_widget.getPlotItem()
        self.flow_time_plot.setLabel('left', 'Volumen', 'L')
        self.flow_time_plot.setLabel('bottom', 'Tiempo', 's')
        self.flow_time_plot.showGrid(x=True, y=True)
        
        grafico_volumen_tiempo_x = 17
        grafico_volumen_tiempo_y = 6
        # ESCALA FIJA IZQUIERDO: Y: 0-4L, X: 0-4s
        self.flow_time_plot.setXRange(0, grafico_volumen_tiempo_x, padding=0)
        self.flow_time_plot.setYRange(-4, grafico_volumen_tiempo_y, padding=0)
        self.flow_time_plot.getViewBox().setLimits(xMin=0, xMax=grafico_volumen_tiempo_x, yMin=-4, yMax=grafico_volumen_tiempo_y)
        self.flow_time_plot.getViewBox().setMouseEnabled(x=False, y=False)  # Deshabilitar zoom/pan
        
        # Configurar el gráfico Flujo vs Volumen (DERECHO)
        self.flow_pressure_plot = self.flow_pressure_widget.getPlotItem()
        self.flow_pressure_plot.setLabel('left', 'Flujo', 'L/s')
        self.flow_pressure_plot.setLabel('bottom', 'Volumen', 'L')
        self.flow_pressure_plot.showGrid(x=True, y=True)
        

        grafico_flujo_volumen_x = 8
        grafico_flujo_volumen_y = 10
        # ESCALA FIJA DERECHO: Y: -8 a 8 L/s, X: -1 a 4 L
        self.flow_pressure_plot.setXRange(0, grafico_flujo_volumen_x, padding=0)
        self.flow_pressure_plot.setYRange(0, grafico_flujo_volumen_y, padding=0)
        self.flow_pressure_plot.getViewBox().setLimits(xMin=-8, xMax= grafico_flujo_volumen_x, yMin=-8, yMax= grafico_flujo_volumen_y)
        self.flow_pressure_plot.getViewBox().setMouseEnabled(x=False, y=False)  # Deshabilitar zoom/pan
        
        # Configurar el fondo de los gráficos
        self.flow_time_widget.setBackground('w')
        self.flow_pressure_widget.setBackground('w')
        
        # Agregar los widgets al layout con la proporción correcta
        self.layout.addWidget(self.flow_time_widget, stretch=2)
        self.layout.addWidget(self.flow_pressure_widget, stretch=1)

    def setup_vertical_lines(self):
        """Configurar las líneas verticales móviles"""
        # Crear las líneas verticales para el gráfico Volumen vs Tiempo
        self.vLine1 = pg.InfiniteLine(
            pos=0.5, 
            angle=90, 
            movable=True,
            pen=pg.mkPen('r', width=2),
            bounds=(0, 16)  # Limitar movimiento a rango X
        )
        self.vLine2 = pg.InfiniteLine(
            pos=1.5, 
            angle=90, 
            movable=True,
            pen=pg.mkPen('g', width=2),
            bounds=(0, 16)  # Limitar movimiento a rango X
        )
        
        self.v_line_fvc = pg.InfiniteLine(
            pos=1.5, 
            angle=90, 
            movable=True,
            pen=pg.mkPen('r', width=2),
            bounds=(0, 7)  # Limitar movimiento a rango X
        )

        self.v_line_pef = pg.InfiniteLine(
            pos=0, 
            angle=90, 
            movable=True,
            pen=pg.mkPen('b', width=2),
            label="PEF",
            labelOpts={"movable":True, "position":0.8, "color":(250, 0, 0)},
            bounds=(0, 7)  # Limitar movimiento a rango X
        )

        self.v_line_fev025= pg.InfiniteLine(
            pos=1, 
            angle=90, 
            movable=False,
            pen=pg.mkPen('r', width=2),
            label="fef025",
            labelOpts={"movable":True, "position":0.8, "color":(250, 0, 0)},
            bounds=(0, 7)  # Limitar movimiento a rango X
        )
        #self.text_line_fev025 = pg.InfLineLabel(self.v_line_fev025, text="FEV025", movable=True, position=0.5)

        self.v_line_fev050 = pg.InfiniteLine(
            pos=2, 
            angle=90, 
            movable=False,
            pen=pg.mkPen('b', width=2),
            label="fef050",
            labelOpts={"movable":True, "position":0.8, "color":(250, 0, 0)},
            bounds=(0, 7)  # Limitar movimiento a rango X
        )

        self.v_line_fev075 = pg.InfiniteLine(
            pos=3, 
            angle=90, 
            movable=False,
            pen=pg.mkPen('g', width=2),
            label="fef075",
            labelOpts={"movable":True, "position":0.8, "color":(250, 0, 0)},
            bounds=(0, 7)  # Limitar movimiento a rango X
        )

        self.v_line_fvc = pg.InfiniteLine(
            pos=4, 
            angle=90, 
            movable=True,
            pen=pg.mkPen('r', width=2),
            label="FVC",
            labelOpts={"movable":True, "position":0.8, "color":(250, 0, 0)},
            bounds=(0, 7)  # Limitar movimiento a rango X
        )
        
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


        self.flow_pressure_plot.addItem(self.v_line_pef)
        self.flow_pressure_plot.addItem(self.v_line_fev025)
        self.flow_pressure_plot.addItem(self.v_line_fev050)
        self.flow_pressure_plot.addItem(self.v_line_fev075)
        self.flow_pressure_plot.addItem(self.v_line_fvc)
        
        # Conectar señales para actualizar cuando las líneas se muevan
        self.vLine1.sigPositionChanged.connect(self.update_line_info)
        self.vLine2.sigPositionChanged.connect(self.update_line_info)
        self.v_line_pef.sigPositionChanged.connect(self.update_line_pef_fvc)
        self.v_line_fvc.sigPositionChanged.connect(self.update_line_pef_fvc)

    def setup_curve_styles(self):
        """Configurar las curvas de los gráficos"""
        # Curva actual para Volumen vs Tiempo (línea sólida azul)
        self.flow_time_curve = self.flow_time_plot.plot(
            pen=pg.mkPen('b', width=3)
        )
        
        # Curva actual para Flujo vs Volumen (línea sólida roja)
        self.flow_pressure_curve = self.flow_pressure_plot.plot(
            pen=pg.mkPen('r', width=3)
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
        if idx > 0 and idx < len(x_data):
            x0, x1 = x_data[idx-1], x_data[idx]
            y0, y1 = y_data[idx-1], y_data[idx]
            
            if x1 == x0:
                return y0
                
            y_interp = y0 + (y1 - y0) * (x_pos - x0) / (x1 - x0)
            return y_interp

        return None

    def update_line_pef_fvc(self):
        try:
            pef = self.v_line_pef.value()
            fvc = self.v_line_fvc.value()
            #evitar que pef sea mayor a fvc
            diff_4 = (fvc - pef)/4
            self.v_line_fev025.setValue(pef + diff_4)
            self.v_line_fev050.setValue(pef + diff_4*2)
            self.v_line_fev075.setValue(pef + diff_4*3)
            print(f"pef {pef} , fvc {fvc}, fev025 {self.v_line_fev025.setValue(pef + diff_4)}")
            
            #self.text_line_fev025.setFormat(f"fev025: {self.v_line_fev025.value()}")

        except:
            pass
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
                y_position = 3.5  # Posición fija cerca del tope
                
                self.diff_label.setPos(x_mid, y_position)
                self.diff_label.setText(
                    f'ΔX: {x_diff:.2f} s\n'
                    f'ΔY: {y_diff:.2f} L'
                )
        except Exception as e:
            print(f"Error actualizando líneas: {e}")

    def start_new_recording(self):
        """Activar nueva grabación - debe llamarse manualmente"""
        if self.recording_count >= self.max_recordings:
            print(f"No se pueden crear más grabaciones. Máximo: {self.max_recordings}")
            return False
        
        if self.recording_started:
            print("Ya hay una grabación en curso")
            return False
            
        self.ready_for_new_recording = True
        print(f"Sistema listo para nueva grabación {self.recording_count + 1}")
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
            
            # Agregar curva permanente al gráfico
            self.add_permanent_curve(recording_data)
            
            # Emitir señal de nueva grabación
            self.new_recording_created.emit(
                recording_data['recording_number'], 
                recording_data['data']
            )
            
            print(f"Grabación {recording_data['recording_number']} almacenada y señal emitida")

    def add_permanent_curve(self, recording_data):
        """Agregar curva permanente de la grabación al gráfico"""
        color_idx = (recording_data['recording_number'] - 1) % len(self.recording_colors)
        color = self.recording_colors[color_idx]
        
        # Curva en gráfico tiempo-volumen (línea punteada)
        curve_time = self.flow_time_plot.plot(
            x=recording_data['data']['t'],
            y=recording_data['data']['v'],
            pen=pg.mkPen(color, width=2, style=pg.QtCore.Qt.DashLine),
            name=f'Grabación {recording_data["recording_number"]}'
        )
        
        # Curva en gráfico volumen-flujo (si hay datos de flujo)
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
        # 1. Buscar y eliminar de stored_recordings
        for i, recording in enumerate(self.stored_recordings):
            if recording['recording_number'] == recording_number:
                del self.stored_recordings[i]
                break
        else:
            print(f"Grabación {recording_number} no encontrada")
            return False

        # 2. Limpiar completamente ambos gráficos
        self.flow_time_plot.clear()
        self.flow_pressure_plot.clear()

        # 3. Limpiar listas
        self.stored_curves = []

        # 4. Recrear solo las grabaciones restantes
        for recording in self.stored_recordings:
            self.add_permanent_curve(recording)
            
        self.display_data = {'t': [], 'p': [], 'f': [], 'v': []}

        # 5. Recrear curvas actuales (si hay datos)
        self.setup_curve_styles()
        self.setup_vertical_lines()
        self.update_plots()

        print(f"Grabación {recording_number} eliminada")
        return True

    def get_recording_list(self):
        """Obtener lista de números de grabaciones almacenadas"""
        return [rec['recording_number'] for rec in self.stored_recordings]

    def get_stored_recordings(self):
        """Obtener todas las grabaciones almacenadas"""
        return self.stored_recordings

    def reset_data(self):
        """Reset manual - usado después de calibración"""
        self.display_data = {
            't': [],
            'p': [],
            'f': [],
            'v': []
        }
        
        # Resetear variables de grabación después de calibración
        self.recording_started = False
        self.start_time = None
        self.ready_for_new_recording = False
        print("DEBUG: reset_data() - Variables de grabación reseteadas")

    @Slot(dict)
    def update_data(self, new_data):
        try:
            if not self.graph_record:
                return

            # Verificar si ya se alcanzó el máximo de grabaciones
            if self.recording_count >= self.max_recordings:
                return

            # El volumen ya viene en litros desde el equipo
            volume = new_data.get('v', 0)
            t_raw = new_data.get('t', 0)

            # Detectar reset de placa: si timestamp actual es mucho menor que el anterior
            if hasattr(self, 'last_timestamp') and t_raw < self.last_timestamp * 0.1 and self.last_timestamp > 1000:
                self.start_time = None  # Forzar recálculo
                self.recording_started = False  # Reiniciar grabación
                print(f"DEBUG: Reset de placa detectado, timestamp: {t_raw}, último: {self.last_timestamp}")
                
            # Actualizar último timestamp
            self.last_timestamp = t_raw

            # Si aún no ha empezado a grabar, esperar volumen positivo Y activación manual
            if not self.recording_started:
                if volume > 0 and self.ready_for_new_recording:  # Requiere activación manual
                    self.recording_started = True
                    self.start_time = t_raw  # Usar el timestamp actual como referencia
                    # Limpiar solo los datos actuales
                    for key in self.display_data:
                        self.display_data[key] = []
                    print(f"DEBUG: Grabación {self.recording_count + 1} iniciada con start_time={self.start_time}")
                return

            # ---------- grabación activa ----------
            t_rel = (t_raw - self.start_time) / 1000.0  # ms → s (tiempo relativo desde inicio)

            # Verificar tiempo negativo
            if t_rel < 0:
                print(f"Tiempo negativo detectado: {t_rel} - IGNORANDO DATO")
                return

            # Verificar si se cumplieron los 3 segundos
            if t_rel >= self.recording_duration:
                # Almacenar la grabación actual
                self.store_current_recording()
                
                # Reiniciar para la siguiente grabación
                self.recording_started = False
                self.start_time = None
                self.ready_for_new_recording = False  # Desactivar hasta nueva activación manual
                self.recording_count += 1
                
                print(f"Grabación completada. Total: {self.recording_count}/{self.max_recordings}")
                return

            # Agregar datos actuales
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
            # Actualizar curva actual (línea sólida)
            self.flow_time_curve.setData(
                x=self.display_data['t'],
                y=self.display_data['v']
            )
            if len(self.display_data['f']) > 0:
                self.flow_pressure_curve.setData(
                    x=self.display_data['v'],
                    y=self.display_data['f']
                )
            self.update_line_info()

    def clear_data(self):
        """Limpiar todo - datos actuales y grabaciones"""
        # Limpiar datos actuales
        for key in self.display_data:
            self.display_data[key] = []

        # Limpiar grabaciones almacenadas
        for curve_data in self.stored_curves:
            self.flow_time_plot.removeItem(curve_data['curve_time'])
            if curve_data['curve_pressure']:
                self.flow_pressure_plot.removeItem(curve_data['curve_pressure'])

        # Resetear variables
        self.start_time = None
        self.recording_started = False
        self.recording_count = 0
        self.ready_for_new_recording = False
        self.stored_recordings = []
        self.stored_curves = []

        # Limpiar curvas actuales
        self.update_plots()

        # Resetear líneas verticales
        self.vLine1.setValue(0.5)
        self.vLine2.setValue(1.5)
        self.label1.setText('')
        self.label2.setText('')
        self.diff_label.setText('')

        self.graph_record = True

    def stop_record(self):
        """Detener grabación"""
        self.graph_record = False