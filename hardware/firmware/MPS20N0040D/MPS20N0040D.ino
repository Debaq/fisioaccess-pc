/*
  Sistema de medición con Venturi 28mm/15mm
  Sensor: MPS20N0040D con HX710B (ADC 24-bit)
  Pines: DOUT=5, SCK=6
*/

#include <math.h>

// ========== PINES ==========
#define DOUT_PIN 5
#define SCK_PIN  6

// ========== CALIBRACIÓN (del PDF Maker Portal) ==========
const float OFFSET_MV = 22.6;           // Offset típico del sensor
const float SENSITIVITY = 29.5 / 50.0;  // 0.59 kPa/mV (calibrado)
const float SUPPLY_VOLTAGE = 5.0;
const float HX710B_GAIN = 128.0;
const long  ADC_MAX = 8388607;          // 2^23 - 1

// ========== VENTURI ==========
const float FLOW_CONSTANT = 6.77;
const float PRESSURE_THRESHOLD = 0.002;
const float FLOW_THRESHOLD = 0.1;

// ========== VARIABLES ==========
float calibrationOffset = 0.0;  // En counts ADC
float volume = 0.0;
unsigned long lastMeasurementTime = 0;
unsigned long resetMeasurementTime = 0;
const int NUM_CALIBRATION_SAMPLES = 200;

struct FlowData {
    float flowRate;
    int direction;
};

// ========== LEER HX710B (SIN TIMEOUT) ==========
long readHX710B() {
    long data = 0;
    
    // Esperar dato listo (sin timeout)
    while (digitalRead(DOUT_PIN) == HIGH) {
        yield();
    }
    
    // Leer 24 bits
    for (uint8_t i = 0; i < 24; i++) {
        digitalWrite(SCK_PIN, HIGH);
        delayMicroseconds(1);
        data = (data << 1) | digitalRead(DOUT_PIN);
        digitalWrite(SCK_PIN, LOW);
        delayMicroseconds(1);
    }
    
    // Pulso 25 = ganancia 128
    digitalWrite(SCK_PIN, HIGH);
    delayMicroseconds(1);
    digitalWrite(SCK_PIN, LOW);
    
    // Sign extend 24→32 bits
    if (data & 0x00800000) data |= 0xFF000000;
    
    return data;
}

// ========== INICIALIZAR HX710B ==========
bool initHX710B() {
    Serial.println(F("Inicializando HX710B..."));
    
    // Reset: SCK alto >60µs
    digitalWrite(SCK_PIN, HIGH);
    delayMicroseconds(100);
    digitalWrite(SCK_PIN, LOW);
    delay(100);
    
    // Verificar respuesta (max 500ms)
    int attempts = 0;
    while (digitalRead(DOUT_PIN) == HIGH && attempts < 50) {
        delay(10);
        attempts++;
    }
    
    if (attempts >= 50) {
        return false;
    }
    
    // Lectura dummy para sincronizar
    readHX710B();
    delay(10);
    
    Serial.println(F("HX710B inicializado correctamente"));
    return true;
}

// ========== CONVERTIR ADC → mV ==========
float adcToMillivolts(long adcValue) {
    float calibrated = adcValue - calibrationOffset;
    float voltage_mv = (calibrated / ADC_MAX) * (SUPPLY_VOLTAGE * 1000.0 / HX710B_GAIN);
    return voltage_mv;
}

// ========== CONVERTIR mV → kPa ==========
float millivoltsToKPa(float voltage_mv) {
    return SENSITIVITY * (voltage_mv - OFFSET_MV);
}

// ========== OBTENER PRESIÓN ==========
float getPressureKPA() {
    const int numReadings = 5;
    float sumPressure = 0.0;
    int validReadings = 0;
    
    for(int i = 0; i < numReadings; i++) {
        long adc = readHX710B();
        
        // Verificar no saturado
        if (abs(adc) < ADC_MAX * 0.95) {
            float mv = adcToMillivolts(adc);
            float pressure = millivoltsToKPa(mv);
            sumPressure += pressure;
            validReadings++;
        }
        delay(2);
    }
    
    if (validReadings == 0) {
        return 0.0;
    }
    
    return sumPressure / validReadings;
}

