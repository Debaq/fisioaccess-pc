from PySide6.QtCore import QObject, Signal, QThread, Slot
import serial
import serial.tools.list_ports
import re
import time


class SerialReaderThread(QThread):
    data_received = Signal(str)

    def __init__(self, serial_port):
        super().__init__()
        self.serial_port = serial_port
        self.is_running = False
        print("Thread inicializado")  # Debug print

    def run(self):
        print("Thread iniciado")  # Debug print
        self.is_running = True
        counter = 0  # Contador para debug
        
        while self.is_running and self.serial_port and self.serial_port.is_open:
            try:
                # Debug print cada 100 iteraciones
                counter += 1
                if counter % 100 == 0:
                    print(f"Thread running... Loop count: {counter}")
                    print(f"Serial port status - Is open: {self.serial_port.is_open}")
                    print(f"Bytes waiting: {self.serial_port.in_waiting}")
                
                if self.serial_port.in_waiting:
                    data = self.serial_port.readline().decode().strip()
                    print(f"Datos leídos: {data}")  # Debug print
                    if data:
                        print("Emitiendo señal con datos")  # Debug print
                        self.data_received.emit(data)
                
            except Exception as e:
                error_msg = f"Error en thread de lectura: {str(e)}"
                print(error_msg)  # Debug print
                self.data_received.emit(error_msg)
                break
                
            self.msleep(100)  # Aumentado para mejor debugging

    def stop(self):
        print("Stopping thread...")  # Debug print
        self.is_running = False
        self.wait()
        print("Thread stopped")  # Debug print


class SerialHandler(QObject):
    data_received = Signal(str)

    def __init__(self, port=None, baudrate=115200):
        super().__init__()
        self.serial = None
        self.port = port
        self.baudrate = baudrate
        self.reader_thread = None
        print(f"SerialHandler inicializado - Puerto: {port}, Baudrate: {baudrate}")  # Debug print

    def get_available_ports(self):
        ports = [port.device for port in serial.tools.list_ports.comports()]
        acm_ports = [port for port in ports if re.search(r'ACM\d+$', port)]
        return acm_ports
        
    def open(self):
        try:
            print(f"Intentando abrir puerto {self.port}")  # Debug print
            self.serial = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                timeout=1
            )
            print(f"Puerto abierto exitosamente: {self.serial.is_open}")  # Debug print
            return True
        except serial.SerialException as e:
            error_msg = f"Error al abrir puerto {self.port}: {str(e)}"
            print(error_msg)  # Debug print
            raise Exception(error_msg)
            
    def close(self):
        print("Cerrando conexión serial...")  # Debug print
        self.stop_reading()
        if self.serial and self.serial.is_open:
            self.serial.close()
            print("Conexión serial cerrada")  # Debug print
            
    def start_reading(self):
        if not self.serial or not self.serial.is_open:
            error_msg = "Puerto serial no está abierto"
            print(error_msg)  # Debug print
            raise Exception(error_msg)
            
        if self.reader_thread is None:
            print("Creando nuevo thread de lectura")  # Debug print
            self.reader_thread = SerialReaderThread(self.serial)
            
            # Conectar señal con debug
            print("Conectando señales...")
            self.reader_thread.data_received.connect(self.handle_received_data)
            
            print("Iniciando thread...")
            self.reader_thread.start()
            
            # Verificar que el thread está corriendo
            time.sleep(0.1)  # Pequeña pausa para que el thread inicie
            if self.reader_thread.isRunning():
                print("Thread iniciado correctamente")
                return "Lectura iniciada correctamente"
            else:
                print("Error: Thread no está corriendo")
                return "Error: Thread no se inició correctamente"
        return "Thread ya existe"

    @Slot(str)
    def handle_received_data(self, data):
        """Método intermedio para debug de señales"""
        print(f"Datos recibidos en SerialHandler: {data}")
        self.data_received.emit(data)
    
    def stop_reading(self):
        if self.reader_thread:
            print("Deteniendo thread de lectura...")  # Debug print
            self.reader_thread.stop()
            self.reader_thread = None
            print("Thread detenido y eliminado")  # Debug print