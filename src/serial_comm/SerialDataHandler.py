from PySide6.QtCore import QObject, Signal, Slot
import json
import time

class SerialDataHandler(QObject):
    # Señales para diferentes tipos de mensajes
    new_data = Signal(str, dict)  # (device_type, data_dict)
    device_detected = Signal(str, dict)  # (device_type, device_info)
    command_response = Signal(str, dict)  # (device_type, response)
    device_status = Signal(str, dict)  # (device_type, status)
    error_occurred = Signal(str, str)  # (device_type, error_message)
    # Señal para strings no estándar (compatibilidad)
    other_string = Signal(str)
    
    def __init__(self):
        super().__init__()
        # Registry de dispositivos detectados
        self.detected_devices = {}
        
        # Mapeo de tipos de dispositivos conocidos
        self.device_types = {
            'SPIRO': 'Espirometría',
            'ECG': 'Electrocardiograma',
            'EMG': 'Electromiografía', 
            'EEG': 'Electroencefalografía'
        }
    
    def validate_json_message(self, message_dict):
        """
        Validar estructura básica del mensaje JSON.
        
        Args:
            message_dict (dict): Mensaje decodificado
            
        Returns:
            bool: True si el mensaje es válido
        """
        required_fields = ['type', 'device', 'timestamp']
        
        # Verificar campos requeridos
        for field in required_fields:
            if field not in message_dict:
                return False
        
        # Verificar tipos de datos
        if not isinstance(message_dict['timestamp'], (int, float)):
            return False
            
        # Verificar tipo de mensaje válido
        valid_types = ['data', 'response', 'status', 'error']
        if message_dict['type'] not in valid_types:
            return False
            
        # Verificar dispositivo conocido
        if message_dict['device'] not in self.device_types:
            return False
            
        return True
    
    def validate_time(self, time_value):
        """
        Validar el valor del tiempo.
        
        Args:
            time_value (float): Valor de tiempo a validar
            
        Returns:
            bool: True si el tiempo es válido
        """
        # Verificar que sea un número positivo razonable
        if not isinstance(time_value, (int, float)):
            return False
            
        # Verificar rango razonable (timestamp en ms)
        if time_value < 0 or time_value > 9999999999999:  # Año 2286 aprox
            return False
            
        return True
    
    @Slot(str)
    def analisis_input_serial(self, data_string):
        """Analizar datos recibidos del puerto serial"""
        try:
            # Limpiar el string
            data_string = data_string.strip()
            
            # Intentar parsear como JSON primero
            if self.try_parse_json(data_string):
                return
                
            # Si no es JSON, intentar formato CSV legacy
            if self.try_parse_csv_legacy(data_string):
                return
                
            # Si no coincide con ningún formato, tratar como string no estándar
            self.analizar_otro_string(data_string)
                
        except Exception as e:
            error_msg = f"Error procesando mensaje: {data_string}, {str(e)}"
            self.error_occurred.emit("UNKNOWN", error_msg)
    
    def try_parse_json(self, data_string):
        """
        Intentar parsear el string como mensaje JSON.
        
        Args:
            data_string (str): String a parsear
            
        Returns:
            bool: True si se parseó exitosamente
        """
        try:
            # Verificar si empieza con { (indicador básico de JSON)
            if not data_string.startswith('{'):
                return False
                
            # Intentar decodificar JSON
            message = json.loads(data_string)
            
            # Validar estructura
            if not self.validate_json_message(message):
                error_msg = f"Mensaje JSON con estructura inválida: {data_string}"
                self.error_occurred.emit(message.get('device', 'UNKNOWN'), error_msg)
                return True  # Se parseó pero era inválido
            
            # Validar timestamp
            if not self.validate_time(message['timestamp']):
                error_msg = f"Timestamp inválido en mensaje: {message['timestamp']}"
                self.error_occurred.emit(message['device'], error_msg)
                return True
            
            # Procesar según tipo de mensaje
            self.process_json_message(message)
            return True
            
        except json.JSONDecodeError:
            # No es JSON válido
            return False
        except Exception as e:
            error_msg = f"Error procesando JSON: {str(e)}"
            self.error_occurred.emit("UNKNOWN", error_msg)
            return True
    
    def process_json_message(self, message):
        """
        Procesar mensaje JSON válido según su tipo.
        
        Args:
            message (dict): Mensaje JSON decodificado
        """
        device_type = message['device']
        msg_type = message['type']
        
        # Registrar dispositivo si no existe
        if device_type not in self.detected_devices:
            self.detected_devices[device_type] = {
                'name': self.device_types[device_type],
                'last_seen': time.time(),
                'connected': True
            }
            self.device_detected.emit(device_type, self.detected_devices[device_type])
        
        # Actualizar última vez visto
        self.detected_devices[device_type]['last_seen'] = time.time()
        
        # Procesar según tipo de mensaje
        if msg_type == 'data':
            self.process_data_message(device_type, message)
        elif msg_type == 'response':
            self.command_response.emit(device_type, message['payload'])
        elif msg_type == 'status':
            self.device_status.emit(device_type, message['payload'])
        elif msg_type == 'error':
            error_msg = message.get('payload', {}).get('message', 'Error desconocido')
            self.error_occurred.emit(device_type, error_msg)
    
    def process_data_message(self, device_type, message):
        """
        Procesar mensaje de datos específico por tipo de dispositivo.
        
        Args:
            device_type (str): Tipo de dispositivo
            message (dict): Mensaje completo
        """
        payload = message.get('payload', {})
        
        # Añadir timestamp al payload para compatibilidad
        data_dict = payload.copy()
        data_dict['t'] = message['timestamp']
        
        # Validar datos específicos según dispositivo
        if device_type == 'SPIRO':
            required_fields = ['pressure', 'flow', 'volume']
            if all(field in payload for field in required_fields):
                # Mapear a formato legacy para compatibilidad
                data_dict.update({
                    'p': payload['pressure'],
                    'f': payload['flow'], 
                    'v': payload['volume']
                })
                self.new_data.emit(device_type, data_dict)
            else:
                self.error_occurred.emit(device_type, f"Datos de espirometría incompletos: {payload}")
                
        elif device_type == 'ECG':
            # Procesar datos de ECG
            if 'lead1' in payload:  # Al menos una derivación
                data_dict['ecg'] = payload['lead1']  # Derivación principal
                # Añadir otras derivaciones si están disponibles
                for i in range(1, 13):  # Hasta 12 derivaciones
                    lead_key = f'lead{i}'
                    if lead_key in payload:
                        data_dict[lead_key] = payload[lead_key]
                self.new_data.emit(device_type, data_dict)
            else:
                self.error_occurred.emit(device_type, f"Datos de ECG incompletos: {payload}")
                
        elif device_type == 'EMG':
            # Procesar datos de EMG
            if 'channel1' in payload:
                data_dict['emg'] = payload['channel1']  # Canal principal
                # Añadir canales adicionales
                for i in range(1, 9):  # Hasta 8 canales
                    ch_key = f'channel{i}'
                    if ch_key in payload:
                        data_dict[ch_key] = payload[ch_key]
                # RMS si está disponible
                if 'rms' in payload:
                    data_dict['rms'] = payload['rms']
                self.new_data.emit(device_type, data_dict)
            else:
                self.error_occurred.emit(device_type, f"Datos de EMG incompletos: {payload}")
                
        elif device_type == 'EEG':
            # Procesar datos de EEG (similar a EMG pero más canales)
            channels_found = False
            for i in range(1, 65):  # Hasta 64 canales EEG
                ch_key = f'channel{i}'
                if ch_key in payload:
                    data_dict[ch_key] = payload[ch_key]
                    channels_found = True
            
            if channels_found:
                # Canal principal si existe
                if 'channel1' in payload:
                    data_dict['eeg'] = payload['channel1']
                self.new_data.emit(device_type, data_dict)
            else:
                self.error_occurred.emit(device_type, f"Datos de EEG incompletos: {payload}")
    
    def try_parse_csv_legacy(self, data_string):
        """
        Intentar parsear formato CSV legacy para compatibilidad.
        
        Args:
            data_string (str): String a parsear
            
        Returns:
            bool: True si se parseó exitosamente
        """
        try:
            # Verificar si es formato CSV con exactamente 4 valores
            values = data_string.split(',')
            
            if len(values) == 4:
                # Convertir valores a float
                t, p, f, v = map(float, values)
                
                # Validar el tiempo (formato legacy)
                if not self.validate_time_legacy(t):
                    error_msg = f"Valor de tiempo inválido ({t}): debe tener al menos 4 dígitos"
                    self.error_occurred.emit("SPIRO", error_msg)
                    return True
                
                # Crear mensaje compatible con formato JSON
                data_dict = {
                    't': t,
                    'p': p,
                    'f': f,
                    'v': v
                }
                
                # Emitir como dispositivo SPIRO (asunción para legacy)
                self.new_data.emit("SPIRO", data_dict)
                return True
                
            return False
            
        except (ValueError, TypeError):
            return False
    
    def validate_time_legacy(self, time_value):
        """
        Validar el valor del tiempo en formato legacy.
        
        Args:
            time_value (float): Valor de tiempo a validar
            
        Returns:
            bool: True si el tiempo es válido
        """
        # Convertir a string para contar dígitos
        time_str = str(abs(time_value))
        
        # Remover el punto decimal para contar dígitos
        digits = time_str.replace('.', '')
        
        # Verificar que tenga al menos 4 dígitos
        return len(digits) >= 4
    
    def analizar_otro_string(self, string):
        """Procesar strings que no coinciden con ningún formato esperado"""
        print(f"String no estándar recibido: {string}")
        self.other_string.emit(string)
    
    def get_detected_devices(self):
        """
        Obtener lista de dispositivos detectados.
        
        Returns:
            dict: Diccionario de dispositivos detectados
        """
        return self.detected_devices.copy()
    
    def is_device_connected(self, device_type):
        """
        Verificar si un dispositivo específico está conectado.
        
        Args:
            device_type (str): Tipo de dispositivo
            
        Returns:
            bool: True si está conectado
        """
        if device_type not in self.detected_devices:
            return False
            
        # Considerar desconectado si no hay actividad por más de 5 segundos
        last_seen = self.detected_devices[device_type]['last_seen']
        return (time.time() - last_seen) < 5.0