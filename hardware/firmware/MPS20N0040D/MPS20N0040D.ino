/*
 *  Sistema de medición con Venturi 28mm/15mm
 *  Sensor: MPS20N0040D con HX710B (ADC 24-bit)
 *  Pines: DOUT=5, SCK=6
 *
 *  CALIBRACIÓN EMPÍRICA:
 *  - Offset en reposo: ~720,376 counts
 *  - Max (soplar fuerte): ~660,291 counts (estimado ~2-3 kPa)
 *  - Min (succionar fuerte): ~-1,406,866 counts (estimado ~-3-5 kPa)
 *  - Rango sensor: 0-40 kPa
 *
 *  Factor calculado considerando que al soplar/succionar fuerte
 *  se alcanzan aproximadamente ±2-3 kPa:
 *  COUNTS_TO_KPA ≈ 3 kPa / 660000 counts ≈ 0.0000045
 */

#include <math.h>

// ========== PINES ==========
#define DOUT_PIN 5
#define SCK_PIN  6

// ========== CALIBRACIÓN EMPÍRICA ==========
// Factor ajustado basado en:
// - Datasheet MPS20N0040D: 50-100mV span para 40kPa
// - HX710B ganancia: 128x
// - Rango ADC: ~1.4M counts para rango completo
// Factor: 40 kPa / 1,400,000 counts ≈ 0.000028
const float COUNTS_TO_KPA = 0.000028;

// ========== VENTURI ==========
const float FLOW_CONSTANT = 6.77;       // K para Venturi 28mm/15mm
const float PRESSURE_THRESHOLD = 0.010; // 10 Pa (ajustado por ruido del sensor)
const float FLOW_THRESHOLD = 0.1;       // 0.1 L/s
const float DIVISION_FACTOR = 14.388;      // Factor de división para valores medidos

// ========== VARIABLES ==========
long calibrationOffset = 0;  // Offset en counts ADC
float volume = 0.0;
unsigned long lastMeasurementTime = 0;
unsigned long resetMeasurementTime = 0;
const int NUM_CALIBRATION_SAMPLES = 50;

struct FlowData {
    float flowRate;
    int direction;
};

// ========== LEER HX710B ==========
long readHX710B() {
    long data = 0;

    while (digitalRead(DOUT_PIN) == HIGH) yield();

    for (uint8_t i = 0; i < 24; i++) {
        digitalWrite(SCK_PIN, HIGH);
        delayMicroseconds(1);
        data = (data << 1) | digitalRead(DOUT_PIN);
        digitalWrite(SCK_PIN, LOW);
        delayMicroseconds(1);
    }

    digitalWrite(SCK_PIN, HIGH);
    delayMicroseconds(1);
    digitalWrite(SCK_PIN, LOW);

    if (data & 0x00800000) data |= 0xFF000000;

    return data;
}

// ========== INICIALIZAR HX710B ==========
bool initHX710B() {
    digitalWrite(SCK_PIN, HIGH);
    delayMicroseconds(100);
    digitalWrite(SCK_PIN, LOW);
    delay(100);

    int attempts = 0;
    while (digitalRead(DOUT_PIN) == HIGH && attempts < 50) {
        delay(10);
        attempts++;
    }

    if (attempts >= 50) return false;

    readHX710B(); // lectura dummy
    delay(10);

    return true;
}

// ========== OBTENER PRESIÓN ==========
float getPressureKPA() {
    const int numReadings = 1;
    float sumPressure = 0.0;

    for(int i = 0; i < numReadings; i++) {
        long adc = readHX710B();
        long calibrated = adc - calibrationOffset;
        float pressure = (calibrated * COUNTS_TO_KPA) / DIVISION_FACTOR;
        sumPressure += pressure;
    }

    return sumPressure / numReadings;
}

// ========== CALIBRAR ==========
void calibrateSensor() {
    const int TOTAL = NUM_CALIBRATION_SAMPLES * 2;
    long sumValues = 0;
    long sumSquares = 0;

    Serial.println(F("Iniciando calibración..."));
    Serial.println(F("Asegúrese que no hay flujo de aire"));
    delay(2000);

    for (int i = 0; i < TOTAL; i++) {
        long adc = readHX710B();

        if (i < NUM_CALIBRATION_SAMPLES) {
            sumValues += adc;
        } else {
            long mean = sumValues / NUM_CALIBRATION_SAMPLES;
            long diff = adc - mean;
            sumSquares += (diff * diff);
        }

        if (i % (TOTAL / 20) == 0) {
            Serial.print(F("Calibrando: "));
            Serial.print((i * 100L) / TOTAL);
            Serial.println('%');
        }
        delay(10);
    }

    calibrationOffset = sumValues / NUM_CALIBRATION_SAMPLES;
    float stdDev = sqrt((float)sumSquares / NUM_CALIBRATION_SAMPLES);

    Serial.print(F("Calibración completada. Offset: "));
    Serial.println(calibrationOffset);
    Serial.print(F("Desviación estándar: "));
    Serial.println(stdDev, 6);
    Serial.println(F("Iniciando mediciones..."));
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

    if (!initHX710B()) {
        while(1) delay(1000);
    }

}

// ========== LOOP ==========
void loop() {
    // Comandos
    if (Serial.available() > 0) {
        char cmd = Serial.read();
        if (cmd == 'r' || cmd == 'R') {
            fullReset();
            return;
        }
        if (cmd == 'v' || cmd == 'V') {
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
