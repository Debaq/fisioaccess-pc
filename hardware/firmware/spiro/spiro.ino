#include <Wire.h>
#include <Adafruit_ADS1X15.h>
#include <math.h>
#include <ArduinoJson.h>

Adafruit_ADS1115 ads;

#define I2C_SDA 6
#define I2C_SCL 7
#define BUFFER_SIZE 500

// Estados del sistema
enum SystemState {
    STATE_BOOT,
    STATE_CALIBRATING,
    STATE_READY,
    STATE_MEASURING,
    STATE_ERROR
};

struct FlowData {
    float pressure;
    float flowRate;
    float volume;
    uint32_t timestamp;
};

// Variables globales
SystemState currentState = STATE_BOOT;

// Buffer circular simple
FlowData dataBuffer[BUFFER_SIZE];
int bufferHead = 0;
int bufferTail = 0;

// Configuración
const float PRESSURE_THRESHOLD = 0.002;
const float FLOW_THRESHOLD = 0.1;
const float FLOW_CONSTANT = 5.1591;
const int NUM_CALIBRATION_SAMPLES = 100;
int samplingRate = 200; // Hz

// Variables de medición
float calibrationOffset = 0;
float volume = 0;
unsigned long lastMeasurementTime = 0;
unsigned long lastDataSendTime = 0;

// Filtro promedio móvil exponencial
float alpha = 0.1;
float filteredPressure = 0;
bool filterInitialized = false;

// Timer para muestreo
hw_timer_t *samplingTimer = NULL;
volatile bool takeMeasurement = false;

// Interrupción del timer
void IRAM_ATTR onSamplingTimer() {
    takeMeasurement = true;
}

void setup() {
    Serial.begin(115200);
    delay(100);

    Wire.begin(I2C_SDA, I2C_SCL);

    if (!ads.begin()) {
        sendErrorMessage("ADS1115 initialization failed");
        currentState = STATE_ERROR;
        return;
    }

    ads.setGain(GAIN_ONE);

    // ✅ Nueva API del timer
    samplingTimer = timerBegin(1000000); // 1 MHz
    timerAttachInterrupt(samplingTimer, &onSamplingTimer);
    timerAlarm(samplingTimer, 1000000 / samplingRate, true, 0);
    timerStart(samplingTimer);

    if (performSelfTest()) {
        sendDeviceInfo();
        currentState = STATE_READY;
        Serial.println("System ready");
    } else {
        currentState = STATE_ERROR;
        Serial.println("Self-test failed");
    }
}

void loop() {
    processIncomingCommands();

    if (takeMeasurement && currentState == STATE_MEASURING) {
        takeMeasurement = false;
        performMeasurement();
    }

    if (millis() - lastDataSendTime >= 5) {
        sendBufferedData();
        lastDataSendTime = millis();
    }

    delay(1);
}

void performMeasurement() {
    FlowData newData;
    newData.timestamp = millis();

    float rawPressure = getPressureKPA(0);
    newData.pressure = rawPressure;

    if (!filterInitialized) {
        filteredPressure = newData.pressure;
        filterInitialized = true;
    } else {
        filteredPressure = alpha * newData.pressure + (1 - alpha) * filteredPressure;
    }

    newData.flowRate = calculateFlowRate(filteredPressure);

    float dt = (newData.timestamp - lastMeasurementTime) / 1000.0;
    if (abs(newData.flowRate) >= FLOW_THRESHOLD && dt > 0) {
        volume += newData.flowRate * dt;
    }
    newData.volume = volume;
    lastMeasurementTime = newData.timestamp;

    addToBuffer(newData);
}

void addToBuffer(const FlowData& data) {
    int nextHead = (bufferHead + 1) % BUFFER_SIZE;
    if (nextHead != bufferTail) {
        dataBuffer[bufferHead] = data;
        bufferHead = nextHead;
    }
}

bool getFromBuffer(FlowData& data) {
    if (bufferTail != bufferHead) {
        data = dataBuffer[bufferTail];
        bufferTail = (bufferTail + 1) % BUFFER_SIZE;
        return true;
    }
    return false;
}

void processIncomingCommands() {
    if (Serial.available()) {
        String input = Serial.readStringUntil('\n');
        input.trim();
        if (input.length() == 0) return;

        StaticJsonDocument<300> doc;
        DeserializationError error = deserializeJson(doc, input);
        if (error) {
            sendErrorMessage("Invalid JSON command");
            return;
        }

        String cmd = doc["cmd"];
        JsonObject params = doc["params"];

        if (cmd == "calibrate") {
            handleCalibrate();
        } else if (cmd == "reset") {
            handleReset(params);
        } else if (cmd == "start") {
            handleStart();
        } else if (cmd == "stop") {
            handleStop();
        } else if (cmd == "config") {
            handleConfig(params);
        } else if (cmd == "info") {
            sendDeviceInfo();
        } else {
            sendErrorMessage("Unknown command: " + cmd);
        }
    }
}

void handleCalibrate() {
    if (currentState != STATE_READY) {
        sendResponse("calibrate", "error", "Not in ready state");
        return;
    }

    currentState = STATE_CALIBRATING;
    sendResponse("calibrate", "success", "Calibration started");

    if (performCalibration()) {
        currentState = STATE_READY;
        sendResponse("calibrate", "success", "Calibration completed");
    } else {
        currentState = STATE_ERROR;
        sendResponse("calibrate", "error", "Calibration failed");
    }
}

