from PySide6.QtCore import QObject, Signal, Slot
from .binary_protocol import BinaryProtocolDecoder, SensorDataProcessor

class SerialDataHandler(QObject):
    # Señal para nuevos datos procesados
    new_data = Signal(dict)
    # Señal para strings no estándar
    other_string = Signal(str)

    def __init__(self):
        super().__init__()
        # Inicializar decodificador de protocolo binario
        self.binary_decoder = BinaryProtocolDecoder()
        self.sensor_processor = SensorDataProcessor()

        # Modo de operación: 'binary' o 'csv' (para compatibilidad)
        self.mode = 'binary'

    def reset_volume(self):
        """Reinicia el cálculo de volumen acumulado"""
        self.sensor_processor.reset_volume()

    def set_pressure_calibration(self, offset_1, offset_2):
        """Establece los valores de calibración para los sensores de presión"""
        self.sensor_processor.set_pressure_calibration(offset_1, offset_2)

    @Slot(bytes)
    def analisis_input_binary(self, data_bytes):
        """
        Analizar datos binarios recibidos del puerto serial

        Args:
            data_bytes (bytes): Datos binarios del protocolo
        """
        try:
            # Agregar datos al buffer del decodificador
            self.binary_decoder.add_data(data_bytes)

            # Procesar todos los mensajes disponibles
            messages = self.binary_decoder.process_buffer()

            for message in messages:
                # Procesar mensaje y convertir a formato t, p, f, v
                data_dict = self.sensor_processor.process_message(message)

                if data_dict:
                    # Emitir los datos procesados
                    self.new_data.emit(data_dict)

        except Exception as e:
            error_msg = f"Error procesando datos binarios: {str(e)}"
            print(error_msg)
            self.other_string.emit(error_msg)

    def validate_time(self, time_value):
        """
        Validar el valor del tiempo.
        
        Args:
            time_value (float): Valor de tiempo a validar
            
        Returns:
            bool: True si el tiempo es válido, False en caso contrario
        """
        # Convertir a string para contar dígitos
        time_str = str(abs(time_value))
        
        # Remover el punto decimal para contar dígitos
        digits = time_str.replace('.', '')
        
        # Verificar que tenga al menos 4 dígitos
        return len(digits) >= 4
    
    @Slot(str)
    def analisis_input_serial(self, data_string):
        """Analizar datos recibidos del puerto serial"""
        try:
            # Limpiar el string
            data_string = data_string.strip()
            # Verificar si es el formato esperado
            values = data_string.split(',')
     
            if len(values) == 4:
                # Convertir valores a float
                t, p, f, v = map(float, values)
                
                # Validar el tiempo
               #if not self.validate_time(t):
               #     error_msg = f"Valor de tiempo inválido ({t}): debe tener al menos 4 dígitos"
               #     self.other_string.emit(error_msg)
               #     print(error_msg)
               #     return
                
                # Validar que los demás valores sean números razonables
                if not all(isinstance(x, (int, float)) for x in [p, f, v]):
                    raise ValueError("Valores no numéricos detectados")
                
                # Crear diccionario de datos
                data_dict = {
                    't': t,
                    'p': p,
                    'f': f,
                    'v': v
                }
                
                # Emitir los datos procesados
                self.new_data.emit(data_dict)
            else:
                # Si no es el formato esperado, enviar a otro analizador
                self.analizar_otro_string(data_string)
                
        except Exception as e:
            # Si hay error en el procesamiento, tratar como otro tipo de string
            self.analizar_otro_string(f"Error procesando: {data_string}, {str(e)}")
    
    def analizar_otro_string(self, string):
        """Procesar strings que no coinciden con el formato esperado"""
        print(f"String no estándar recibido: {string}")
        self.other_string.emit(string)