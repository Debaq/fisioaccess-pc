from PySide6.QtCore import QObject, Signal, QThread, Slot, QMutex, QWaitCondition
import serial
import serial.tools.list_ports
import re
import time


class SerialReaderThread(QThread):
    data_received = Signal(bytes)  # Cambiado de str a bytes

    def __init__(self, serial_port, mutex):
        super().__init__()
        self.serial_port = serial_port
        self.mutex = mutex  # Compartir el mutex
        self.is_running = False
        self.wait_condition = QWaitCondition()

    def run(self):
        self.is_running = True

        while self.is_running and self.serial_port and self.serial_port.is_open:
            try:
                # Usar un bloqueo con timeout para permitir escrituras
                self.mutex.lock()
                if self.serial_port.in_waiting:
                    # Leer bytes disponibles (máximo 256 bytes por lectura)
                    data = self.serial_port.read(min(self.serial_port.in_waiting, 256))
                    if data:
                        self.data_received.emit(data)
                self.mutex.unlock()

                # Pequeña pausa para no saturar el CPU y dar oportunidad a la escritura
                self.msleep(1)

            except Exception as e:
                if self.mutex.tryLock():
                    self.mutex.unlock()
                error_msg = f"Error en thread de lectura: {str(e)}"
                print(error_msg)
                # Emitir mensaje de error como bytes UTF-8
                self.data_received.emit(error_msg.encode('utf-8'))
                break

    def stop(self):
        print("Stopping thread...")
        self.is_running = False
        self.wait_condition.wakeAll()  # Despertar el thread si está esperando
        self.wait()
        print("Thread stopped")


class SerialHandler(QObject):
    data_received_serial = Signal(bytes)  # Cambiado de str a bytes
    write_status = Signal(str)
    error_occurred = Signal(str)

    def __init__(self, port=None, baudrate=115200):
        super().__init__()
        self.serial = None
        self.port = port
        self.baudrate = baudrate
        self.reader_thread = None
        self.mutex = QMutex()  # Mutex para sincronización
        self.write_timeout = 1000  # timeout en ms para escritura

    def get_available_ports(self):
        ports = [port.device for port in serial.tools.list_ports.comports()]
        acm_ports = [port for port in ports if re.search(r'ACM\d+$', port)]
        return acm_ports
        
    def open(self):
        try:
            print(f"Intentando abrir puerto {self.port}")
            self.serial = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                timeout=1
            )
            print(f"Puerto abierto exitosamente: {self.serial.is_open}")
            return True
        except serial.SerialException as e:
            error_msg = f"Error al abrir puerto {self.port}: {str(e)}"
            self.error_occurred.emit(error_msg)
            raise Exception(error_msg)
            
    def close(self):
        print("Cerrando conexión serial...")
        self.stop_reading()
        if self.serial and self.serial.is_open:
            self.serial.close()
            print("Conexión serial cerrada")
            
    def start_reading(self):
        if not self.serial or not self.serial.is_open:
            error_msg = "Puerto serial no está abierto"
            self.error_occurred.emit(error_msg)
            raise Exception(error_msg)
            
        if self.reader_thread is None:
            self.reader_thread = SerialReaderThread(self.serial, self.mutex)
            self.reader_thread.data_received.connect(self.handle_received_data)
            self.reader_thread.start()
            
            time.sleep(0.1)
            if self.reader_thread.isRunning():
                return "Lectura iniciada correctamente"
            else:
                return "Error: Thread no se inició correctamente"
        return "Thread ya existe"

    @Slot(bytes)
    def handle_received_data(self, data):
        """Método intermedio para debug de señales"""
        self.data_received_serial.emit(data)
    
    def stop_reading(self):
        if self.reader_thread:
            print("Deteniendo thread de lectura...")
            self.reader_thread.stop()
            self.reader_thread = None
            print("Thread detenido y eliminado")

    def write_data(self, data, add_newline=True):
        """
        Envía datos por el puerto serial de manera thread-safe.
        
        Args:
            data (str): Datos a enviar
            add_newline (bool): Si True, agrega un salto de línea al final
        
        Returns:
            bool: True si el envío fue exitoso, False en caso contrario
        """
        if not self.serial or not self.serial.is_open:
            self.error_occurred.emit("Puerto serial no está abierto")
            return False

        try:
            # Preparar los datos
            if add_newline and not data.endswith('\n'):
                data += '\n'
            
            data_bytes = data.encode()
            return self.write_bytes(data_bytes)

        except Exception as e:
            error_msg = f"Error preparando datos: {str(e)}"
            self.error_occurred.emit(error_msg)
            return False

    def write_bytes(self, data_bytes):
        """
        Envía bytes por el puerto serial de manera thread-safe.
        
        Args:
            data_bytes (bytes): Datos en bytes a enviar
        
        Returns:
            bool: True si el envío fue exitoso, False en caso contrario
        """
        if not self.serial or not self.serial.is_open:
            self.error_occurred.emit("Puerto serial no está abierto")
            return False

        try:
            # Intentar obtener el lock con timeout
            if not self.mutex.tryLock(self.write_timeout):
                self.error_occurred.emit("Timeout esperando para escribir")
                return False

            try:
                # Escribir datos
                bytes_written = self.serial.write(data_bytes)
                self.serial.flush()
                
                # Emitir estado
                self.write_status.emit(f"Enviados {bytes_written} bytes exitosamente")
                return True

            finally:
                # Siempre liberar el mutex
                self.mutex.unlock()

        except Exception as e:
            error_msg = f"Error escribiendo datos: {str(e)}"
            self.error_occurred.emit(error_msg)
            return False