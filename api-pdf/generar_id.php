<?php
/**
 * generar_id.php - Genera IDs únicos para uploads con reserva temporal
 * 
 * POST con:
 *   - actividad_id: ID de la actividad
 *   - rut: RUT del estudiante
 * 
 * Retorna:
 *   - upload_id: ID único generado
 *   - expires_in: segundos hasta expiración
 */

header('Content-Type: application/json');

// Solo POST
if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    http_response_code(405);
    echo json_encode(['error' => 'Método no permitido']);
    exit;
}

// Constantes
const TIPOS_ESTUDIO = [
    'espirometria' => 'Espirometría',
    'ecg' => 'Electrocardiograma',
    'emg' => 'Electromiografía',
    'eeg' => 'Electroencefalograma'
];

const RESERVA_TTL = 300; // 5 minutos en segundos

$dataDir = __DIR__ . '/data/';
$actividadesFile = $dataDir . 'actividades.json';
$reservasFile = $dataDir . 'reservas_ids.json';

// Crear directorio si no existe
if (!is_dir($dataDir)) {
    mkdir($dataDir, 0755, true);
}

// ========== VALIDAR CAMPOS REQUERIDOS ==========
if (empty($_POST['actividad_id']) || empty($_POST['rut'])) {
    http_response_code(400);
    echo json_encode(['error' => 'Faltan campos: actividad_id, rut']);
    exit;
}

$actividadId = trim($_POST['actividad_id']);
$rut = trim($_POST['rut']);

// ========== CARGAR ACTIVIDADES ==========
if (!file_exists($actividadesFile)) {
    http_response_code(404);
    echo json_encode(['error' => 'No existen actividades creadas']);
    exit;
}

$actividades = json_decode(file_get_contents($actividadesFile), true);

// ========== VALIDAR QUE LA ACTIVIDAD EXISTE ==========
if (!isset($actividades[$actividadId])) {
    http_response_code(404);
    echo json_encode(['error' => 'Actividad no encontrada']);
    exit;
}

$actividad = $actividades[$actividadId];

// ========== VALIDAR QUE EL USUARIO TIENE PERMISO ==========
// Si la actividad no es pública, verificar que el usuario esté en la lista
if (!$actividad['publico']) {
    $usuariosPermitidos = $actividad['usuarios_permitidos'] ?? [];
    
    if (!in_array($rut, $usuariosPermitidos)) {
        http_response_code(403);
        echo json_encode(['error' => 'Usuario no autorizado para esta actividad']);
        exit;
    }
}

// ========== GENERAR ID ÚNICO ==========
$timestamp = microtime(true);
$random = bin2hex(random_bytes(4));
$uploadId = sprintf(
    '%s_%s_%d_%s',
    $actividadId,
    str_replace(['.', '-'], '', $rut), // Limpiar RUT
    (int)($timestamp * 1000), // Timestamp en milisegundos
    $random
);

// ========== CARGAR RESERVAS EXISTENTES ==========
$reservas = [];
if (file_exists($reservasFile)) {
    $reservas = json_decode(file_get_contents($reservasFile), true) ?: [];
}

// ========== LIMPIAR RESERVAS EXPIRADAS ==========
$now = time();
$reservas = array_filter($reservas, function($reserva) use ($now) {
    return $reserva['expires_at'] > $now;
});

// ========== GUARDAR NUEVA RESERVA ==========
$reservas[$uploadId] = [
    'upload_id' => $uploadId,
    'actividad_id' => $actividadId,
    'rut' => $rut,
    'tipo' => $actividad['tipo'],
    'created_at' => $now,
    'expires_at' => $now + RESERVA_TTL
];

file_put_contents($reservasFile, json_encode($reservas, JSON_PRETTY_PRINT));

// ========== RESPONDER ==========
http_response_code(200);
echo json_encode([
    'upload_id' => $uploadId,
    'actividad_id' => $actividadId,
    'tipo' => $actividad['tipo'],
    'expires_in' => RESERVA_TTL,
    'message' => 'ID generado exitosamente. Válido por ' . RESERVA_TTL . ' segundos'
]);