<?php
/**
 * api/validar_token.php - Validar token de estudiante sin subir archivos
 * Usado por el software PC para autenticación inicial
 *
 * POST /api/validar_token.php
 * Body: {
 *   "token": "A3B7X9"
 * }
 */

require_once '../config.php';

// Configurar CORS de forma segura
configurarCORS();

// Manejar preflight OPTIONS
if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    http_response_code(200);
    exit;
}

header('Content-Type: application/json; charset=utf-8');

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    responderJSON([
        'success' => false,
        'error' => 'Método no permitido'
    ], 405);
}

try {
    // Obtener datos
    $input = json_decode(file_get_contents('php://input'), true);
    $token = sanitizarString($input['token'] ?? '', ['max_length' => 6]);

    if (empty($token)) {
        responderJSON([
            'success' => false,
            'error' => 'Token requerido'
        ], 400);
    }

    // Rate limiting por IP
    $ip = obtenerIP();
    if (!verificarRateLimit('validar_token', $ip, 20, 3600)) {
        registrarEventoSeguridad('Rate limit excedido en validar_token', ['ip' => $ip]);
        responderJSON([
            'success' => false,
            'error' => 'Demasiados intentos. Intenta nuevamente en 1 hora.'
        ], 429);
    }

    registrarIntento('validar_token', $ip);

    // Cargar tokens
    $tokens_file = DATA_PATH . '/tokens.json';
    if (!file_exists($tokens_file)) {
        responderJSON([
            'success' => false,
            'error' => 'Sistema de tokens no inicializado'
        ], 500);
    }

    $tokens = json_decode(file_get_contents($tokens_file), true) ?? [];

    if (!isset($tokens[$token])) {
        responderJSON([
            'success' => false,
            'error' => 'Token inválido o no existe. Verifica que hayas generado el token desde la plataforma web.'
        ], 401);
    }

    $token_data = $tokens[$token];

    // Verificar expiración
    $fecha_expira = strtotime($token_data['expira']);
    if (time() > $fecha_expira) {
        responderJSON([
            'success' => false,
            'error' => 'Token expirado. Genera un nuevo token desde la plataforma web.'
        ], 401);
    }

    // Obtener información de la actividad
    $actividad_id = $token_data['actividad_id'];
    $actividades = cargarJSON(ACTIVIDADES_FILE);

    if (!isset($actividades[$actividad_id])) {
        responderJSON([
            'success' => false,
            'error' => 'La actividad asociada a este token no existe. Puede haber sido eliminada.'
        ], 404);
    }

    $actividad = $actividades[$actividad_id];

    // Verificar que la actividad esté activa
    $ahora = time();
    $fecha_inicio = strtotime($actividad['info_basica']['fecha_inicio']);
    $fecha_cierre = strtotime($actividad['info_basica']['fecha_cierre']);

    if ($ahora < $fecha_inicio) {
        responderJSON([
            'success' => false,
            'error' => 'La actividad aún no ha comenzado. Disponible desde el ' .
                      date('d/m/Y H:i', $fecha_inicio)
        ], 403);
    }

    if ($ahora > $fecha_cierre) {
        responderJSON([
            'success' => false,
            'error' => 'La actividad ha finalizado. No se aceptan más entregas.'
        ], 403);
    }

    // Obtener información del estudiante
    $estudiante_rut = $token_data['rut'];
    $estudiantes = cargarJSON(ESTUDIANTES_FILE);
    $estudiante = $estudiantes[$estudiante_rut] ?? null;

    if (!$estudiante) {
        responderJSON([
            'success' => false,
            'error' => 'Estudiante no encontrado'
        ], 404);
    }

    // Actualizar último uso del token
    $tokens[$token]['ultimo_uso'] = formatearFecha();
    guardarJSON($tokens_file, $tokens);

    // Registrar validación exitosa
    registrarLog('INFO', 'Token validado desde software PC', [
        'token' => $token,
        'estudiante_rut' => $estudiante_rut,
        'actividad_id' => $actividad_id,
        'ip' => $ip
    ]);

    // Respuesta exitosa
    responderJSON([
        'success' => true,
        'message' => 'Token válido',
        'data' => [
            'token' => $token,
            'estudiante_rut' => $estudiante_rut,
            'estudiante_nombre' => $estudiante['nombre'],
            'estudiante_email' => $estudiante['email'],
            'actividad_id' => $actividad_id,
            'actividad_nombre' => $actividad['info_basica']['nombre'],
            'actividad_tipo' => $actividad['info_basica']['tipo_estudio'],
            'actividad_descripcion' => $actividad['info_basica']['descripcion'],
            'fecha_cierre' => $actividad['info_basica']['fecha_cierre'],
            'expira' => $token_data['expira']
        ]
    ], 200);

} catch (Exception $e) {
    responderJSON([
        'success' => false,
        'error' => 'Error del servidor: ' . $e->getMessage()
    ], 500);
}
?>
