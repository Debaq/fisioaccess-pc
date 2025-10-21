from PySide6.QtWidgets import QMainWindow, QListWidgetItem
from PySide6.QtCore import QTimer, Slot, Qt
from PySide6.QtGui import QColor, QBrush
import serial.tools.list_ports
from .main_window import Ui_Main
from serial_comm.serial_handler import SerialHandler  
from serial_comm.SerialDataHandler import SerialDataHandler
from utils.GraphHandler import GraphHandler
from utils.FileHandler import FileHandler

class MainWindow(QMainWindow, Ui_Main):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        
        # Variables de estado
        self.is_calibrated = False
        self.is_testing = False
        self.test_counter = 0
        
        # Variable para almacenar info de calidad actual
        self.current_quality = None
        
        # Iniciar metodos de guardado
        self.file_handler = FileHandler()
        # Inicializar el manejador serial
        self.serial_handler = SerialHandler()
        self.data_handler = SerialDataHandler()
 
        # Inicializar los gráficos
        self.graph_handler = GraphHandler()
        self.horizontalLayout_2.addWidget(self.graph_handler)

        # Configurar el timer para actualizar la lista de puertos
        self.port_timer = QTimer()
        self.port_timer.timeout.connect(self.update_port_list)
        self.port_timer.start(1000)  # Actualizar cada segundo
        
        # Lista para mantener track de los puertos disponibles
        self.available_ports = []
        
        # Conectar señales
        self.connect_signals()
        
        # Actualizar lista inicial de puertos
        self.update_port_list()
        
        # Estado inicial de botones
        self.update_button_states()

    def connect_signals(self):
        """Conectar todas las señales necesarias"""
        
        self.file_handler.save_status.connect(self.statusbar.showMessage)
        self.file_handler.error_occurred.connect(self.statusbar.showMessage)
        self.btn_save.clicked.connect(self.save_data)

        self.btn_clear.clicked.connect(self.clear_data)
        
        # Cambiar reset por calibración
        self.btn_cal.clicked.connect(self.calibrate)
        
        # Conectar el botón de abrir
        self.btn_open.clicked.connect(self.open_data)
        
        # Conectar la señal de datos cargados del file_handler
        self.file_handler.data_loaded.connect(self.load_data_to_graph)

        # Conectar el botón de conexión
        self.btn_connect.clicked.connect(self.handle_connection)
        
        # Conectar el cambio de selección del combo box
        self.serial_list.currentIndexChanged.connect(self.port_selected)

        # Verificar la conexión de señales del serial_handler
        try:
            # Desconectar primero para evitar conexiones duplicadas
            try:
                self.serial_handler.data_received_serial.disconnect(self.data_handler.analisis_input_serial)
            except:
                pass
            
            # Reconectar la señal
            self.serial_handler.data_received_serial.connect(self.data_handler.analisis_input_serial)
        except Exception as e:
            print(f"Error al conectar serial_handler.data_received: {str(e)}")

        # Verificar la conexión del data_handler
        try:
            self.data_handler.new_data.connect(self.graph_handler.update_data)
            self.data_handler.other_string.connect(self.handle_calibration_response)

            print("Señal new_data conectada exitosamente a graph_handler")
        except Exception as e:
            print(f"Error al conectar data_handler.new_data: {str(e)}")
        
        # Conectar señal de prueba completada
        try:
            self.graph_handler.new_recording_created.connect(self.on_test_completed)
            print("Señal new_recording_created conectada")
        except Exception as e:
            print(f"Error al conectar new_recording_created: {str(e)}")
        
        # Conectar señal de calidad
        try:
            self.graph_handler.quality_changed.connect(self.update_test_list_colors)
            print("Señal quality_changed conectada")
        except Exception as e:
            print(f"Error al conectar quality_changed: {str(e)}")
        
        self.btn_start.clicked.connect(self.start_test)
        
        # Conectar señales del list_test - NUEVA FUNCIONALIDAD
        self.list_test.itemSelectionChanged.connect(self.on_test_selection_changed)
        self.list_test.itemClicked.connect(self.on_test_clicked)
        
        # Conectar botón para eliminar pruebas
        self.btn_delete_test.clicked.connect(self.delete_selected_test)

        print("Conexión de señales completada\n")

    def update_button_states(self):
        """Actualizar el estado de los botones según el estado actual"""
        is_connected = self.btn_connect.isChecked()
        
        # Botón calibrar: solo disponible si está conectado y no está probando
        self.btn_cal.setEnabled(is_connected and not self.is_testing)
        
        # Botón iniciar: solo disponible si está calibrado y no está probando
        self.btn_start.setEnabled(is_connected and self.is_calibrated and not self.is_testing)
        
        # Botón limpiar: disponible si está conectado y no está probando
        self.btn_clear.setEnabled(is_connected and not self.is_testing)
        
        # Botón eliminar test: disponible si hay algo seleccionado en la lista
        self.btn_delete_test.setEnabled(self.list_test.currentItem() is not None)
        
        # Lista de puertos: deshabilitada si está conectado o probando
        self.serial_list.setEnabled(not is_connected and not self.is_testing)

    @Slot()
    def calibrate(self):
        """Enviar comando de calibración"""
        try:
            if self.serial_handler:
                # Asegurar que la lectura esté activa
                if not hasattr(self.serial_handler, 'reader_thread') or self.serial_handler.reader_thread is None:
                    self.serial_handler.start_reading()
                
                # Enviar comando de calibración
                self.serial_handler.write_data("r")
                self.statusbar.showMessage("Enviando comando de calibración...")
                # El estado se actualizará cuando llegue la respuesta de calibración
        except Exception as e:
            self.statusbar.showMessage(f"Error al calibrar: {str(e)}")
            print(f"Error en calibración: {str(e)}")

    @Slot()
    def handle_calibration_response(self, data):
        """Manejar la respuesta de calibración"""
        if data.startswith("Iniciando calibración"):
            self.statusbar.showMessage("Calibración iniciada...")
            self.btn_cal.setEnabled(False)  # Deshabilitar botón durante calibración
        elif data.startswith("Asegúrese que no hay flujo"):
            self.statusbar.showMessage("IMPORTANTE: Asegúrese que no hay flujo de aire")
        elif data.startswith("Calibrando:"):
            # Mostrar progreso de calibración
            self.statusbar.showMessage(f"Calibrando... {data}")
        elif data.startswith("Calibración completada."):
            self.statusbar.showMessage("Calibración completada - Configurando sistema...")
        elif data.startswith("Desviación estándar:"):
            self.statusbar.showMessage(f"Calibración exitosa - {data}")
        elif data.startswith("Iniciando mediciones..."):
            # Aquí es donde realmente está listo
            self.is_calibrated = True
            self.graph_handler.reset_data()
            self.statusbar.showMessage("Sistema calibrado y listo para iniciar prueba")
            self.update_button_states()
        elif data.startswith("Tiempo(ms),Presion(kPa)"):
            # Headers de datos, ignorar o registrar
            pass
        else:
            self.statusbar.showMessage(f"Dispositivo: {data}")


    @Slot()
    def start_test(self):
        """Iniciar una nueva prueba"""
        
        if not self.is_calibrated:
            self.statusbar.showMessage("Debe calibrar antes de iniciar una prueba")
            return
            
        try:
            self.is_testing = True
            self.update_button_states()
            
            # ORDEN CORRECTO:
            # 1. Preparar el GraphHandler ANTES de enviar comando al hardware
            self.graph_handler.prepare_new_recording()
            
            # 2. Enviar comando al hardware
            if self.serial_handler:
                if not hasattr(self.serial_handler, 'reader_thread') or self.serial_handler.reader_thread is None:
                    self.serial_handler.start_reading()
                
                self.serial_handler.write_data("v")
                self.statusbar.showMessage("Comando de reset enviado, iniciando prueba...")
            
        except Exception as e:
            self.is_testing = False
            self.update_button_states()
            self.statusbar.showMessage(f"Error al iniciar prueba: {str(e)}")
            print(f"Error al iniciar prueba: {str(e)}")

    @Slot()
    def on_test_completed(self, recording_data):
        """Manejar cuando se completa una prueba"""
        try:
            self.is_testing = False
            self.test_counter += 1
            
            # Crear item en la lista de pruebas
            test_name = f"Prueba {self.test_counter}"
            item = QListWidgetItem(test_name)
            
            # Guardar el número de grabación, no todo el objeto
            if isinstance(recording_data, dict) and 'recording_number' in recording_data:
                recording_number = recording_data['recording_number']
            else:
                recording_number = recording_data  # Asumir que ya es el número
            
            item.setData(Qt.UserRole, recording_number)
            self.list_test.addItem(item)
            
            print(f"Test agregado: {test_name}, recording_number: {recording_number}")
            
            self.statusbar.showMessage(f"Prueba completada - {test_name} agregada a la lista")
            self.update_button_states()
            
            # Detener la lectura serial
            if self.serial_handler:
                self.serial_handler.stop_reading()
                
        except Exception as e:
            self.statusbar.showMessage(f"Error al completar prueba: {str(e)}")
            print(f"Error al completar prueba: {str(e)}")

    @Slot(dict)
    def update_test_list_colors(self, quality_info):
        """Actualizar colores y badges de las pruebas según calidad"""
        try:
            self.current_quality = quality_info
            
            if not quality_info or quality_info['grade'] is None:
                return
            
            # Obtener lista de pruebas que deberían eliminarse (sugerencias)
            suggested_removals = set()
            if quality_info.get('suggestions'):
                for suggestion in quality_info['suggestions']:
                    suggested_removals.add(suggestion['recording_number'])
            
            # Determinar color según grado
            grade = quality_info['grade']
            grade_colors = {
                'A': QColor(0, 200, 0),      # Verde
                'B': QColor(150, 200, 0),    # Verde-amarillo
                'C': QColor(255, 165, 0),    # Naranja
                'D': QColor(200, 100, 0)     # Naranja-rojo
            }
            grade_color = grade_colors.get(grade, QColor(128, 128, 128))
            
            # Actualizar cada item en la lista
            for i in range(self.list_test.count()):
                item = self.list_test.item(i)
                recording_number = item.data(Qt.UserRole)
                
                if recording_number in suggested_removals:
                    # Marcar en rojo con asterisco
                    item.setText(f"Prueba {recording_number}*")
                    item.setForeground(QBrush(QColor(255, 0, 0)))
                else:
                    # Marcar con badge de grado y color correspondiente
                    item.setText(f"Prueba {recording_number} [{grade}]")
                    item.setForeground(QBrush(grade_color))
            
        except Exception as e:
            print(f"Error actualizando colores de lista: {str(e)}")

    @Slot()
    def on_test_selection_changed(self):
        """Manejar cambio de selección en la lista de pruebas"""
        current_item = self.list_test.currentItem()
        if current_item:
            # Actualizar estado del botón eliminar
            self.update_button_states()
        else:
            # Ninguna prueba seleccionada
            self.update_button_states()

    @Slot()
    def on_test_clicked(self, item):
        """Manejar click en una prueba de la lista"""
        try:
            recording_number = item.data(Qt.UserRole)
            test_name = item.text()
            
            print(f"Prueba seleccionada: {test_name}, recording_number: {recording_number}")
            
            # Activar esta grabación en el GraphHandler
            self.graph_handler.set_active_recording(recording_number)
            
            self.statusbar.showMessage(f"Mostrando: {test_name}")
            
        except Exception as e:
            self.statusbar.showMessage(f"Error al seleccionar prueba: {str(e)}")
            print(f"Error al seleccionar prueba: {str(e)}")

    @Slot()
    def delete_selected_test(self):
        """Eliminar la prueba seleccionada"""
        current_item = self.list_test.currentItem()
        if not current_item:
            self.statusbar.showMessage("No hay prueba seleccionada para eliminar")
            return
            
        try:
            test_name = current_item.text()
            row = self.list_test.row(current_item)
            recording_number = current_item.data(Qt.UserRole)
            
            print(f"Intentando eliminar: {test_name}, recording_number: {recording_number}")
            print(f"Lista actual de grabaciones: {self.graph_handler.get_recording_list()}")
            
            # Eliminar del graph_handler primero
            if hasattr(self.graph_handler, 'delete_recording') and recording_number is not None:
                success = self.graph_handler.delete_recording(recording_number)
                print(f"Eliminación del gráfico: {'exitosa' if success else 'falló'}")
                print(f"Lista después de eliminar: {self.graph_handler.get_recording_list()}")
            
            # Eliminar de la lista visual
            self.list_test.takeItem(row)
            
            # Actualizar estados de botones
            self.update_button_states()
            
            self.statusbar.showMessage(f"Prueba eliminada: {test_name}")
            
        except Exception as e:
            self.statusbar.showMessage(f"Error al eliminar prueba: {str(e)}")
            print(f"Error al eliminar prueba: {str(e)}")

    @Slot()
    def update_port_list(self):
        """Actualizar la lista de puertos seriales disponibles"""
        # Obtener puertos actuales
        ports = self.serial_handler.get_available_ports()
        
        # Si la lista es diferente a la anterior, actualizar el combo box
        if ports != self.available_ports:
            # Guardar el puerto seleccionado actualmente
            current_port = self.serial_list.currentText()
            
            # Actualizar la lista de puertos
            self.serial_list.clear()
            self.serial_list.addItems(ports)
            
            # Intentar mantener el puerto seleccionado si aún existe
            if current_port in ports:
                self.serial_list.setCurrentText(current_port)
            
            # Actualizar la lista de puertos disponibles
            self.available_ports = ports
            
            # Deshabilitar el botón de conexión si no hay puertos
            self.btn_connect.setEnabled(len(ports) > 0 and not self.is_testing)
            
            # Si no hay puertos y estaba conectado, desconectar
            if not ports and self.btn_connect.isChecked():
                self.btn_connect.setChecked(False)
                self.handle_connection()

    @Slot()
    def handle_connection(self):
        """Manejar la conexión/desconexión del puerto serial"""
        if self.btn_connect.isChecked():
            try:
                port = self.serial_list.currentText()
                
                # Crear nueva instancia de SerialHandler
                self.serial_handler = SerialHandler(port=port)
                
                # Reconectar la señal data_received
                try:
                    self.serial_handler.data_received_serial.disconnect(self.data_handler.analisis_input_serial)
                except:
                    pass
                self.serial_handler.data_received_serial.connect(self.data_handler.analisis_input_serial)
                
                if self.serial_handler.open():
                    self.statusbar.showMessage(f"Conectado a {port} - Debe calibrar antes de iniciar pruebas")
                    self.btn_connect.setText("Desconectar")
                    
                    # Reset del estado de calibración al conectar
                    self.is_calibrated = False
                    self.update_button_states()
                
                else:
                    raise Exception("No se pudo conectar al puerto")
                    
            except Exception as e:
                print(f"Error en conexión: {str(e)}")
                self.statusbar.showMessage(f"Error de conexión: {str(e)}")
                self.btn_connect.setChecked(False)
                self.update_button_states()
        else:
            try:
                if self.serial_handler:
                    self.serial_handler.stop_reading()
                    self.serial_handler.close()
                self.statusbar.showMessage("Desconectado")
                self.btn_connect.setText("Conectar")
                
                # Reset de estados al desconectar
                self.is_calibrated = False
                self.is_testing = False
                self.update_button_states()

            except Exception as e:
                self.statusbar.showMessage(f"Error al desconectar: {str(e)}")

    @Slot()
    def open_data(self):
        """Abrir y cargar datos desde un archivo"""
        # Desconectar del puerto serial si está conectado
        if self.btn_connect.isChecked():
            self.btn_connect.setChecked(False)
            self.handle_connection()
        
        # Abrir archivo
        self.file_handler.open_data_file(self)

    @Slot(dict)
    def load_data_to_graph(self, data):
        """
        Cargar datos en el gráfico
        
        Args:
            data (dict): Diccionario con los datos cargados
        """
        try:
            # Activar grabación de gráficos
            self.graph_handler.graph_record = True
            
            # Asignar datos directamente a display_data
            self.graph_handler.display_data = {
                't': data['t'].copy(),
                'p': data['p'].copy(),
                'f': data['f'].copy(),
                'v': data['v'].copy()
            }
            
            # Actualizar visualización
            self.graph_handler.update_plots()
            
            # Deshabilitar botones de control serial
            self.is_testing = False
            self.is_calibrated = False
            self.update_button_states()
            
            self.statusbar.showMessage(f"Datos cargados: {len(data['t'])} puntos")
            
        except Exception as e:
            self.statusbar.showMessage(f"Error al cargar datos en el gráfico: {str(e)}")

    @Slot(int)
    def port_selected(self, index):
        """Manejar la selección de un puerto en el combo box"""
        # Si hay un puerto seleccionado y no está probando, habilitar el botón de conexión
        self.btn_connect.setEnabled(index >= 0 and not self.is_testing)
        
        # Si cambia el puerto y estaba conectado, desconectar
        if self.btn_connect.isChecked():
            self.btn_connect.setChecked(False)
            self.handle_connection()

    @Slot()
    def save_data(self):
        """Guardar datos actuales en CSV"""
        # Si hay una curva activa, guardar esa
        if self.graph_handler.active_recording_number is not None:
            self.file_handler.save_data_to_csv(self, self.graph_handler.display_data)
        else:
            # Si no hay curva activa pero hay datos en display_data
            if self.graph_handler.display_data['t']:
                self.file_handler.save_data_to_csv(self, self.graph_handler.display_data)
            else:
                self.statusbar.showMessage("No hay datos para guardar. Seleccione una prueba primero.")

    @Slot()
    def clear_data(self):
        """Limpiar el puerto serial y los gráficos"""
        if self.serial_handler and not self.is_testing:
            self.serial_handler.write_data("v")
        
        # Limpiar los gráficos
        self.graph_handler.clear_data()
        
        # Limpiar la lista de pruebas
        self.list_test.clear()
        self.test_counter = 0
        
        # Limpiar info de calidad
        self.current_quality = None

    def closeEvent(self, event):
        """Manejar el cierre de la ventana"""
        # Detener el timer
        self.port_timer.stop()
        
        # Desconectar si es necesario
        if self.btn_connect.isChecked():
            if self.serial_handler:
                self.serial_handler.stop_reading()
                self.serial_handler.close()
            
        # Aceptar el evento de cierre
        event.accept()