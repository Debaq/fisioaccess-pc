"""
Módulo para decodificar el protocolo binario del ESP32 FisioAccess

Protocolo:
[SYNC_1][SYNC_2][ID_ESP32][TIMESTAMP][N_DATOS][DATOS...][CRC16]
  0xFF    0xAA      2B        4B         1B     variable   2B

Cada dato:
[ID][VALUE_FLOAT]
 1B      4B

Endianness: Little-endian
"""

import struct

# Constantes del protocolo
SYNC_BYTE_1 = 0xFF
SYNC_BYTE_2 = 0xAA

# IDs de sensores
ID_PRESION_1 = 0x33  # Sensor 1 RAW ADC (HX710B 24-bit) - Espirometría
ID_PRESION_2 = 0x34  # Sensor 2 RAW ADC (HX710B 24-bit) - Rinomanometría
ID_ECG_CH1 = 0x10    # ECG Canal 1 (RAW ADC)
ID_EMG_CH1 = 0x18    # EMG Canal 1 (RAW ADC)
ID_ECG_LD_PLUS = 0x16   # Estado del lead detection positivo (0/1)
ID_ECG_LD_MINUS = 0x17  # Estado del lead detection negativo (0/1)


class BinaryProtocolDecoder:
    """Decodificador del protocolo binario del ESP32"""

    def __init__(self):
        self.buffer = bytearray()

    def calculate_crc16(self, data):
        """
        Calcula CRC16 usando el algoritmo compatible con el ESP32

        Args:
            data (bytes): Datos para calcular CRC

        Returns:
            int: Valor CRC16
        """
        crc = 0xFFFF
        for byte in data:
            crc ^= byte
            for _ in range(8):
                if crc & 0x0001:
                    crc = (crc >> 1) ^ 0x8408
                else:
                    crc >>= 1
        return crc & 0xFFFF

    def add_data(self, data):
        """
        Agrega datos recibidos al buffer

        Args:
            data (bytes): Datos recibidos del puerto serial
        """
        self.buffer.extend(data)

    def find_sync_bytes(self):
        """
        Busca los bytes de sincronización en el buffer

        Returns:
            int: Índice donde comienzan los bytes de sincronización, -1 si no se encuentra
        """
        for i in range(len(self.buffer) - 1):
            if self.buffer[i] == SYNC_BYTE_1 and self.buffer[i + 1] == SYNC_BYTE_2:
                return i
        return -1

    def decode_message(self):
        """
        Intenta decodificar un mensaje completo del buffer

        Returns:
            dict: Diccionario con los datos decodificados o None si no hay mensaje completo
                {
                    'esp32_id': int,
                    'timestamp': int,
                    'sensors': {sensor_id: value, ...}
                }
        """
        # Buscar bytes de sincronización
        sync_idx = self.find_sync_bytes()

        if sync_idx == -1:
            # No se encontraron bytes de sincronización
            # Limpiar buffer si es muy grande para evitar acumulación
            if len(self.buffer) > 1024:
                self.buffer = self.buffer[-256:]
            return None

        # Eliminar datos antes de los bytes de sincronización
        if sync_idx > 0:
            self.buffer = self.buffer[sync_idx:]

        # Verificar que haya suficientes bytes para el header mínimo
        # SYNC(2) + ID_ESP32(2) + TIMESTAMP(4) + N_DATOS(1) = 9 bytes
        if len(self.buffer) < 9:
            return None

        # Decodificar header
        esp32_id = struct.unpack('<H', self.buffer[2:4])[0]  # Little-endian uint16
        timestamp = struct.unpack('<I', self.buffer[4:8])[0]  # Little-endian uint32
        n_datos = self.buffer[8]

        # Calcular tamaño total del mensaje
        # Header(9) + Datos(n_datos * 5) + CRC(2)
        message_size = 9 + (n_datos * 5) + 2

        # Verificar que tengamos el mensaje completo
        if len(self.buffer) < message_size:
            return None

        # Extraer mensaje completo
        message = self.buffer[:message_size]

        # Verificar CRC
        crc_received = struct.unpack('<H', message[-2:])[0]
        crc_calculated = self.calculate_crc16(message[2:-2])  # Desde ID_ESP32 hasta fin de datos

        if crc_received != crc_calculated:
            print(f"Error CRC: recibido={crc_received:04X}, calculado={crc_calculated:04X}")
            # Eliminar el mensaje corrupto y buscar el siguiente
            self.buffer = self.buffer[2:]  # Saltar los bytes de sync y buscar el siguiente
            return None

        # Decodificar datos de sensores
        sensors = {}
        idx = 9  # Comenzar después del header

        for _ in range(n_datos):
            sensor_id = message[idx]
            sensor_value = struct.unpack('<f', message[idx+1:idx+5])[0]  # Little-endian float
            sensors[sensor_id] = sensor_value
            idx += 5

        # Eliminar mensaje procesado del buffer
        self.buffer = self.buffer[message_size:]

        return {
            'esp32_id': esp32_id,
            'timestamp': timestamp,
            'sensors': sensors
        }

    def process_buffer(self):
        """
        Procesa todos los mensajes disponibles en el buffer

        Returns:
            list: Lista de mensajes decodificados
        """
        messages = []

        while True:
            message = self.decode_message()
            if message is None:
                break
            messages.append(message)

        return messages


