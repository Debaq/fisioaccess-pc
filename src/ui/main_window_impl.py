from PySide6.QtWidgets import QMainWindow
from PySide6.QtCore import QTimer, Slot
import serial.tools.list_ports
from .main_window import Ui_Main
from serial_comm.serial_handler import SerialHandler  
from serial_comm.SerialDataHandler import SerialDataHandler
from utils.GraphHandler import GraphHandler

class MainWindow(QMainWindow, Ui_Main):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        
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
        
    def connect_signals(self):
        """Conectar todas las señales necesarias"""
        # Conectar el botón de conexión
        self.btn_connect.clicked.connect(self.handle_connection)
        
        # Conectar el cambio de selección del combo box
        self.serial_list.currentIndexChanged.connect(self.port_selected)

        #conectar entrada serial al handler
        self.serial_handler.data_received.connect(self.print_info)

        # Conectar el manejador de datos con los gráficos
        self.data_handler.new_data.connect(self.graph_handler.update_data)
        
        # Conectar el boton iniciar al thread para que lea los datos
        self.btn_start.setEnabled(False)
        self.btn_start.clicked.connect(self.serial_handler.start_reading)

        # Conectar el manejador serial con el procesamiento de datos
        if hasattr(self.serial_handler, 'data_received'):
            self.serial_handler.data_received.connect(self.data_handler.analisis_input_serial)
    
    @Slot()
    def print_info(self, data):
        print(f"estamos recibiendo lo siguiente: {data}")

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
                if self.serial_handler.open():
                    # Conexión exitosa
                    self.statusbar.showMessage(f"Conectado a {port}")
                    # Deshabilitar combo box mientras está conectado
                    self.serial_list.setEnabled(False)
                    self.btn_connect.setText("Desconectar")
                    self.btn_start.setEnabled(True)
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
                    self.serial_handler.close()
                self.statusbar.showMessage("Desconectado")
                # Habilitar combo box después de desconectar
                self.serial_list.setEnabled(True)
                self.btn_connect.setText("Conectar")

            except Exception as e:
                self.statusbar.showMessage(f"Error al desconectar: {str(e)}")
    @Slot()
    def clear_plots(self):
        """Limpiar los gráficos"""
        self.graph_handler.clear_data()
    
    def closeEvent(self, event):
        """Manejar el cierre de la ventana"""
        # Detener el timer
        self.port_timer.stop()
        
        # Desconectar si es necesario
        if self.btn_connect.isChecked():
            self.serial_handler.disconnect()
            
        # Aceptar el evento de cierre
        event.accept()