void handleReset(JsonObject params) {
    String type = params["type"] | "full";
    timerStop(samplingTimer);

    if (type == "volume") {
        volume = 0;
        lastMeasurementTime = millis();
        sendResponse("reset", "success", "Volume reset");
    } else {
        volume = 0;
        lastMeasurementTime = millis();
        filterInitialized = false;
        bufferHead = 0;
        bufferTail = 0;
        currentState = STATE_READY;
        sendResponse("reset", "success", "Full reset completed");
    }
}

void handleStart() {
    if (currentState == STATE_READY) {
        currentState = STATE_MEASURING;
        volume = 0;
        lastMeasurementTime = millis();
        filterInitialized = false;
        bufferHead = 0;
        bufferTail = 0;

        timerStart(samplingTimer);
        sendResponse("start", "success", "Measurement started");
    } else {
        sendResponse("start", "error", "Cannot start measurement");
    }
}

void handleStop() {
    if (currentState == STATE_MEASURING) {
        timerStop(samplingTimer);
        currentState = STATE_READY;
        sendResponse("stop", "success", "Measurement stopped");
    } else {
        sendResponse("stop", "error", "Not measuring");
    }
}

void handleConfig(JsonObject params) {
    bool changed = false;

    if (params.containsKey("sampling_rate")) {
        int newRate = params["sampling_rate"];
        if (newRate >= 50 && newRate <= 1000) {
            samplingRate = newRate;
            timerAlarm(samplingTimer, 1000000 / samplingRate, true, 0);
            changed = true;
        }
    }

    if (params.containsKey("filter_alpha")) {
        float newAlpha = params["filter_alpha"];
        if (newAlpha > 0 && newAlpha <= 1) {
            alpha = newAlpha;
            changed = true;
        }
    }

    if (changed) {
        sendResponse("config", "success", "Configuration updated");
    } else {
        sendResponse("config", "error", "Invalid parameters");
    }
}

void sendBufferedData() {
    static FlowData lastSentData = {0, 0, 0, 0};
    FlowData data;
    int sentCount = 0;

    while (getFromBuffer(data) && sentCount < 10) {
        if (abs(data.pressure - lastSentData.pressure) < 0.0001 &&
            abs(data.flowRate - lastSentData.flowRate) < 0.01 &&
            abs(data.volume - lastSentData.volume) < 0.01) {
            continue;
        }

        StaticJsonDocument<200> doc;
        doc["type"] = "data";
        doc["device"] = "SPIRO";
        doc["timestamp"] = data.timestamp;

        JsonObject payload = doc.createNestedObject("payload");
        payload["pressure"] = roundf(data.pressure * 10000) / 10000;
        payload["flow"] = roundf(data.flowRate * 100) / 100;
        payload["volume"] = roundf(data.volume * 100) / 100;

        serializeJson(doc, Serial);
        Serial.println();

        lastSentData = data;
        sentCount++;
    }
}

bool performSelfTest() {
    int16_t adc0 = ads.readADC_SingleEnded(0);
    return adc0 != 0 && adc0 != 32767;
}

bool performCalibration() {
    float sumVoltages = 0;
    for (int i = 0; i < NUM_CALIBRATION_SAMPLES; i++) {
        int16_t adc0 = ads.readADC_SingleEnded(0);
        if (adc0 <= 100 || adc0 >= 32667) return false;
        float volt = ads.computeVolts(adc0);
        sumVoltages += volt;
        delay(10);
    }
    calibrationOffset = (sumVoltages / NUM_CALIBRATION_SAMPLES) - 2.5;
    return true;
}

float getPressureKPA(int channel) {
    int16_t adc = ads.readADC_SingleEnded(channel);
    if (adc <= 100 || adc >= 32667) return 0;
    float volt = ads.computeVolts(adc);
    float voltCalibrated = volt - calibrationOffset;
    return (voltCalibrated - 2.5) / 0.285;
}

float calculateFlowRate(float pressureKPA) {
    if (abs(pressureKPA) < PRESSURE_THRESHOLD) return 0;
    int direction = (pressureKPA >= 0) ? 1 : -1;
    float flowRate = direction * FLOW_CONSTANT * sqrt(abs(pressureKPA));
    return abs(flowRate) < FLOW_THRESHOLD ? 0 : flowRate;
}

void sendResponse(String command, String status, String message) {
    StaticJsonDocument<300> doc;
    doc["type"] = "response";
    doc["device"] = "SPIRO";
    doc["timestamp"] = millis();

    JsonObject payload = doc.createNestedObject("payload");
    payload["command"] = command;
    payload["status"] = status;
    payload["message"] = message;

    serializeJson(doc, Serial);
    Serial.println();
}

void sendErrorMessage(String error) {
    StaticJsonDocument<300> doc;
    doc["type"] = "error";
    doc["device"] = "SPIRO";
    doc["timestamp"] = millis();

    JsonObject payload = doc.createNestedObject("payload");
    payload["error"] = error;

    serializeJson(doc, Serial);
    Serial.println();
}

void sendDeviceInfo() {
    StaticJsonDocument<400> doc;
    doc["type"] = "status";
    doc["device"] = "SPIRO";
    doc["timestamp"] = millis();

    JsonObject payload = doc.createNestedObject("payload");
    payload["firmware_version"] = "2.0.0";
    payload["device_model"] = "ESP32-C3_SPIRO";
    payload["sampling_rate"] = samplingRate;
    payload["state"] = getStateString();
    payload["calibrated"] = (calibrationOffset != 0);
    payload["free_heap"] = ESP.getFreeHeap();

    serializeJson(doc, Serial);
    Serial.println();
}

String getStateString() {
    switch (currentState) {
        case STATE_BOOT: return "boot";
        case STATE_CALIBRATING: return "calibrating";
        case STATE_READY: return "ready";
        case STATE_MEASURING: return "measuring";
        case STATE_ERROR: return "error";
        default: return "unknown";
    }
}