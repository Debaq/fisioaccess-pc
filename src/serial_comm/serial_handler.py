from PySide6.QtCore import QObject, Signal, QThread
import serial
import serial.tools.list_ports

class SerialHandler(QObject):
    data_received = Signal(list)  # Señal para enviar datos a la interfaz

    def __init__(self, port=None, baudrate=115200):
        super().__init__()
        self.serial = None
        self.is_reading = False
        self.port = port
        self.baudrate = baudrate
        self.read_thread = None
        
    def get_available_ports(self):
        """Obtiene lista de puertos disponibles"""
        return [port.device for port in serial.tools.list_ports.comports()]
        
    def open(self, port=None):
        """Abre la conexión serial"""
        if port:
            self.port = port
            
        if self.port is None:
            # Si no se especifica puerto, intentar con el primero disponible
            available_ports = self.get_available_ports()
            if available_ports:
                self.port = available_ports[0]
            else:
                raise Exception("No hay puertos seriales disponibles")
                
        try:
            self.serial = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                timeout=1
            )
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
        
    def stop_reading(self):
        """Detiene la lectura de datos"""
        self.is_reading = False
        if self.read_thread:
            self.read_thread.quit()
            self.read_thread.wait()
            
    def _read_loop(self):
        """Loop principal de lectura"""
        while self.is_reading:
            if self.serial and self.serial.in_waiting:
                try:
                    data = self.serial.readline().decode().strip()
                    # Aquí procesas los datos según tu protocolo
                    # y emites la señal data_received
                    self.data_received.emit([float(data)])
                except Exception as e:
                    print(f"Error leyendo datos: {str(e)}")