class SensorDataProcessor:
    """Procesa datos RAW de sensores y los convierte a unidades físicas"""

    def __init__(self):
        # Calibración para sensores de presión (offset RAW)
        self.pressure_offset_1 = 0.0
        self.pressure_offset_2 = 0.0

        # Estado para cálculo de flujo y volumen
        self.last_timestamp = None
        self.accumulated_volume = 0.0

        # Constantes de conversión
        # HX710B: 24-bit signed (-8388608 a 8388607)
        # MPS20N0040D: Rango ±40 kPa
        # Asumiendo sensibilidad típica del HX710B con MPS20N0040D
        self.kpa_per_raw_unit = 80.0 / 16777216.0  # 80 kPa rango total / 2^24

    def set_pressure_calibration(self, offset_1, offset_2):
        """
        Establece los valores de calibración para los sensores de presión

        Args:
            offset_1 (float): Offset RAW del sensor 1
            offset_2 (float): Offset RAW del sensor 2
        """
        self.pressure_offset_1 = offset_1
        self.pressure_offset_2 = offset_2
        print(f"Calibración actualizada: Sensor1={offset_1:.0f}, Sensor2={offset_2:.0f}")

    def reset_volume(self):
        """Reinicia el cálculo de volumen acumulado"""
        self.accumulated_volume = 0.0
        self.last_timestamp = None

    def raw_to_pressure(self, raw_value, offset):
        """
        Convierte valor RAW del HX710B a presión en kPa

        Args:
            raw_value (float): Valor RAW del ADC
            offset (float): Offset de calibración

        Returns:
            float: Presión en kPa
        """
        calibrated = raw_value - offset
        pressure_kpa = calibrated * self.kpa_per_raw_unit
        return pressure_kpa

    def calculate_flow(self, pressure_kpa):
        """
        Calcula flujo a partir de presión diferencial
        Usa ecuación de Fleisch para neumotacógrafo

        Args:
            pressure_kpa (float): Presión diferencial en kPa

        Returns:
            float: Flujo en L/s
        """
        # Convertir kPa a Pa
        pressure_pa = pressure_kpa * 1000.0

        # Ecuación simplificada de flujo
        # Q = K * sqrt(|ΔP|) * sign(ΔP)
        # K es una constante de calibración del neumotacógrafo
        K = 0.5  # Ajustar según calibración del dispositivo

        if abs(pressure_pa) < 0.1:  # Umbral de ruido
            return 0.0

        flow_sign = 1.0 if pressure_pa >= 0 else -1.0
        flow = K * (abs(pressure_pa) ** 0.5) * flow_sign

        return flow

    def calculate_volume(self, flow, timestamp):
        """
        Calcula volumen acumulado por integración numérica del flujo

        Args:
            flow (float): Flujo en L/s
            timestamp (int): Timestamp en milisegundos

        Returns:
            float: Volumen acumulado en L
        """
        if self.last_timestamp is None:
            self.last_timestamp = timestamp
            return self.accumulated_volume

        # Calcular delta de tiempo en segundos
        dt = (timestamp - self.last_timestamp) / 1000.0

        # Limitar dt para evitar saltos grandes
        if dt > 0.5:  # Más de 500ms indica pérdida de datos
            dt = 0.0

        # Integración trapezoidal (más precisa que rectangular)
        # Necesitaríamos el flujo anterior, por ahora usamos rectangular
        delta_volume = flow * dt

        self.accumulated_volume += delta_volume
        self.last_timestamp = timestamp

        # Limitar volumen a rango razonable (0 a 10L)
        self.accumulated_volume = max(0.0, min(10.0, self.accumulated_volume))

        return self.accumulated_volume

    def process_message(self, message):
        """
        Procesa un mensaje decodificado y extrae t, p, f, v

        Args:
            message (dict): Mensaje decodificado del protocolo binario

        Returns:
            dict: Diccionario con keys 't', 'p', 'f', 'v' o None si no hay datos de presión
        """
        sensors = message['sensors']
        timestamp = message['timestamp']

        # Verificar que tengamos al menos un sensor de presión
        if ID_PRESION_1 not in sensors and ID_PRESION_2 not in sensors:
            return None

        # Obtener valor RAW de presión (usar sensor 1 por defecto, sensor 2 para rinomanometría)
        raw_pressure = sensors.get(ID_PRESION_1, sensors.get(ID_PRESION_2, 0.0))
        offset = self.pressure_offset_1 if ID_PRESION_1 in sensors else self.pressure_offset_2

        # Convertir a presión en kPa
        pressure_kpa = self.raw_to_pressure(raw_pressure, offset)

        # Calcular flujo
        flow_lps = self.calculate_flow(pressure_kpa)

        # Calcular volumen
        volume_l = self.calculate_volume(flow_lps, timestamp)

        return {
            't': timestamp,
            'p': pressure_kpa,
            'f': flow_lps,
            'v': volume_l
        }
