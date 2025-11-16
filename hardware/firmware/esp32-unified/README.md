# Firmware ESP32 Unificado - FisioAccess

Firmware modular para ESP32 que implementa el protocolo binario de comunicación unificado para múltiples dispositivos de fisioterapia.

## Características

- **Protocolo binario optimizado** con CRC16 para integridad de datos
- **Arquitectura modular** basada en clases para fácil extensión
- **Múltiples sensores soportados** con activación por configuración
- **Comunicación flexible**: Serial, WiFi o Bluetooth
- **Un solo firmware** para todos los dispositivos
- **Datos RAW**: Todos los sensores envían valores sin procesar - el procesamiento se realiza en Python

## Dispositivos Soportados

### 1. Espirómetro/Rinomanómetro (MPS20N0040D Dual)

- **Sensores**: 2x MPS20N0040D con HX710B (ADC 24-bit)
- **Datos enviados**: Valores RAW del ADC (24-bit con signo)
- **Aplicaciones**: Espirometría, rinomanometría
- **Protocolo IDs**:
  - `0x33` - Sensor 1 RAW ADC (Python convierte a kPa, calcula flujo y volumen)
  - `0x34` - Sensor 2 RAW ADC (Python convierte a kPa, calcula flujo y volumen)
- **Procesamiento en Python**:
  - Calibración (restar offset)
  - Conversión a kPa
  - Cálculo de flujo (L/s)
  - Integración de volumen (L)

### 2. Electrocardiograma (ECG)

#### ECG con ADS1115
- **ADC**: ADS1115 16-bit I2C
- **Canal**: A0 del ADS1115
- **Datos enviados**: Valores RAW del ADC (16-bit con signo, -32768 a +32767)
- **Lead Detection**: Pines D2 (LD+) y D3 (LD-)
- **Frecuencia**: 860 SPS
- **Protocolo IDs**:
  - `0x10` - ECG Canal 1 RAW ADC (Python convierte a voltaje)
  - `0x16` - Estado LD+ (0/1)
  - `0x17` - Estado LD- (0/1)
- **Procesamiento en Python**: Conversión a voltaje según ganancia del ADS1115

#### ECG Analógico Directo
- **ADC**: ADC interno ESP32 (12-bit)
- **Pin**: GPIO36 (A0)
- **Datos enviados**: Valores RAW del ADC (12-bit, 0-4095)
- **Lead Detection**: Pines D2 (LD+) y D3 (LD-)
- **Frecuencia**: Configurable (default 500 Hz)
- **Protocolo IDs**: Mismos que ECG con ADS1115
- **Procesamiento en Python**: Conversión a voltaje (0-3.3V)

### 3. Electromiografía (EMG)

#### EMG con ADS1115
- **ADC**: ADS1115 16-bit I2C
- **Canal**: A0 del ADS1115
- **Datos enviados**: Valores RAW del ADC (16-bit con signo, -32768 a +32767)
- **Frecuencia**: 860 SPS
- **Protocolo IDs**:
  - `0x18` - EMG Canal 1 RAW ADC (Python convierte a voltaje)
- **Procesamiento en Python**: Conversión a voltaje según ganancia del ADS1115

#### EMG Analógico Directo
- **ADC**: ADC interno ESP32 (12-bit)
- **Pin**: GPIO39 (A3)
- **Datos enviados**: Valores RAW del ADC (12-bit, 0-4095)
- **Frecuencia**: Configurable (default 500 Hz)
- **Protocolo IDs**: Mismo que EMG con ADS1115
- **Procesamiento en Python**: Conversión a voltaje (0-3.3V)

## Estructura del Proyecto

```
esp32-unified/
├── src/
│   ├── main.cpp                 # Loop principal
│   ├── config.h                 # Configuración del dispositivo
│   ├── protocol.h               # Definiciones del protocolo
│   ├── protocol.cpp             # Implementación del protocolo
│   ├── communication/
│   │   ├── serial_comm.h
│   │   └── serial_comm.cpp
│   └── sensors/
│       ├── sensor_base.h        # Clase base abstracta
│       ├── mps20n0040d_dual.h   # Espirómetro/Rinomanómetro
│       ├── mps20n0040d_dual.cpp
│       ├── ecg_ads1115.h        # ECG con ADS1115
│       ├── ecg_ads1115.cpp
│       ├── ecg_analog.h         # ECG analógico
│       ├── ecg_analog.cpp
│       ├── emg_ads1115.h        # EMG con ADS1115
│       ├── emg_ads1115.cpp
│       ├── emg_analog.h         # EMG analógico
│       └── emg_analog.cpp
├── examples/
│   ├── config_espirometro.h     # Config para espirómetro
│   ├── config_ecg_ads1115.h     # Config para ECG con ADS1115
│   ├── config_ecg_analog.h      # Config para ECG analógico
│   ├── config_emg_ads1115.h     # Config para EMG con ADS1115
│   └── config_emg_analog.h      # Config para EMG analógico
├── platformio.ini
└── README.md
```

## Configuración Rápida

### 1. Seleccionar Configuración

Copiar el archivo de configuración de ejemplo correspondiente:

```bash
# Para espirómetro/rinomanómetro
cp examples/config_espirometro.h src/config.h

# Para ECG con ADS1115
cp examples/config_ecg_ads1115.h src/config.h

# Para ECG analógico
cp examples/config_ecg_analog.h src/config.h

# Para EMG con ADS1115
cp examples/config_emg_ads1115.h src/config.h

# Para EMG analógico
cp examples/config_emg_analog.h src/config.h
```

### 2. Personalizar Configuración

