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
        print("\nIniciando conexión de señales...")
        
        # Verificar que el objeto serial_handler existe
        print(f"Estado de serial_handler: {self.serial_handler}")
        print(f"serial_handler tiene señal data_received: {hasattr(self.serial_handler, 'data_received')}")
        
        # Conectar el botón de conexión
        self.btn_connect.clicked.connect(self.handle_connection)
        print("Señal de botón connect conectada")
        
        # Conectar el cambio de selección del combo box
        self.serial_list.currentIndexChanged.connect(self.port_selected)
        print("Señal de combo box conectada")

        # Verificar la conexión de señales del serial_handler
        try:
            # Desconectar primero para evitar conexiones duplicadas
            try:
                self.serial_handler.data_received.disconnect(self.print_info)
            except:
                pass
            
            # Reconectar la señal
            self.serial_handler.data_received.connect(self.print_info)
            print("Señal data_received conectada exitosamente a print_info")
        except Exception as e:
            print(f"Error al conectar serial_handler.data_received: {str(e)}")

        # Verificar la conexión del data_handler
        try:
            self.data_handler.new_data.connect(self.graph_handler.update_data)
            print("Señal new_data conectada exitosamente a graph_handler")
        except Exception as e:
            print(f"Error al conectar data_handler.new_data: {str(e)}")
        
        self.btn_start.setEnabled(False)
        self.btn_start.clicked.connect(self.start_read)
        print("Señal de botón start conectada")

        print("Conexión de señales completada\n")

    @Slot()
    def handle_connection(self):
        """Manejar la conexión/desconexión del puerto serial"""
        print("\nManejando conexión...")
        if self.btn_connect.isChecked():
            try:
                port = self.serial_list.currentText()
                print(f"Intentando conectar a puerto: {port}")
                
                # Crear nueva instancia de SerialHandler
                self.serial_handler = SerialHandler(port=port)
                
                # Reconectar la señal data_received
                try:
                    self.serial_handler.data_received.disconnect(self.print_info)
                except:
                    pass
                self.serial_handler.data_received.connect(self.print_info)
                print("Señal data_received reconectada después de crear nuevo SerialHandler")
                
                if self.serial_handler.open():
                    print("Conexión exitosa")
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
            # Código de desconexión...
            pass

    @Slot()
    def start_read(self):
        print("\nIniciando lectura...")
        try:
            result = self.serial_handler.start_reading()
            print(f"Resultado de start_reading: {result}")
            # Verificar estado del thread
            if self.serial_handler.reader_thread:
                print(f"Thread estado - isRunning: {self.serial_handler.reader_thread.isRunning()}")
            else:
                print("Thread no fue creado")
        except Exception as e:
            print(f"Error al iniciar lectura: {str(e)}")

    @Slot(str)
    def print_info(self, data):
        print(f"\nMainWindow.print_info recibido: {data}")

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
            self.serial_handler.stop_reading()
            self.serial_handler.close()
            
        # Aceptar el evento de cierre
        event.accept()