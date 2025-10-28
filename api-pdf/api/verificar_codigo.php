<?php
/**
 * api/verificar_codigo.php - Verificar código y crear sesión
 * 
 * POST /api/verificar_codigo.php
 * Body: {
 *   "email": "estudiante@uach.cl",
 *   "codigo": "123456"
 * }
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

try {
    // Obtener datos
    $input = json_decode(file_get_contents('php://input'), true);
    $email = strtolower(trim($input['email'] ?? ''));
    $codigo = trim($input['codigo'] ?? '');
    
    if (empty($email) || empty($codigo)) {
        responderJSON([
            'success' => false,
            'error' => 'Email y código son requeridos'
        ], 400);
    }
    
    // Limpiar códigos expirados
    limpiarCodigosExpirados();
    
    // Verificar código
    $codigos = cargarJSON(CODIGOS_VERIFICACION_FILE);
    
    if (!isset($codigos[$email])) {
        responderJSON([
            'success' => false,
            'error' => 'Código no encontrado o expirado'
        ], 404);
    }
    
    $datos_codigo = $codigos[$email];
    
    // Verificar intentos
    if ($datos_codigo['intentos'] >= 5) {
        // Eliminar código
        unset($codigos[$email]);
        guardarJSON(CODIGOS_VERIFICACION_FILE, $codigos);
        
        responderJSON([
            'success' => false,
            'error' => 'Demasiados intentos fallidos. Solicita un nuevo código.'
        ], 403);
    }
    
    // Verificar código
    if ($datos_codigo['codigo'] !== $codigo) {
        // Incrementar intentos
        $codigos[$email]['intentos']++;
        guardarJSON(CODIGOS_VERIFICACION_FILE, $codigos);
        
        $intentos_restantes = 5 - $codigos[$email]['intentos'];
        
        responderJSON([
            'success' => false,
            'error' => 'Código incorrecto. Intentos restantes: ' . $intentos_restantes
        ], 400);
    }
    
    // Código válido - eliminar de la lista
    $actividad_id = $datos_codigo['actividad_id'];
    $token_actividad = $datos_codigo['token_actividad'];
    
    unset($codigos[$email]);
    guardarJSON(CODIGOS_VERIFICACION_FILE, $codigos);
    
    // Crear sesión de estudiante
    $sesiones = cargarJSON(SESIONES_ESTUDIANTES_FILE);
    $session_id = generarToken(32);
    
    $sesiones[$session_id] = [
        'session_id' => $session_id,
        'email' => $email,
        'actividad_id' => $actividad_id,
        'timestamp' => time(),
        'ip' => $_SERVER['REMOTE_ADDR'] ?? 'unknown',
        'user_agent' => $_SERVER['HTTP_USER_AGENT'] ?? 'unknown',
        'token_app_generado' => false
    ];
    
    guardarJSON(SESIONES_ESTUDIANTES_FILE, $sesiones);
    
    // Agregar estudiante a la lista de registrados de la actividad
    $actividades = cargarJSON(ACTIVIDADES_FILE);
    
    if (isset($actividades[$actividad_id])) {
        if (!in_array($email, $actividades[$actividad_id]['accesos']['estudiantes_registrados'])) {
            $actividades[$actividad_id]['accesos']['estudiantes_registrados'][] = $email;
            guardarJSON(ACTIVIDADES_FILE, $actividades);
        }
        
        $actividad = $actividades[$actividad_id];
    } else {
        responderJSON([
            'success' => false,
            'error' => 'Actividad no encontrada'
        ], 404);
    }
    
    responderJSON([
        'success' => true,
        'message' => 'Verificación exitosa',
        'data' => [
            'session_id' => $session_id,
            'email' => $email,
            'actividad' => [
                'id' => $actividad_id,
                'nombre' => $actividad['info_basica']['nombre'],
                'descripcion' => $actividad['info_basica']['descripcion'],
                'tipo_estudio' => $actividad['info_basica']['tipo_estudio'],
                'fecha_cierre' => $actividad['info_basica']['fecha_cierre']
            ]
        ]
    ], 200);
    
} catch (Exception $e) {
    responderJSON([
        'success' => false,
        'error' => 'Error del servidor: ' . $e->getMessage()
    ], 500);
}
?>