// ========== CALIBRAR ==========
void calibrateSensor() {
    const int TOTAL = NUM_CALIBRATION_SAMPLES * 2;
    float sumValues = 0;
    float sumSquares = 0;
    
    Serial.println(F("========================================"));
    Serial.println(F("CALIBRACIÓN"));
    Serial.println(F("IMPORTANTE: Sin flujo de aire"));
    Serial.println(F("========================================"));
    delay(2000);
    
    for (int i = 0; i < TOTAL; i++) {
        long adc = readHX710B();
        
        if (i < NUM_CALIBRATION_SAMPLES) {
            sumValues += adc;
        } else {
            static float mean = sumValues / NUM_CALIBRATION_SAMPLES;
            sumSquares += sq(adc - mean);
        }
        
        if (i % (TOTAL / 20) == 0) {
            Serial.print(F("Progreso: "));
            Serial.print((i * 100L) / TOTAL);
            Serial.println('%');
        }
        delay(10);
    }
    
    float meanValue = sumValues / NUM_CALIBRATION_SAMPLES;
    float stdDev = sqrt(sumSquares / NUM_CALIBRATION_SAMPLES);
    
    calibrationOffset = meanValue;
    
    Serial.println(F("========================================"));
    Serial.print(F("Offset (counts): "));
    Serial.println(calibrationOffset, 1);
    Serial.print(F("Desv. estándar: "));
    Serial.println(stdDev, 1);
    
    if (stdDev > 1000) {
        Serial.println(F("ADVERTENCIA: Alta desviación - verificar aire"));
    }
    
    Serial.println(F("Sistema listo"));
    Serial.println(F("========================================"));
}

// ========== CALCULAR FLUJO ==========
FlowData calculateBidirectionalFlow(float pressureKPA) {
    FlowData result;
    
    if (abs(pressureKPA) < PRESSURE_THRESHOLD) {
        result.flowRate = 0;
        result.direction = 0;
        return result;
    }
    
    result.direction = (pressureKPA >= 0) ? 1 : -1;
    result.flowRate = result.direction * FLOW_CONSTANT * sqrt(abs(pressureKPA));
    
    if (abs(result.flowRate) < FLOW_THRESHOLD) {
        result.flowRate = 0;
        result.direction = 0;
    }
    
    return result;
}

// ========== RESETS ==========
void resetVolume() {
    volume = 0;
    lastMeasurementTime = millis();
    resetMeasurementTime = lastMeasurementTime;
    Serial.println(F("Volumen reseteado"));
}

void fullReset() {
    volume = 0;
    calibrateSensor();
    lastMeasurementTime = millis();
    resetMeasurementTime = lastMeasurementTime;
}

// ========== SETUP ==========
void setup() {
    delay(50);
    Serial.begin(115200);
    
    pinMode(SCK_PIN, OUTPUT);
    pinMode(DOUT_PIN, INPUT);
    digitalWrite(SCK_PIN, LOW);
    
    Serial.println();
    Serial.println(F("========================================"));
    Serial.println(F("ESPIRÓMETRO VENTURI"));
    Serial.println(F("Sensor: MPS20N0040D + HX710B"));
    Serial.println(F("Venturi: 28mm/15mm (K=6.77)"));
    Serial.println(F("========================================"));
    Serial.println(F("Comandos:"));
    Serial.println(F("  'r' - Reset completo + calibración"));
    Serial.println(F("  'v' - Reset solo volumen"));
    Serial.println(F("========================================"));
    Serial.println();
    
    // Inicializar HX710B
    if (!initHX710B()) {
        Serial.println(F("ERROR: HX710B no detectado"));
        Serial.println(F("Conexiones:"));
        Serial.println(F("  DOUT -> GPIO 5"));
        Serial.println(F("  SCK  -> GPIO 6"));
        Serial.println(F("  VCC  -> 3.3V o 5V"));
        Serial.println(F("  GND  -> GND"));
        while(1) delay(1000);
    }
    
    Serial.println();
    fullReset();
    
    Serial.println();
    Serial.println(F("Formato: Tiempo(ms),Presión(kPa),Flujo(L/s),Volumen(L)"));
    Serial.println(F("========================================"));
}

// ========== LOOP ==========
void loop() {
    // Comandos
    if (Serial.available() > 0) {
        char cmd = Serial.read();
        if (cmd == 'r' || cmd == 'R') {
            Serial.println(F("\n>>> RESET COMPLETO"));
            fullReset();
            return;
        }
        if (cmd == 'v' || cmd == 'V') {
            Serial.println(F("\n>>> RESET VOLUMEN"));
            resetVolume();
            return;
        }
    }
    
    unsigned long currentTime = millis();
    float deltaTimeSeconds = (currentTime - lastMeasurementTime) / 1000.0;
    
    // Medir
    float pressure_kpa = getPressureKPA();
    FlowData flujo = calculateBidirectionalFlow(pressure_kpa);
    
    // Integrar volumen
    if (abs(flujo.flowRate) >= FLOW_THRESHOLD && 
        deltaTimeSeconds > 0 && 
        deltaTimeSeconds < 1.0) {
        volume += flujo.flowRate * deltaTimeSeconds;
    }
    
    lastMeasurementTime = currentTime;
    unsigned long relativeTime = currentTime - resetMeasurementTime;
    
    // Output CSV
    Serial.print(relativeTime);
    Serial.print(",");
    Serial.print(pressure_kpa, 4);
    Serial.print(",");
    Serial.print(flujo.flowRate, 4);
    Serial.print(",");
    Serial.println(volume, 4);
    
}
