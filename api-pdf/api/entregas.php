<?php
/**
 * api/entregas.php - API para recibir entregas desde software externo
 * 
 * Endpoint principal que recibe archivos PDF y RAW desde FisioaccessPC Python
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

// Solo permitir POST
if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    responderJSON(['error' => 'Método no permitido'], 405);
}

/**
 * Validar y procesar upload de entrega
 */
try {
    // Validar que vengan archivos
    if (!isset($_FILES['pdf']) || !isset($_FILES['raw'])) {
        responderJSON([
            'success' => false,
            'error' => 'Se requieren archivos PDF y RAW'
        ], 400);
    }
    
    // Rate limiting por IP
    $ip = obtenerIP();
    if (!verificarRateLimit('ip', $ip)) {
        registrarEventoSeguridad('Rate limit excedido en entregas', ['ip' => $ip]);
        responderJSON([
            'success' => false,
            'error' => 'Demasiados intentos. Intenta nuevamente en 1 hora.'
        ], 429);
    }

    // Validar token del estudiante (REQUERIDO)
    $token = sanitizarString($_POST['token'] ?? '', ['max_length' => 6]);
    $comments = sanitizarString($_POST['comments'] ?? '', ['max_length' => 1000]);

    if (empty($token)) {
        responderJSON([
            'success' => false,
            'error' => 'Token de estudiante requerido. Por favor autentícate en el software.'
        ], 400);
    }

    // Registrar intento
    registrarIntento('ip', $ip);

    // Validar token contra tokens.json
    $tokens_file = DATA_PATH . '/tokens.json';
    if (!file_exists($tokens_file)) {
        responderJSON([
            'success' => false,
            'error' => 'Sistema de tokens no inicializado. Contacta al administrador.'
        ], 500);
    }

    $tokens = json_decode(file_get_contents($tokens_file), true) ?? [];

    if (!isset($tokens[$token])) {
        responderJSON([
            'success' => false,
            'error' => 'Token inválido o expirado. Genera un nuevo token desde la plataforma web.'
        ], 401);
    }

    $token_data = $tokens[$token];
    $estudiante_rut = $token_data['rut'];
    $actividad_id = $token_data['actividad_id'];

    // Verificar que el token no esté expirado
    $fecha_expira = strtotime($token_data['expira']);
    if (time() > $fecha_expira) {
        responderJSON([
            'success' => false,
            'error' => 'Token expirado. Genera un nuevo token desde la plataforma web.'
        ], 401);
    }

    // Actualizar último uso del token
    $tokens[$token]['ultimo_uso'] = formatearFecha();
    guardarJSON($tokens_file, $tokens);
    
    // Validar archivos subidos
    $pdf = $_FILES['pdf'];
    $raw = $_FILES['raw'];
    
    if ($pdf['error'] !== UPLOAD_ERR_OK) {
        responderJSON([
            'success' => false,
            'error' => 'Error al subir archivo PDF: ' . $pdf['error']
        ], 400);
    }
    
    if ($raw['error'] !== UPLOAD_ERR_OK) {
        responderJSON([
            'success' => false,
            'error' => 'Error al subir archivo RAW: ' . $raw['error']
        ], 400);
    }
    
    // Validar tamaños
    if ($pdf['size'] > PDF_MAX_SIZE) {
        responderJSON([
            'success' => false,
            'error' => 'El archivo PDF excede el tamaño máximo permitido (' . (PDF_MAX_SIZE / 1024 / 1024) . 'MB)'
        ], 400);
    }
    
    if ($raw['size'] > RAW_MAX_SIZE) {
        responderJSON([
            'success' => false,
            'error' => 'El archivo RAW excede el tamaño máximo permitido (' . (RAW_MAX_SIZE / 1024 / 1024) . 'MB)'
        ], 400);
    }
    
    // Validar extensiones
    $pdf_ext = strtolower(pathinfo($pdf['name'], PATHINFO_EXTENSION));
    $raw_ext = strtolower(pathinfo($raw['name'], PATHINFO_EXTENSION));
    
    if ($pdf_ext !== 'pdf') {
        responderJSON([
            'success' => false,
            'error' => 'El archivo debe ser PDF'
        ], 400);
    }
    
    if ($raw_ext !== 'json') {
        responderJSON([
            'success' => false,
            'error' => 'El archivo RAW debe ser JSON'
        ], 400);
    }
    
    // Generar ID único para la entrega
    $entrega_id = generarID('ENT');

    // Verificar que la actividad existe y está abierta
    $actividades = cargarJSON(ACTIVIDADES_FILE);

    if (!isset($actividades[$actividad_id])) {
        responderJSON([
            'success' => false,
            'error' => 'Actividad no encontrada. El token puede estar asociado a una actividad eliminada.'
        ], 404);
    }

    $actividad = $actividades[$actividad_id];

    // Verificar que la actividad esté abierta
    $ahora = time();
    $fecha_inicio = strtotime($actividad['info_basica']['fecha_inicio']);
    $fecha_cierre = strtotime($actividad['info_basica']['fecha_cierre']);

    if ($ahora < $fecha_inicio) {
        responderJSON([
            'success' => false,
            'error' => 'La actividad aún no ha comenzado. Espera hasta el ' .
                      date('d/m/Y H:i', $fecha_inicio)
        ], 403);
    }

    if ($ahora > $fecha_cierre) {
        responderJSON([
            'success' => false,
            'error' => 'La actividad ha finalizado. No se aceptan más entregas.'
        ], 403);
    }

    // Verificar que el estudiante está inscrito en la actividad
    if (!in_array($estudiante_rut, $actividad['estudiantes_inscritos'] ?? [])) {
        responderJSON([
            'success' => false,
            'error' => 'No estás inscrito en esta actividad. Contacta a tu profesor.'
        ], 403);
    }

    // Crear carpeta de entregas para la actividad
    $carpeta_entregas = UPLOADS_PATH . '/' . $actividad_id . '/entregas';

    if (!is_dir($carpeta_entregas)) {
        mkdir($carpeta_entregas, 0755, true);
    }
    
    // Generar nombres únicos para archivos
    $timestamp = time();
    $pdf_filename = $entrega_id . '_' . $timestamp . '.pdf';
    $raw_filename = $entrega_id . '_' . $timestamp . '.json';
    
    $pdf_destino = $carpeta_entregas . '/' . $pdf_filename;
    $raw_destino = $carpeta_entregas . '/' . $raw_filename;
    
    // Mover archivos
    if (!move_uploaded_file($pdf['tmp_name'], $pdf_destino)) {
        responderJSON([
            'success' => false,
            'error' => 'Error al guardar archivo PDF'
        ], 500);
    }
    
    if (!move_uploaded_file($raw['tmp_name'], $raw_destino)) {
        // Si falla RAW, eliminar PDF
        unlink($pdf_destino);
        responderJSON([
            'success' => false,
            'error' => 'Error al guardar archivo RAW'
        ], 500);
    }
    
    // Crear registro de entrega
    $entregas = cargarJSON(ENTREGAS_FILE);

    // Obtener información del estudiante
    $estudiantes = cargarJSON(ESTUDIANTES_FILE);
    $estudiante = $estudiantes[$estudiante_rut] ?? null;
    $nombre_estudiante = $estudiante['nombre'] ?? 'Desconocido';

    $entregas[$entrega_id] = [
        'id' => $entrega_id,
        'actividad_id' => $actividad_id,
        'estudiante_rut' => $estudiante_rut,
        'estudiante_nombre' => $nombre_estudiante,
        'timestamp' => formatearFecha(),
        'metadata' => [
            'token_usado' => $token,
            'tipo_estudio' => $actividad['info_basica']['tipo_estudio'],
            'comments' => $comments
        ],
        'archivos' => [
            'pdf' => str_replace(BASE_PATH . '/', '', $pdf_destino),
            'raw' => str_replace(BASE_PATH . '/', '', $raw_destino),
            'pdf_filename' => $pdf_filename,
            'raw_filename' => $raw_filename,
            'pdf_size' => $pdf['size'],
            'raw_size' => $raw['size']
        ],
        'revision' => [
            'estado' => 'pendiente',
            'nota' => null,
            'retroalimentacion' => '',
            'fecha_revision' => null,
            'revisor_rut' => null
        ],
        'origen' => 'api',
        'ip' => $_SERVER['REMOTE_ADDR'] ?? 'unknown'
    ];
    
    guardarJSON(ENTREGAS_FILE, $entregas);

    // Registrar evento
    registrarLog('INFO', 'Entrega recibida via API con token', [
        'entrega_id' => $entrega_id,
        'actividad_id' => $actividad_id,
        'estudiante_rut' => $estudiante_rut,
        'estudiante_nombre' => $nombre_estudiante,
        'token' => $token,
        'ip' => $ip
    ]);

    // Actualizar estadísticas de actividad
    $actividades[$actividad_id]['estadisticas']['entregas_realizadas']++;
    $actividades[$actividad_id]['estadisticas']['entregas_pendientes']++;
    guardarJSON(ACTIVIDADES_FILE, $actividades);
    
    // Respuesta exitosa
    responderJSON([
        'success' => true,
        'message' => 'Entrega recibida exitosamente',
        'data' => [
            'id' => $entrega_id,
            'actividad_id' => $actividad_id,
            'timestamp' => $entregas[$entrega_id]['timestamp'],
            'pdf_url' => $entregas[$entrega_id]['archivos']['pdf'],
            'raw_url' => $entregas[$entrega_id]['archivos']['raw']
        ]
    ], 200);
    
} catch (Exception $e) {
    responderJSON([
        'success' => false,
        'error' => 'Error del servidor: ' . $e->getMessage()
    ], 500);
}