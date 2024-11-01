from PySide6.QtCore import QObject, Signal, QThread
import serial
import serial.tools.list_ports
import re


class SerialReaderThread(QThread):
    data_received = Signal(str)

    def __init__(self, serial_port):
        super().__init__()
        self.serial_port = serial_port
        self.is_running = False

    def run(self):
        self.is_running = True
        while self.is_running and self.serial_port and self.serial_port.is_open:
            try:
                if self.serial_port.in_waiting:
                    data = self.serial_port.readline().decode().strip()
                    if data:
                        self.data_received.emit(data)
            except Exception as e:
                print(f"Error en thread de lectura: {str(e)}")
                break
            self.msleep(10)  # Pequeña pausa para no saturar el CPU

    def stop(self):
        self.is_running = False
        self.wait()

class SerialHandler(QObject):
    data_received = Signal(str)

    def __init__(self, port=None, baudrate=115200):
        super().__init__()
        self.serial = None
        self.port = port
        self.baudrate = baudrate
        self.reader_thread = None

    def get_available_ports(self):
        """Obtiene lista de puertos disponibles que terminan en ACM seguido de un número"""
        all_ports = [port.device for port in serial.tools.list_ports.comports()]
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
            
        if self.reader_thread is None:
            self.reader_thread = SerialReaderThread(self.serial)
            self.reader_thread.data_received.connect(self.data_received)
            self.reader_thread.start()
        return "Lectura iniciada correctamente"
        
    def stop_reading(self):
        """Detiene la lectura de datos"""
        if self.reader_thread:
            self.reader_thread.stop()
            self.reader_thread = None