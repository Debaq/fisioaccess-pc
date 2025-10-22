/*
 *  Sistema de medición con Venturi 28mm/15mm + LED RGB de feedback visual
 *  Sensor: MPS20N0040D con HX710B (ADC 24-bit)
 *  Pines Sensor: DOUT=5, SCK=6
 *  Pines LED RGB (común VCC): R=9, G=3, B=10
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

// ========== PINES SENSOR ==========
#define DOUT_PIN 5
#define SCK_PIN  6

// ========== PINES LED RGB (común VCC) ==========
#define LED_R 9
#define LED_G 3
#define LED_B 10

// ========== CALIBRACIÓN EMPÍRICA ==========
const float COUNTS_TO_KPA = 0.000028;

// ========== VENTURI ==========
const float FLOW_CONSTANT = 6.77;
const float PRESSURE_THRESHOLD = 0.010;
const float FLOW_THRESHOLD = 0.1;
const float DIVISION_FACTOR = 14.388;

// ========== VARIABLES DE MEDICIÓN ==========
long calibrationOffset = 0;
float volume = 0.0;
unsigned long lastMeasurementTime = 0;
unsigned long resetMeasurementTime = 0;
const int NUM_CALIBRATION_SAMPLES = 50;

// ========== VARIABLES LED ==========
enum LEDState {
  LED_UNCALIBRATED,  // Verde suave - esperando calibración
  LED_CALIBRATING,   // Rojo pulsante - calibrando
  LED_READY,         // Azul constante - listo para prueba
  LED_RESETTING,     // Magenta pulsante - reset volumen
  LED_ERROR          // Rojo intermitente - error
};

LEDState currentLEDState = LED_UNCALIBRATED;
LEDState targetLEDState = LED_UNCALIBRATED;

// Colores RGB actuales y objetivo (0-255, invertido porque es común VCC)
struct Color {
  int r, g, b;
};

Color currentColor = {255, 255, 255}; // Apagado (común VCC)
Color targetColor = {255, 255, 255};

// Variables para animaciones
unsigned long lastLEDUpdate = 0;
const int LED_UPDATE_INTERVAL = 20; // ms entre actualizaciones
float ledPhase = 0.0; // Fase para pulsos (0-1)
float ledBrightness = 0.0; // Brillo general (0-1)
bool fadingToTarget = false;
float fadeProgress = 0.0;
const float FADE_SPEED = 0.05; // Velocidad de transición

// Variables para detección de estado de flujo
bool isMeasuring = false;
float lastVolume = 0.0;
unsigned long lastVolumeIncrease = 0;
const unsigned long VOLUME_TIMEOUT = 1000; // ms sin aumento = fin de medición

struct FlowData {
    float flowRate;
    int direction;
};

// ========== FUNCIONES LED ==========

void setupLED() {
  pinMode(LED_R, OUTPUT);
  pinMode(LED_G, OUTPUT);
  pinMode(LED_B, OUTPUT);
  setLEDColor(255, 255, 255); // Apagado inicialmente
}

// Establecer color LED (0-255, invertido para común VCC)
void setLEDColor(int r, int g, int b) {
  analogWrite(LED_R, 255 - r);
  analogWrite(LED_G, 255 - g);
  analogWrite(LED_B, 255 - b);
}

// Interpolación lineal entre dos valores
float lerpColor(float a, float b, float t) {
  return a + (b - a) * t;
}

// Obtener color objetivo según estado
Color getTargetColor(LEDState state) {
  Color c;
  switch(state) {
    case LED_UNCALIBRATED:
      // Verde suave - sin calibrar
      c.r = 0; c.g = 255; c.b = 0;
      break;
    case LED_CALIBRATING:
      // Rojo - calibrando
      c.r = 255; c.g = 0; c.b = 0;
      break;
    case LED_READY:
      // Azul - listo
      c.r = 0; c.g = 0; c.b = 255;
      break;
    case LED_RESETTING:
      // Magenta - reset volumen
      c.r = 255; c.g = 0; c.b = 255;
      break;
    case LED_ERROR:
      // Rojo - error
      c.r = 255; c.g = 0; c.b = 0;
      break;
    default:
      // Apagado
      c.r = 0; c.g = 0; c.b = 0;
      break;
  }
  return c;
}

// Actualizar LED según estado actual
void updateLED() {
  unsigned long now = millis();
  
  if (now - lastLEDUpdate < LED_UPDATE_INTERVAL) {
    return;
  }
  
  lastLEDUpdate = now;
  
  // Si hay cambio de estado, iniciar fade
  if (currentLEDState != targetLEDState) {
    currentLEDState = targetLEDState;
    targetColor = getTargetColor(currentLEDState);
    fadingToTarget = true;
    fadeProgress = 0.0;
  }
  
  // Fade suave entre colores
  if (fadingToTarget) {
    fadeProgress += FADE_SPEED;
    if (fadeProgress >= 1.0) {
      fadeProgress = 1.0;
      fadingToTarget = false;
      currentColor = targetColor;
    }
    
    currentColor.r = lerpColor(currentColor.r, targetColor.r, fadeProgress);
    currentColor.g = lerpColor(currentColor.g, targetColor.g, fadeProgress);
    currentColor.b = lerpColor(currentColor.b, targetColor.b, fadeProgress);
  }
  
  // Aplicar efectos según estado
  Color displayColor = currentColor;
  
  switch(currentLEDState) {
    case LED_UNCALIBRATED: {
      // Verde constante suave
      ledBrightness = 0.4;
      displayColor.r *= ledBrightness;
      displayColor.g *= ledBrightness;
      displayColor.b *= ledBrightness;
      break;
    }
    
    case LED_CALIBRATING: {
      // Rojo pulsante suave lento (respiración)
      ledPhase += 0.02;
      if (ledPhase > 1.0) ledPhase = 0.0;
      ledBrightness = 0.3 + 0.4 * sin(ledPhase * 2.0 * PI);
      displayColor.r *= ledBrightness;
      displayColor.g *= ledBrightness;
      displayColor.b *= ledBrightness;
      break;
    }
      
    case LED_READY: {
      // Azul constante - listo para prueba
      ledBrightness = 0.6;
      displayColor.r *= ledBrightness;
      displayColor.g *= ledBrightness;
      displayColor.b *= ledBrightness;
      break;
    }
    
    case LED_RESETTING: {
      // Magenta pulsante rápido (manejado con showResetEffect)
      ledPhase += 0.2;
      if (ledPhase > 1.0) ledPhase = 0.0;
      ledBrightness = 0.5 + 0.5 * sin(ledPhase * 2.0 * PI);
      displayColor.r *= ledBrightness;
      displayColor.g *= ledBrightness;
      displayColor.b *= ledBrightness;
      break;
    }
      
    case LED_ERROR: {
      // Rojo intermitente rápido
      ledPhase += 0.3;
      if (ledPhase > 1.0) ledPhase = 0.0;
      ledBrightness = (ledPhase < 0.5) ? 1.0 : 0.0;
      displayColor.r *= ledBrightness;
      displayColor.g *= ledBrightness;
      displayColor.b *= ledBrightness;
      break;
    }
      
    default: {
      // Apagado
      displayColor.r = 0;
      displayColor.g = 0;
      displayColor.b = 0;
      break;
    }
  }
  
  setLEDColor(displayColor.r, displayColor.g, displayColor.b);
}

// Efecto de reset volumen (2-3 pulsos magenta)
void showResetEffect() {
  for(int i = 0; i < 2; i++) {
    setLEDColor(255, 0, 255); // Magenta brillante
    delay(150);
    setLEDColor(0, 0, 0); // Apagado
    delay(150);
  }
  targetLEDState = LED_READY;
}

// ========== RESETS ==========
void resetVolume() {
    volume = 0;
    lastMeasurementTime = millis();
    resetMeasurementTime = lastMeasurementTime;
    showResetEffect(); // Magenta 2 pulsos
}

void fullReset() {
    volume = 0;
    calibrateSensor(); // Cambiará a LED_READY al terminar
    lastMeasurementTime = millis();
    resetMeasurementTime = lastMeasurementTime;
}

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

    targetLEDState = LED_CALIBRATING;
    
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
        
        updateLED(); // Mantener animación durante calibración
        delay(10);
    }

    calibrationOffset = sumValues / NUM_CALIBRATION_SAMPLES;
    float stdDev = sqrt((float)sumSquares / NUM_CALIBRATION_SAMPLES);

    Serial.print(F("Calibración completada. Offset: "));
    Serial.println(calibrationOffset);
    Serial.print(F("Desviación estándar: "));
    Serial.println(stdDev, 6);
    Serial.println(F("Iniciando mediciones..."));
    
    targetLEDState = LED_READY;
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

// ========== SETUP ==========
void setup() {
    delay(50);
    Serial.begin(115200);

    pinMode(SCK_PIN, OUTPUT);
    pinMode(DOUT_PIN, INPUT);
    digitalWrite(SCK_PIN, LOW);

    setupLED();
    targetLEDState = LED_UNCALIBRATED; // Verde - esperando calibración

    if (!initHX710B()) {
        targetLEDState = LED_ERROR;
        while(1) {
          updateLED();
          delay(100);
        }
    }
}

// ========== LOOP ==========
void loop() {
    // Actualizar LED continuamente
    updateLED();
    
    // Comandos desde serial
    if (Serial.available() > 0) {
        String cmd = Serial.readStringUntil('\n');
        cmd.trim();
        
        if (cmd == "r" || cmd == "R") {
            fullReset();
            return;
        } else if (cmd == "v" || cmd == "V") {
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
