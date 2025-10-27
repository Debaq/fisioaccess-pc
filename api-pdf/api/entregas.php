<?php
/**
 * api/entregas.php - API para recibir entregas desde software externo
 * 
 * Endpoint principal que recibe archivos PDF y RAW desde FisioaccessPC Python
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
    
    // Validar metadata
    $owner = trim($_POST['owner'] ?? '');
    $type = trim($_POST['type'] ?? '');
    $comments = trim($_POST['comments'] ?? '');
    
    if (empty($owner)) {
        responderJSON([
            'success' => false,
            'error' => 'Se requiere información del propietario (owner)'
        ], 400);
    }
    
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
    
    // Determinar actividad y estudiante desde el RAW (si viene estructurado)
    $raw_temp = $raw['tmp_name'];
    $raw_data = json_decode(file_get_contents($raw_temp), true);
    
    // Intentar extraer información del RAW
    $estudiante_rut = null;
    $actividad_id = null;
    
    if ($raw_data && isset($raw_data['patient'])) {
        $estudiante_rut = $raw_data['patient']['rut'] ?? null;
    }
    
    // Si no viene actividad_id en POST, buscar actividad abierta del tipo correcto
    $actividad_id = $_POST['actividad_id'] ?? null;
    
    if (empty($actividad_id)) {
        // Buscar actividad abierta del tipo de estudio correcto
        $actividades = cargarJSON(ACTIVIDADES_FILE);
        $tipo_estudio = $_POST['tipo_estudio'] ?? 'espirometria';
        
        $actividades_abiertas = array_filter($actividades, function($act) use ($tipo_estudio) {
            $ahora = time();
            $fecha_inicio = strtotime($act['info_basica']['fecha_inicio']);
            $fecha_cierre = strtotime($act['info_basica']['fecha_cierre']);
            
            return $act['info_basica']['tipo_estudio'] === $tipo_estudio &&
                   $fecha_inicio <= $ahora &&
                   $fecha_cierre >= $ahora;
        });
        
        if (!empty($actividades_abiertas)) {
            $actividad = reset($actividades_abiertas);
            $actividad_id = $actividad['id'];
        }
    }
    
    // Si no se encuentra actividad, crear carpeta genérica "sin_actividad"
    if (empty($actividad_id)) {
        $actividad_id = 'sin_actividad';
        $carpeta_entregas = UPLOADS_PATH . '/sin_actividad';
        
        if (!is_dir($carpeta_entregas)) {
            mkdir($carpeta_entregas, 0755, true);
        }
    } else {
        $carpeta_entregas = UPLOADS_PATH . '/' . $actividad_id . '/entregas';
        
        if (!is_dir($carpeta_entregas)) {
            mkdir($carpeta_entregas, 0755, true);
        }
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
    
    $entregas[$entrega_id] = [
        'id' => $entrega_id,
        'actividad_id' => $actividad_id,
        'estudiante_rut' => $estudiante_rut ?? 'desconocido',
        'timestamp' => formatearFecha(),
        'metadata' => [
            'owner' => $owner,
            'type' => $type,
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
    
    // Actualizar estadísticas de actividad si existe
    if ($actividad_id !== 'sin_actividad') {
        $actividades = cargarJSON(ACTIVIDADES_FILE);
        
        if (isset($actividades[$actividad_id])) {
            $actividades[$actividad_id]['estadisticas']['entregas_realizadas']++;
            $actividades[$actividad_id]['estadisticas']['entregas_pendientes']++;
            guardarJSON(ACTIVIDADES_FILE, $actividades);
        }
    }
    
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