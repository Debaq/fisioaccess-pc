from PySide6.QtCore import QObject, Signal, QThread
import serial
import serial.tools.list_ports
import re


class SerialHandler(QObject):
    data_received = Signal(str)  # Señal para enviar datos a la interfaz

    def __init__(self, port=None, baudrate=115200):
        super().__init__()
        self.serial = None
        self.is_reading = False
        self.port = port
        self.baudrate = baudrate
        self.read_thread = None
        

    def get_available_ports(self):
        """Obtiene lista de puertos disponibles que terminan en ACM seguido de un número"""
        all_ports = [port.device for port in serial.tools.list_ports.comports()]
        # Filtra usando regex para encontrar puertos que terminan en ACM seguido de cualquier número
        acm_ports = [port for port in all_ports if re.search(r'ACM\d+$', port)]
        return acm_ports
        
    def open(self):
        """Abre la conexión serial"""
               
        try:
            self.serial = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                timeout=1
            )
            return True
        
        except serial.SerialException as e:
            raise Exception(f"Error al abrir puerto {self.port}: {str(e)}")
            
    def close(self):
        """Cierra la conexión serial"""
        self.stop_reading()
        if self.serial and self.serial.is_open:
            self.serial.close()
            
    def start_reading(self):
        """Inicia la lectura de datos en un hilo separado"""
        if not self.serial or not self.serial.is_open:
            raise Exception("Puerto serial no está abierto")
            
        self.is_reading = True
        self.read_thread = QThread()
        self.moveToThread(self.read_thread)
        self.read_thread.started.connect(self._read_loop)
        self.read_thread.start()
        return "Estamos grabando no se que te pasa!"
        
    def stop_reading(self):
        """Detiene la lectura de datos"""
        self.is_reading = False
        if self.read_thread:
            self.read_thread.quit()
            self.read_thread.wait()
    
    def read_line(self):
        return self.serial.readline().decode()

    def _read_loop(self):
        """Loop principal de lectura"""
        while self.is_reading:
            try:
                data = self.serial.readline()

                self.data_received.emit(data)
            except Exception as e:
                print(f"Error leyendo datos: {str(e)}")