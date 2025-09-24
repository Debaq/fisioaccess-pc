from PySide6.QtWidgets import QMainWindow, QPushButton
from PySide6.QtCore import QTimer, Slot
import serial.tools.list_ports
import json
from .main_window import Ui_Main
from serial_comm.serial_handler import SerialHandler  
from serial_comm.SerialDataHandler import SerialDataHandler
from utils.FileHandler import FileHandler
from utils.DeviceManager import DeviceManager

class MainWindow(QMainWindow, Ui_Main):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        
        # Iniciar metodos de guardado
        self.file_handler = FileHandler()
        
        # Inicializar el manejador serial
        self.serial_handler = SerialHandler()
        
        # Inicializar el manejador de datos con protocolo JSON
        self.data_handler = SerialDataHandler()
        
        # Inicializar el gestor de dispositivos
        self.device_manager = DeviceManager()

        # Configurar el timer para actualizar la lista de puertos
        self.port_timer = QTimer()
        self.port_timer.timeout.connect(self.update_port_list)
        self.port_timer.start(1000)  # Actualizar cada segundo
        
        # Lista para mantener track de los puertos disponibles
        self.available_ports = []
        
        # Dispositivo activo actual
        self.current_device_type = None
        
        # Conectar señales
        self.connect_signals()
        
        # Actualizar lista inicial de puertos
        self.update_port_list()

        # Conectar botones de prueba a reconexión de gráficos
        for objeto in self.findChildren(QPushButton):
            if objeto.objectName().startswith("btn_test_"):
                objeto.clicked.connect(self.switch_device_manually)

    def connect_signals(self):
        """Conectar todas las señales necesarias"""
        
        # Señales de archivo
        self.file_handler.save_status.connect(self.statusbar.showMessage)
        self.file_handler.error_occurred.connect(self.statusbar.showMessage)
        self.file_handler.data_loaded.connect(self.load_data_to_graph)
        
        # Botones de archivo
        self.btn_save.clicked.connect(self.save_data)
        self.btn_open.clicked.connect(self.open_data)
        
        # Botones de control
        self.btn_clear.clicked.connect(self.clear_data)
        self.btn_reset.clicked.connect(self.reset_data)
        self.btn_start.clicked.connect(self.start_read)
        
        # Señales de conexión serial
        self.btn_connect.clicked.connect(self.handle_connection)
        self.serial_list.currentIndexChanged.connect(self.port_selected)
        
        # Conectar señales del data_handler (protocolo JSON)
        self.data_handler.new_data.connect(self.handle_device_data)
        self.data_handler.device_detected.connect(self.device_manager.register_device)
        self.data_handler.device_status.connect(self.device_manager.update_device_status)
        self.data_handler.error_occurred.connect(self.handle_device_error)
        
        # Conectar serial_handler con data_handler
        try:
            self.serial_handler.data_received_serial.disconnect()
        except:
            pass
        self.serial_handler.data_received_serial.connect(self.data_handler.analisis_input_serial)
        
        # Señales del device_manager
        self.device_manager.device_added.connect(self.on_device_added)
        self.device_manager.device_removed.connect(self.on_device_removed)
        self.device_manager.active_device_changed.connect(self.on_active_device_changed)
        
        # Estado inicial de botones
        self.btn_start.setEnabled(False)
        
        print("Conexión de señales completada")

    @Slot(str, dict)
    def handle_device_data(self, device_type, data_dict):
        """
        Manejar datos recibidos de un dispositivo específico.
        
        Args:
            device_type (str): Tipo de dispositivo
            data_dict (dict): Datos recibidos
        """
        # Obtener el graph manager del dispositivo
        graph_manager = self.device_manager.get_device_graph_manager(device_type)
        
        if graph_manager:
            # Enviar datos al graph manager correspondiente
            graph_manager.update_data(data_dict)
        else:
            print(f"Warning: No hay graph manager para dispositivo {device_type}")

    @Slot(str, str)
    def handle_device_error(self, device_type, error_message):
        """
        Manejar errores de dispositivo.
        
        Args:
            device_type (str): Tipo de dispositivo
            error_message (str): Mensaje de error
        """
        status_msg = f"{device_type}: {error_message}"
        self.statusbar.showMessage(status_msg)
        print(f"Error en dispositivo {device_type}: {error_message}")

    @Slot(str, dict)
    def on_device_added(self, device_type, device_info):
        """
        Manejar adición de nuevo dispositivo.
        
        Args:
            device_type (str): Tipo de dispositivo
            device_info (dict): Información del dispositivo
        """
        print(f"Dispositivo detectado: {device_type} - {device_info['name']}")
        
        # Actualizar UI para mostrar dispositivo disponible
        self.update_device_combo()
        
        # Si no hay dispositivo activo, activar este
        if not self.current_device_type:
            self.switch_to_device(device_type)

    @Slot(str)
    def on_device_removed(self, device_type):
        """
        Manejar remoción de dispositivo.
        
        Args:
            device_type (str): Tipo de dispositivo removido
        """
        print(f"Dispositivo removido: {device_type}")
        self.update_device_combo()

    @Slot(str)
    def on_active_device_changed(self, device_type):
        """
        Manejar cambio de dispositivo activo.
        
        Args:
            device_type (str): Nuevo tipo de dispositivo activo
        """
        print(f"Dispositivo activo cambiado a: {device_type}")
        self.current_device_type = device_type
        self.update_ui_for_device(device_type)

    def switch_to_device(self, device_type):
        """
        Cambiar al dispositivo especificado.
        
        Args:
            device_type (str): Tipo de dispositivo
        """
        # Limpiar layout actual
        self.limpiar_layout(self.graph_layout)
        
        # Establecer como dispositivo activo
        self.device_manager.set_active_device(device_type)
        
        # Obtener graph manager y agregarlo al layout
        graph_manager = self.device_manager.get_active_graph_manager()
        if graph_manager:
            self.graph_layout.addWidget(graph_manager)
            self.current_device_type = device_type
            self.update_ui_for_device(device_type)
        else:
            self.statusbar.showMessage(f"Error: No se puede mostrar {device_type}")

    def switch_device_manually(self):
        """Cambiar dispositivo manualmente desde botones de prueba"""
        button = self.sender()
        
        # Mapear botones a tipos de dispositivo
        device_mapping = {
            "btn_test_ecg": "ECG",
            "btn_test_spiro": "SPIRO", 
            "btn_test_emg": "EMG",
            "btn_test_eeg": "EEG"
        }
        
        device_type = device_mapping.get(button.objectName())
        if device_type:
            # Si el dispositivo no está registrado, crear uno virtual para testing
            if device_type not in self.device_manager.devices:
                self.device_manager.register_device(device_type, {
                    'name': f'{device_type} (Modo Test)',
                    'port': None
                })
            
            self.switch_to_device(device_type)

    def update_ui_for_device(self, device_type):
        """
        Actualizar UI específicamente para el tipo de dispositivo.
        
        Args:
            device_type (str): Tipo de dispositivo
        """
        # Habilitar/deshabilitar botones según dispositivo
        device_capabilities = self.device_manager.get_device_capabilities(device_type)
        
        # Actualizar título del panel
        device_name = device_capabilities.get('name', device_type)
        self.label_7.setText(f"## Panel de Control - {device_name}")
        
        # Actualizar configuración específica del dispositivo
        self.update_device_specific_controls(device_type, device_capabilities)
        
        # Resaltar botón de prueba correspondiente
        self.highlight_active_test_button(device_type)

    def update_device_specific_controls(self, device_type, capabilities):
        """
        Actualizar controles específicos para el tipo de dispositivo.
        
        Args:
            device_type (str): Tipo de dispositivo
            capabilities (dict): Capacidades del dispositivo
        """
        # Configurar sampling rate si está disponible
        if 'sampling_rate' in capabilities:
            self.spinBox_2.setValue(capabilities['sampling_rate'])
        
        # Otras configuraciones específicas por dispositivo
        if device_type == 'ECG':
            # Mostrar controles específicos de ECG
            self.spinBox.setVisible(True)  # Duración
            self.horizontalSlider.setVisible(True)  # Amplitud
            # Ocultar controles no relevantes
            # ...
        elif device_type == 'SPIRO':
            # Mostrar controles específicos de espirometría
            # ...
            pass

    def highlight_active_test_button(self, device_type):
        """
        Resaltar el botón de prueba del dispositivo activo.
        
        Args:
            device_type (str): Tipo de dispositivo activo
        """
        # Mapeo inverso
        button_mapping = {
            "ECG": "btn_test_ecg",
            "SPIRO": "btn_test_spiro",
            "EMG": "btn_test_emg", 
            "EEG": "btn_test_eeg"
        }
        
        # Resetear estilos de todos los botones
        for btn_name in button_mapping.values():
            button = getattr(self, btn_name, None)
            if button:
                button.setStyleSheet("")
        
        # Resaltar botón activo
        active_btn_name = button_mapping.get(device_type)
        if active_btn_name:
            active_button = getattr(self, active_btn_name, None)
            if active_button:
                active_button.setStyleSheet("background-color: #3399ff; color: white;")

    def update_device_combo(self):
        """Actualizar combo box con dispositivos conectados"""
        # Guardar puerto seleccionado actualmente
        current_port = self.serial_list.currentText()
        
        # Limpiar combo box
        self.serial_list.clear()
        
        # Obtener puertos seriales disponibles
        available_ports = self.serial_handler.get_available_ports()
        
        # Obtener dispositivos conectados
        connected_devices = self.device_manager.get_connected_devices()
        
        # Agregar puertos con información de dispositivos si está disponible
        for port in available_ports:
            # Buscar si hay un dispositivo asociado a este puerto
            device_info = None
            for dev_type, dev_info in connected_devices.items():
                if dev_info.get('port') == port:
                    device_info = dev_info
                    break
            
            if device_info:
                # Puerto con dispositivo identificado
                combo_text = f"{port} - {device_info['name']}"
            else:
                # Puerto sin dispositivo identificado
                combo_text = f"{port} - Dispositivo Desconocido"
            
            self.serial_list.addItem(combo_text)
        
        # Intentar mantener puerto seleccionado
        if current_port:
            for i in range(self.serial_list.count()):
                if current_port in self.serial_list.itemText(i):
                    self.serial_list.setCurrentIndex(i)
                    break
        
        # Actualizar disponibilidad de botones
        self.available_ports = available_ports
        self.btn_connect.setEnabled(len(available_ports) > 0)

    def update_port_list(self):
        """Actualizar la lista de puertos seriales disponibles"""
        ports = self.serial_handler.get_available_ports()
        
        # Si la lista cambió, actualizar combo
        if ports != self.available_ports:
            self.update_device_combo()
            
            # Si no hay puertos y estaba conectado, desconectar
            if not ports and self.btn_connect.isChecked():
                self.btn_connect.setChecked(False)
                self.handle_connection()

    @Slot()
    def handle_connection(self):
        """Manejar la conexión/desconexión del puerto serial"""
        if self.btn_connect.isChecked():
            try:
                # Obtener puerto seleccionado (extraer solo el nombre del puerto)
                combo_text = self.serial_list.currentText()
                port = combo_text.split(' - ')[0] if ' - ' in combo_text else combo_text
                
                # Crear nueva instancia de SerialHandler
                self.serial_handler = SerialHandler(port=port)
                
                # Reconectar señales
                try:
                    self.serial_handler.data_received_serial.disconnect()
                except:
                    pass
                self.serial_handler.data_received_serial.connect(self.data_handler.analisis_input_serial)
                
                if self.serial_handler.open():
                    self.statusbar.showMessage(f"Conectado a {port}")
                    self.serial_list.setEnabled(False)
                    self.btn_connect.setText("Desconectar")
                    self.btn_start.setEnabled(True)
                else:
                    raise Exception("No se pudo conectar al puerto")
                    
            except Exception as e:
                print(f"Error en conexión: {str(e)}")
                self.statusbar.showMessage(f"Error de conexión: {str(e)}")
                self.btn_connect.setChecked(False)
                self.serial_list.setEnabled(True)
        else:
            try:
                if self.serial_handler:
                    self.serial_handler.close()
                self.statusbar.showMessage("Desconectado")
                self.serial_list.setEnabled(True)
                self.btn_connect.setText("Conectar")
                self.btn_start.setEnabled(False)

            except Exception as e:
                self.statusbar.showMessage(f"Error al desconectar: {str(e)}")

    @Slot()
    def start_read(self):
        """Iniciar lectura de datos"""
        self.btn_start.setText("Detener")
        self.btn_start.clicked.disconnect(self.start_read)
        self.btn_start.clicked.connect(self.stop_read)
        
        try:
            self.serial_handler.start_reading()
            
            # Enviar comando de inicio al dispositivo activo si existe
            if self.current_device_type:
                start_cmd = {"cmd": "start", "params": {}}
                self.device_manager.send_command_to_active(start_cmd)
                
        except Exception as e:
            print(f"Error al iniciar lectura: {str(e)}")
            self.statusbar.showMessage(f"Error: {str(e)}")

    @Slot()
    def stop_read(self):
        """Detener lectura de datos"""
        self.btn_start.setText("Iniciar")
        self.btn_start.clicked.disconnect(self.stop_read)
        self.btn_start.clicked.connect(self.start_read)
        
        # Detener grabación en el dispositivo activo
        active_manager = self.device_manager.get_active_graph_manager()
        if active_manager:
            active_manager.stop_record()
        
        # Enviar comando de parada al dispositivo
        if self.current_device_type:
            stop_cmd = {"cmd": "stop", "params": {}}
            self.device_manager.send_command_to_active(stop_cmd)

    @Slot()
    def clear_data(self):
        """Limpiar datos del dispositivo activo"""
        # Enviar comando de limpieza al dispositivo
        if self.current_device_type:
            clear_cmd = {"cmd": "reset", "params": {"type": "data"}}
            self.device_manager.send_command_to_active(clear_cmd)
        
        # Limpiar gráficos localmente
        active_manager = self.device_manager.get_active_graph_manager()
        if active_manager:
            active_manager.clear_data()

    @Slot()
    def reset_data(self):
        """Reset completo del dispositivo activo"""
        # Enviar comando de reset al dispositivo
        if self.current_device_type:
            reset_cmd = {"cmd": "reset", "params": {"type": "full"}}
            self.device_manager.send_command_to_active(reset_cmd)
        
        # Limpiar gráficos localmente
        active_manager = self.device_manager.get_active_graph_manager()
        if active_manager:
            active_manager.clear_data()

    @Slot()
    def save_data(self):
        """Guardar datos del dispositivo activo"""
        active_manager = self.device_manager.get_active_graph_manager()
        if active_manager and hasattr(active_manager, 'data_manager'):
            self.file_handler.save_data_to_csv(self, active_manager.data_manager.data)
        else:
            self.statusbar.showMessage("No hay datos para guardar")

    @Slot()
    def open_data(self):
        """Abrir y cargar datos desde un archivo"""
        # Desconectar del puerto serial si está conectado
        if self.btn_connect.isChecked():
            self.btn_connect.setChecked(False)
            self.handle_connection()
        
        self.file_handler.open_data_file(self)

    @Slot(dict)
    def load_data_to_graph(self, data):
        """
        Cargar datos en el gráfico del dispositivo activo.
        
        Args:
            data (dict): Diccionario con los datos cargados
        """
        try:
            active_manager = self.device_manager.get_active_graph_manager()
            if not active_manager:
                # Si no hay dispositivo activo, asumir SPIRO para compatibilidad
                self.switch_to_device('SPIRO')
                active_manager = self.device_manager.get_active_graph_manager()
            
            if active_manager:
                # Limpiar datos actuales
                active_manager.clear_data()
                
                # Cargar datos uno por uno
                for i in range(len(data['t'])):
                    new_data = {
                        't': data['t'][i],
                        'p': data['p'][i] if 'p' in data else 0,
                        'f': data['f'][i] if 'f' in data else 0,
                        'v': data['v'][i] if 'v' in data else 0
                    }
                    active_manager.update_data(new_data)
                
                # Deshabilitar controles durante visualización de archivo
                self.btn_start.setEnabled(False)
                self.btn_connect.setEnabled(False)
                self.serial_list.setEnabled(False)
            
        except Exception as e:
            self.statusbar.showMessage(f"Error al cargar datos: {str(e)}")

    @Slot(int)
    def port_selected(self, index):
        """Manejar la selección de un puerto en el combo box"""
        self.btn_connect.setEnabled(index >= 0)
        
        # Si cambia el puerto y estaba conectado, desconectar
        if self.btn_connect.isChecked():
            self.btn_connect.setChecked(False)
            self.handle_connection()

    def limpiar_layout(self, layout):
        """Limpiar layout sin destruir widgets"""
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.setParent(None)

    def closeEvent(self, event):
        """Manejar el cierre de la ventana"""
        # Detener timers
        self.port_timer.stop()
        if hasattr(self.device_manager, 'cleanup_timer'):
            self.device_manager.cleanup_timer.stop()
        
        # Desconectar si es necesario
        if self.btn_connect.isChecked():
            if hasattr(self.serial_handler, 'stop_reading'):
                self.serial_handler.stop_reading()
            self.serial_handler.close()
        
        event.accept()