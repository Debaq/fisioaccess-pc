from PySide6.QtWidgets import QMainWindow
from PySide6.QtCore import QTimer, Slot
import serial.tools.list_ports
from .main_window import Ui_Main
from serial_comm.serial_handler import SerialHandler  # Asumiendo que cambiaste el nombre de la carpeta

class MainWindow(QMainWindow, Ui_Main):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        
        # Inicializar el manejador serial
        self.serial_handler = SerialHandler()
        
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
        
    def connect_signals(self):
        """Conectar todas las señales necesarias"""
        # Conectar el botón de conexión
        self.btn_connect.clicked.connect(self.handle_connection)
        
        # Conectar el cambio de selección del combo box
        self.serial_list.currentIndexChanged.connect(self.port_selected)
    
    @Slot()
    def update_port_list(self):
        """Actualizar la lista de puertos seriales disponibles"""
        # Obtener puertos actuales
        ports = [port.device for port in serial.tools.list_ports.comports()]
        
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
    def handle_connection(self):
        """Manejar la conexión/desconexión del puerto serial"""
        if self.btn_connect.isChecked():
            # Intentar conectar
            try:
                # Obtener el puerto seleccionado
                port = self.serial_list.currentText()
                if not port:
                    raise ValueError("No hay puerto seleccionado")
                
                # Configurar y abrir el puerto
                self.serial_handler = SerialHandler(port=port)
                if self.serial_handler.connect():
                    # Conexión exitosa
                    self.statusbar.showMessage(f"Conectado a {port}")
                    # Deshabilitar combo box mientras está conectado
                    self.serial_list.setEnabled(False)
                else:
                    raise Exception("No se pudo conectar al puerto")
                    
            except Exception as e:
                # Si hay error, mostrar mensaje y desmarcar el botón
                self.statusbar.showMessage(f"Error de conexión: {str(e)}")
                self.btn_connect.setChecked(False)
                self.serial_list.setEnabled(True)
        else:
            # Desconectar
            try:
                if self.serial_handler:
                    self.serial_handler.disconnect()
                self.statusbar.showMessage("Desconectado")
                # Habilitar combo box después de desconectar
                self.serial_list.setEnabled(True)
            except Exception as e:
                self.statusbar.showMessage(f"Error al desconectar: {str(e)}")
    
    def closeEvent(self, event):
        """Manejar el cierre de la ventana"""
        # Detener el timer
        self.port_timer.stop()
        
        # Desconectar si es necesario
        if self.btn_connect.isChecked():
            self.serial_handler.disconnect()
            
        # Aceptar el evento de cierre
        event.accept()