Editar `src/config.h` para ajustar:
- `ESP32_ID`: ID único del dispositivo (0x0001-0xFFFF)
- Pines según tu hardware
- Modo de comunicación (Serial/WiFi/Bluetooth)

### 3. Compilar y Cargar

```bash
pio run -t upload
```

### 4. Verificar

```bash
pio device monitor
```

## Protocolo de Comunicación

Ver [README principal del firmware](../README.md) para detalles completos del protocolo binario.

### Estructura del Mensaje

```
[SYNC_1][SYNC_2][ID_ESP32][TIMESTAMP][N_DATOS][DATOS...][CRC16]
  0xFF    0xAA      2B        4B         1B      variable   2B
```

### Datos de Sensor

Cada dato incluye:
- **ID** (1 byte): Identificador del sensor/medición
- **Valor** (4 bytes): Float en little-endian (valor RAW del ADC)

### Principio de Datos RAW

**IMPORTANTE**: El firmware **SOLO** envía valores RAW de los ADC, sin ningún procesamiento:

- **MPS20N0040D (HX710B)**: Envía valor directo del ADC de 24-bit (-8388608 a +8388607)
- **ADS1115**: Envía valor directo del ADC de 16-bit (-32768 a +32767)
- **ESP32 ADC**: Envía valor directo del ADC de 12-bit (0 a 4095)

**Todo el procesamiento se realiza en Python**:
- Calibración (offset)
- Conversión a unidades físicas (voltios, kPa, etc.)
- Filtrado de señales
- Cálculos derivados (flujo, volumen, frecuencia cardíaca, etc.)

**Ventajas de este enfoque**:
- Mayor flexibilidad para ajustar algoritmos sin recompilar firmware
- Acceso a datos crudos para análisis y depuración
- Firmware más simple y confiable
- Procesamiento complejo en Python (numpy, scipy, pandas)

## Configuraciones de Hardware

### Espirómetro/Rinomanómetro

```
Sensor 1 (HX710B):
  DOUT -> GPIO 5
  SCK  -> GPIO 6

Sensor 2 (HX710B):
  DOUT -> GPIO 7
  SCK  -> GPIO 4
```

### ECG con ADS1115

```
ADS1115 (I2C):
  SDA  -> GPIO 21
  SCL  -> GPIO 22
  ADDR -> 0x48

Lead Detection:
  LD+  -> GPIO 2 (D2)
  LD-  -> GPIO 3 (D3)

Señal ECG -> ADS1115 A0
```

### ECG Analógico Directo

```
Señal ECG -> GPIO 36 (A0)

Lead Detection:
  LD+  -> GPIO 2 (D2)
  LD-  -> GPIO 3 (D3)
```

### EMG con ADS1115

```
ADS1115 (I2C):
  SDA  -> GPIO 21
  SCL  -> GPIO 22
  ADDR -> 0x48

Señal EMG -> ADS1115 A0
```

### EMG Analógico Directo

```
Señal EMG -> GPIO 39 (A3)
```

## Calibración

**El firmware NO realiza calibración**. Todos los sensores envían datos RAW sin procesar.

La calibración se realiza completamente en Python:
- **MPS20N0040D**: Python calcula el offset promediando muestras en reposo y lo resta de las lecturas
- **ECG/EMG**: Python aplica filtros, normalización y corrección de baseline según sea necesario

Ventajas:
- Recalibrar sin reiniciar el ESP32
- Guardar múltiples perfiles de calibración
- Ajustar parámetros en tiempo real

## Ejemplos de Uso

### Dispositivo 1: Espirómetro con dos sensores

```cpp
#define ESP32_ID 0x0001
#define COMM_MODE_SERIAL
#define USE_MPS20N0040D_DUAL
```

### Dispositivo 2: ECG con ADS1115

```cpp
#define ESP32_ID 0x0002
#define COMM_MODE_SERIAL
#define USE_ECG_ADS1115
```

### Dispositivo 3: EMG analógico

```cpp
#define ESP32_ID 0x0003
#define COMM_MODE_SERIAL
#define USE_EMG_ANALOG
```

## Dependencias

Definidas en `platformio.ini`:
- Adafruit ADS1X15 (para ADS1115)
- Adafruit Unified Sensor
- Wire (I2C)

## Frecuencias de Muestreo

| Dispositivo | Frecuencia | Notas |
|-------------|-----------|-------|
| MPS20N0040D | ~100 Hz | Limitado por HX710B |
| ECG ADS1115 | 860 SPS | Máximo del ADS1115 |
| ECG Analógico | 500 Hz | Configurable |
| EMG ADS1115 | 860 SPS | Máximo del ADS1115 |
| EMG Analógico | 500 Hz | Configurable |

## Solución de Problemas

### Error: Sensor no responde

- Verificar conexiones físicas
- Comprobar pines en `config.h`
- Revisar voltaje de alimentación (3.3V)

### Datos corruptos

- Verificar CRC16 en receptor
- Revisar baudrate (115200)
- Comprobar cable USB

### Latencia alta

- Reducir delay en `loop()`
- Para ECG/EMG: comentar delay completamente
- Verificar que no hay bloqueos en código

## Expansión

Para agregar un nuevo sensor:

1. Crear `sensors/nuevo_sensor.h` y `.cpp`
2. Heredar de `SensorBase`
3. Implementar `init()` y `read()`
4. Usar `addData(ID_SENSOR, valor)` en `read()`
5. Agregar `#define USE_NUEVO_SENSOR` en `config.h`
6. Incluir en `main.cpp`

## Licencia

Ver LICENSE en la raíz del proyecto.

## Contacto

FisioAccess - Sistema de adquisición de datos para fisioterapia
