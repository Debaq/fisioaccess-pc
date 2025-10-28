<?php
/**
 * api/tokens_app.php - Generar y validar tokens para app Python
 * 
 * POST /api/tokens_app.php?action=generar
 * Body: { "session_id": "..." }
 * 
 * POST /api/tokens_app.php?action=validar
 * Body: { "token": "..." }
 */

require_once '../config.php';

header('Content-Type: application/json; charset=utf-8');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: POST, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type');

// Manejar preflight OPTIONS
if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    http_response_code(200);
    exit;
}

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    responderJSON([
        'success' => false,
        'error' => 'Método no permitido'
    ], 405);
}

$action = $_GET['action'] ?? '';

try {
    if ($action === 'generar') {
        handleGenerar();
    } elseif ($action === 'validar') {
        handleValidar();
    } else {
        responderJSON([
            'success' => false,
            'error' => 'Acción no válida. Usa: generar o validar'
        ], 400);
    }
} catch (Exception $e) {
    responderJSON([
        'success' => false,
        'error' => 'Error del servidor: ' . $e->getMessage()
    ], 500);
}

/**
 * Generar token para app
 */
function handleGenerar() {
    $input = json_decode(file_get_contents('php://input'), true);
    $session_id = trim($input['session_id'] ?? '');
    
    if (empty($session_id)) {
        responderJSON([
            'success' => false,
            'error' => 'session_id es requerido'
        ], 400);
    }
    
    // Verificar sesión
    $sesiones = cargarJSON(SESIONES_ESTUDIANTES_FILE);
    
    if (!isset($sesiones[$session_id])) {
        responderJSON([
            'success' => false,
            'error' => 'Sesión no encontrada o expirada'
        ], 404);
    }
    
    $sesion = $sesiones[$session_id];
    
    // Verificar que la sesión no haya expirado (2 horas)
    if (time() - $sesion['timestamp'] > SESSION_TIMEOUT) {
        unset($sesiones[$session_id]);
        guardarJSON(SESIONES_ESTUDIANTES_FILE, $sesiones);
        
        responderJSON([
            'success' => false,
            'error' => 'Sesión expirada. Inicia sesión nuevamente.'
        ], 403);
    }
    
    // Limpiar tokens expirados
    limpiarTokensExpirados();
    
    // Generar token
    $token = generarToken(12); // Formato: ABCD-1234-WXYZ
    $tokens = cargarJSON(TOKENS_APP_FILE);
    
    $tokens[$token] = [
        'token' => $token,
        'session_id' => $session_id,
        'email' => $sesion['email'],
        'actividad_id' => $sesion['actividad_id'],
        'timestamp' => time(),
        'ultimo_uso' => time(),
        'ip_generacion' => $_SERVER['REMOTE_ADDR'] ?? 'unknown'
    ];
    
    guardarJSON(TOKENS_APP_FILE, $tokens);
    
    // Marcar en la sesión que se generó token
    $sesiones[$session_id]['token_app_generado'] = true;
    $sesiones[$session_id]['ultimo_token'] = $token;
    guardarJSON(SESIONES_ESTUDIANTES_FILE, $sesiones);
    
    // Obtener info de la actividad
    $actividades = cargarJSON(ACTIVIDADES_FILE);
    $actividad = $actividades[$sesion['actividad_id']] ?? null;
    
    responderJSON([
        'success' => true,
        'message' => 'Token generado exitosamente',
        'data' => [
            'token' => $token,
            'expira_en' => TOKEN_APP_TIMEOUT,
            'email' => $sesion['email'],
            'actividad' => [
                'id' => $sesion['actividad_id'],
                'nombre' => $actividad['info_basica']['nombre'] ?? 'N/A'
            ]
        ]
    ], 200);
}

/**
 * Validar token desde app
 */
function handleValidar() {
    $input = json_decode(file_get_contents('php://input'), true);
    $token = trim($input['token'] ?? '');
    
    if (empty($token)) {
        responderJSON([
            'success' => false,
            'error' => 'Token es requerido'
        ], 400);
    }
    
    // Limpiar tokens expirados
    limpiarTokensExpirados();
    
    // Verificar token
    $tokens = cargarJSON(TOKENS_APP_FILE);
    
    if (!isset($tokens[$token])) {
        responderJSON([
            'success' => false,
            'error' => 'Token inválido o expirado'
        ], 404);
    }
    
    $token_data = $tokens[$token];
    
    // Actualizar último uso
    $tokens[$token]['ultimo_uso'] = time();
    guardarJSON(TOKENS_APP_FILE, $tokens);
    
    // Obtener información de la actividad
    $actividades = cargarJSON(ACTIVIDADES_FILE);
    $actividad = $actividades[$token_data['actividad_id']] ?? null;
    
    if (!$actividad) {
        responderJSON([
            'success' => false,
            'error' => 'Actividad no encontrada'
        ], 404);
    }
    
    // Verificar que la actividad siga abierta
    $ahora = time();
    $fecha_cierre = strtotime($actividad['info_basica']['fecha_cierre']);
    
    if ($ahora > $fecha_cierre) {
        responderJSON([
            'success' => false,
            'error' => 'La actividad ha finalizado'
        ], 403);
    }
    
    // Obtener cuotas disponibles
    $cuotas = $actividad['configuracion']['cuota_estudios'];
    
    responderJSON([
        'success' => true,
        'message' => 'Token válido',
        'data' => [
            'email' => $token_data['email'],
            'actividad' => [
                'id' => $token_data['actividad_id'],
                'nombre' => $actividad['info_basica']['nombre'],
                'tipo_estudio' => $actividad['info_basica']['tipo_estudio'],
                'descripcion' => $actividad['info_basica']['descripcion'],
                'fecha_cierre' => $actividad['info_basica']['fecha_cierre'],
                'cuotas' => $cuotas
            ],
            'tiempo_restante' => TOKEN_APP_TIMEOUT - (time() - $token_data['timestamp'])
        ]
    ], 200);
}
?>