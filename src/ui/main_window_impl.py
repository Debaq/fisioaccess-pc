from PySide6.QtWidgets import QMainWindow, QPushButton
from PySide6.QtCore import QTimer, Slot
import serial.tools.list_ports
from .main_window import Ui_Main
from serial_comm.serial_handler import SerialHandler  
from serial_comm.SerialDataHandler import SerialDataHandler
#from utils.GraphHandler import GraphHandler
from utils.FileHandler import FileHandler

from utils.SpirometryGraphManager import SpirometryGraphManager
from utils.ECGGraphManager import ECGGraphManager

from utils.DeviceManager import DeviceManager

class MainWindow(QMainWindow, Ui_Main):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        
        # Inicializar DeviceManager ANTES de otros componentes
        self.device_manager = DeviceManager()
        
        # Iniciar otros componentes
        self.file_handler = FileHandler()
        self.serial_handler = SerialHandler()
        self.data_handler = SerialDataHandler()
        
        # Inicializar gráficos pero no los agregues al layout aún
        self.spiro_graph = SpirometryGraphManager()
        self.ecg_graph = ECGGraphManager()
        
        # Variable para rastrear el tipo de dispositivo actual
        self.current_device_type = None
        
        # Configurar otros componentes
        self.port_timer = QTimer()
        self.port_timer.timeout.connect(self.update_port_list)
        self.port_timer.start(1000)
        
        self.available_ports = []
        
        # Conectar señales
        self.connect_signals()
        self.update_port_list()

    def reconnect_graph(self):
        button = self.sender()
        self.limpiar_layout(self.graph_layout)
        if button.objectName() == "btn_test_ecg":
            self.graph_layout.addWidget(self.ecg_graph)
        elif button.objectName() == "btn_test_spiro":
            self.graph_layout.addWidget(self.spiro_graph)  # CORREGIDO

    def limpiar_layout(self, layout):
        """Limpiar widgets del layout sin destruirlos"""
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.setParent(None)

    def connect_signals(self):
            """Conectar todas las señales necesarias"""
            
            # Señales del DeviceManager (NUEVAS)
            self.device_manager.device_detected.connect(self.on_device_detected)
            self.device_manager.device_connected.connect(self.on_device_connected)
            self.device_manager.device_disconnected.connect(self.on_device_disconnected)
            self.device_manager.request_tab_switch.connect(self.switch_to_device_tab)
            self.device_manager.request_tab_disable.connect(self.disable_device_tabs)
            
            # Conectar DataHandler con DeviceManager
            self.data_handler.device_detected.connect(self.device_manager.register_device)
            
            # Resto de señales existentes...
            self.file_handler.save_status.connect(self.statusbar.showMessage)
            self.file_handler.error_occurred.connect(self.statusbar.showMessage)
            self.file_handler.data_loaded.connect(self.load_data_to_graph)
            
            self.btn_save.clicked.connect(self.save_data)
            self.btn_open.clicked.connect(self.open_data)
            self.btn_reset.clicked.connect(self.reset_data)
        
            self.btn_connect.setCheckable(False)  # Manejar estado manualmente
            self.btn_connect.setText("Conectar")
            self.btn_connect.clicked.connect(self.handle_connection)
            self.serial_list.currentIndexChanged.connect(self.port_selected)
            
            # Conectar handler serial
            try:
                self.serial_handler.data_received_serial.disconnect()
            except:
                pass
            self.serial_handler.data_received_serial.connect(self.data_handler.analisis_input_serial)
            
            # Conectar datos a gráficos
            self.data_handler.new_data.connect(self.route_data_to_graph)
            
            self.btn_start.setEnabled(False)
            self.btn_start.clicked.connect(self.start_read)
            
            # Botones de prueba manual (mantener para testing)
            for objeto in self.findChildren(QPushButton):
                if objeto.objectName().startswith("btn_test_"):
                    objeto.clicked.connect(self.switch_device_manually)

            print("Conexión de señales completada")
    
    
    def switch_device_manually(self):
        """Cambiar dispositivo manualmente desde botones de prueba"""
        button = self.sender()
        
        device_mapping = {
            "btn_test_ecg": "ECG",
            "btn_test_spiro": "SPIRO",
            "btn_test_emg": "EMG", 
            "btn_test_eeg": "EEG"
        }
        
        device_type = device_mapping.get(button.objectName())
        if device_type and button.isEnabled():
            # Si el dispositivo no está registrado, crear uno para testing
            if device_type not in self.device_manager.devices:
                self.device_manager.register_device(device_type, {
                    'name': f'{device_type} (Modo Test)',
                    'port': None
                })
            
            # Cambiar a ese dispositivo
            self.device_manager.set_active_device(device_type)
            self.switch_to_device_tab(device_type)
    
    
    
    @Slot(str, dict)
    def on_device_detected(self, device_type, device_info):
        """Manejar detección de nuevo dispositivo"""
        print(f"📡 Dispositivo detectado: {device_type} - {device_info['name']}")
        self.statusbar.showMessage(f"Detectado: {device_info['name']} en {device_info['port']}")

    @Slot(str, dict) 
    def on_device_connected(self, device_type, device_info):
        """Manejar conexión de dispositivo"""
        print(f"🔌 Dispositivo conectado: {device_type}")
        self.statusbar.showMessage(f"Conectado: {device_info['name']}")
        
        # Actualizar combo box para mostrar dispositivo conectado
        self.update_device_combo_box()

    @Slot(str)
    def on_device_disconnected(self, device_type):
        """Manejar desconexión de dispositivo"""
        print(f"🔌 Dispositivo desconectado: {device_type}")
        self.statusbar.showMessage(f"Dispositivo {device_type} desconectado")

    @Slot(str)
    def switch_to_device_tab(self, device_type):
        """
        Cambiar automáticamente a la pestaña del dispositivo conectado.
        
        Args:
            device_type (str): Tipo de dispositivo
        """
        # Limpiar layout actual
        self.limpiar_layout(self.graph_layout)
        
        # Obtener y mostrar el graph manager correspondiente
        graph_manager = self.device_manager.get_device_graph_manager(device_type)
        if graph_manager:
            self.graph_layout.addWidget(graph_manager)
            self.current_device_type = device_type
            print(f"🎯 Cambiado a vista de {device_type}")
            
            # Actualizar título del panel
            capabilities = self.device_manager.get_device_capabilities(device_type)
            device_name = capabilities.get('name', device_type)
            self.label_7.setText(f"## Panel de Control - {device_name}")
            
            # Resaltar botón de prueba correspondiente
            self.highlight_active_test_button(device_type)
        else:
            self.statusbar.showMessage(f"Error: No se puede mostrar {device_type}")

    @Slot(list)
    def disable_device_tabs(self, disabled_device_types):
        """
        Deshabilitar pestañas/botones de dispositivos no conectados.
        
        Args:
            disabled_device_types (list): Lista de tipos de dispositivo a deshabilitar
        """
        # Mapeo de tipos a botones
        button_mapping = {
            "ECG": self.btn_test_ecg,
            "SPIRO": self.btn_test_spiro,
            "EMG": self.btn_test_emg,
            "EEG": self.btn_test_eeg
        }
        
        # Habilitar todos los botones primero
        for button in button_mapping.values():
            button.setEnabled(True)
            button.setStyleSheet("")  # Remover estilos especiales
            
        # Deshabilitar botones de dispositivos no conectados
        for device_type in disabled_device_types:
            button = button_mapping.get(device_type)
            if button:
                button.setEnabled(False)
                button.setStyleSheet("background-color: #f5f5f5; color: #9E9E9E;")

    def highlight_active_test_button(self, active_device_type):
        """Resaltar el botón del dispositivo activo"""
        button_mapping = {
            "ECG": self.btn_test_ecg,
            "SPIRO": self.btn_test_spiro, 
            "EMG": self.btn_test_emg,
            "EEG": self.btn_test_eeg
        }
        
        # Remover resaltado de todos los botones
        for button in button_mapping.values():
            if button.isEnabled():
                button.setStyleSheet("")
        
        # Resaltar botón activo
        active_button = button_mapping.get(active_device_type)
        if active_button and active_button.isEnabled():
            active_button.setStyleSheet("background-color: #3399ff; color: white; font-weight: bold;")

    def update_device_combo_box(self):
        """Actualizar combo box con dispositivos conectados"""
        connected_devices = self.device_manager.get_connected_devices()
        
        # Limpiar combo box
        current_selection = self.serial_list.currentText()
        self.serial_list.clear()
        
        # Agregar dispositivos conectados
        for device_type, device_info in connected_devices.items():
            display_text = f"{device_info['port']} - {device_info['name']}"
            self.serial_list.addItem(display_text)
        
        # Agregar puertos sin dispositivo identificado
        all_ports = self.serial_handler.get_available_ports()
        used_ports = [info['port'] for info in connected_devices.values() if info['port']]
        
        for port in all_ports:
            if port not in used_ports:
                self.serial_list.addItem(f"{port} - Puerto Serial")
        
        # Intentar mantener selección si existe
        if current_selection:
            index = self.serial_list.findText(current_selection)
            if index >= 0:
                self.serial_list.setCurrentIndex(index)


    
    
    @Slot(str, dict)
    def route_data_to_graph(self, device_type, data_dict):
        """Enrutar datos al gráfico correspondiente"""
        graph_manager = self.device_manager.get_device_graph_manager(device_type)
        if graph_manager:
            graph_manager.update_data(data_dict)
        else:
            print(f"⚠️  No hay graph manager para {device_type}")
    
    @Slot()
    def start_read(self):
        # Limpiar datos y resetear tiempo ANTES de iniciar
        current_widget = self.graph_layout.itemAt(0).widget() if self.graph_layout.count() > 0 else None
        if current_widget:
            current_widget.clear_data()  # Esto resetea initial_time = None
        
        # Cambiar botón
        self.btn_start.setText("Detener")
        self.btn_start.clicked.disconnect(self.start_read)
        self.btn_start.clicked.connect(self.stop_read)
        
        try:
            # Iniciar lectura y enviar comando start
            self.serial_handler.start_reading()
            self.serial_handler.write_data('{"cmd": "start", "params": {}}')
        except Exception as e:
            print(f"Error al iniciar: {str(e)}")

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
            self.btn_connect.setEnabled(len(ports) > 0)
            
            # Si no hay puertos y estaba conectado, desconectar
            if not ports and self.btn_connect.isChecked():
                self.btn_connect.setChecked(False)
                self.handle_connection()

    @Slot()
    def handle_connection(self):
        """Manejar la conexión/desconexión del puerto serial"""
        if not self.btn_connect.isChecked():  # Si NO está conectado, intentar conectar
            try:
                port_text = self.serial_list.currentText()
                
                if not port_text:
                    raise Exception("No hay puerto seleccionado")
                
                # EXTRAER SOLO EL PUERTO (antes del " - ") - CORREGIDO
                port = port_text.split(" - ")[0] if " - " in port_text else port_text
                
                # Configurar el puerto en el SerialHandler existente
                self.serial_handler.port = port
                
                # Reconectar la señal data_received
                try:
                    self.serial_handler.data_received_serial.disconnect()
                except:
                    pass
                self.serial_handler.data_received_serial.connect(self.data_handler.analisis_input_serial)
                
                # Intentar abrir la conexión
                if self.serial_handler.open():
                    self.statusbar.showMessage(f"Conectado a {port}")
                    self.serial_list.setEnabled(False)
                    self.btn_connect.setText("Desconectar")
                    self.btn_connect.setChecked(True)  # Marcar como conectado
                    self.btn_start.setEnabled(True)
                else:
                    raise Exception("No se pudo abrir el puerto")
                    
            except Exception as e:
                print(f"Error en conexión: {str(e)}")
                self.statusbar.showMessage(f"Error de conexión: {str(e)}")
                self.btn_connect.setChecked(False)
                self.btn_connect.setText("Conectar")
                self.serial_list.setEnabled(True)
                self.btn_start.setEnabled(False)
                
        else:  # Si está conectado, desconectar
            try:
                if self.serial_handler:
                    self.serial_handler.close()
                self.statusbar.showMessage("Desconectado")
                self.serial_list.setEnabled(True)
                self.btn_connect.setText("Conectar")
                self.btn_connect.setChecked(False)  # Marcar como desconectado
                self.btn_start.setEnabled(False)

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
            # Limpiar datos actuales - CORREGIDO para ambos gráficos
            self.spiro_graph.clear_data()
            self.ecg_graph.clear_data()
            
            # Actualizar los datos uno por uno para asegurar la actualización correcta del gráfico
            # Solo para el gráfico activo mostrado
            current_widget = self.graph_layout.itemAt(0).widget() if self.graph_layout.count() > 0 else None
            
            if current_widget == self.spiro_graph:
                for i in range(len(data['t'])):
                    new_data = {
                        't': data['t'][i],
                        'p': data['p'][i],
                        'f': data['f'][i],
                        'v': data['v'][i]
                    }
                    self.spiro_graph.update_data(new_data)
            
            # Deshabilitar botones de control serial
            self.btn_start.setEnabled(False)
            self.btn_connect.setEnabled(False)
            self.serial_list.setEnabled(False)
            
        except Exception as e:
            self.statusbar.showMessage(f"Error al cargar datos en el gráfico: {str(e)}")

    @Slot(int)
    def port_selected(self, index):
        """Manejar la selección de un puerto en el combo box"""
        # Si hay un puerto seleccionado, habilitar el botón de conexión
        self.btn_connect.setEnabled(index >= 0)
        
        # Si cambia el puerto y estaba conectado, desconectar
        if self.btn_connect.isChecked():
            self.btn_connect.setChecked(False)
            self.handle_connection()

    @Slot()
    def save_data(self):
        """Guardar datos actuales en CSV"""
        # Determinar cuál gráfico está activo
        current_widget = self.graph_layout.itemAt(0).widget() if self.graph_layout.count() > 0 else None
        
        if current_widget == self.spiro_graph:
            self.file_handler.save_data_to_csv(self, self.spiro_graph.data_manager.data)
        elif current_widget == self.ecg_graph:
            self.file_handler.save_data_to_csv(self, self.ecg_graph.data_manager.data)
        else:
            self.statusbar.showMessage("No hay gráfico activo para guardar")

    @Slot()
    def clear_data(self):
        """Limpiar el puerto serial y los gráficos"""
        self.serial_handler.write_data("v")

        # Limpiar ambos gráficos
        self.spiro_graph.clear_data()
        self.ecg_graph.clear_data()
        
    @Slot()
    def stop_read(self):
        # Detener grabación en ambos gráficos
        self.spiro_graph.stop_record()
        self.ecg_graph.stop_record()
        
        # Cambiar botón de vuelta a "Iniciar"
        self.btn_start.setText("Iniciar")
        self.btn_start.clicked.disconnect(self.stop_read)
        self.btn_start.clicked.connect(self.start_read)

    @Slot()
    def reset_data(self):
        """resetear la placa"""
        self.serial_handler.write_data("r")

        # Limpiar ambos gráficos
        self.spiro_graph.clear_data()
        self.ecg_graph.clear_data()

    def closeEvent(self, event):
        """Manejar el cierre de la ventana"""
        # Detener el timer
        self.port_timer.stop()
        
        # Desconectar si es necesario
        if self.btn_connect.isChecked():
            self.serial_handler.stop_reading()
            self.serial_handler.close()
            
        # Aceptar el evento de cierre
        event.accept()