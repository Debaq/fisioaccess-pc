<?php
/**
 * api/materiales.php - API para descargar materiales de actividades
 * 
 * GET /api/materiales.php?actividad=ACT123&tipo=guia
 * GET /api/materiales.php?actividad=ACT123&tipo=complementario&index=0
 */

require_once '../config.php';

// Configurar CORS de forma segura
configurarCORS();

if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    http_response_code(200);
    exit;
}

if ($_SERVER['REQUEST_METHOD'] !== 'GET') {
    responderJSON(['error' => 'Método no permitido'], 405);
}

try {
    // Sanitizar parámetros de entrada
    $actividad_id = sanitizarString($_GET['actividad'] ?? '', ['max_length' => 50]);
    $tipo = sanitizarString($_GET['tipo'] ?? '', ['max_length' => 20]);

    if (empty($actividad_id) || empty($tipo)) {
        responderJSON(['error' => 'Parámetros requeridos: actividad, tipo'], 400);
    }

    // Validar que no contenga caracteres peligrosos (path traversal)
    if (preg_match('/[\.\/\\\\]/', $actividad_id)) {
        registrarEventoSeguridad('Intento de path traversal en materiales', [
            'actividad_id' => $actividad_id,
            'ip' => obtenerIP()
        ]);
        responderJSON(['error' => 'Parámetro inválido'], 400);
    }

    $actividades = cargarJSON(ACTIVIDADES_FILE);

    if (!isset($actividades[$actividad_id])) {
        responderJSON(['error' => 'Actividad no encontrada'], 404);
    }
    
    $actividad = $actividades[$actividad_id];
    $material_path = null;
    $filename = '';
    
    // Guía de laboratorio
    if ($tipo === 'guia') {
        if (empty($actividad['material_pedagogico']['guia_laboratorio'])) {
            responderJSON(['error' => 'Guía de laboratorio no disponible'], 404);
        }

        $guia = $actividad['material_pedagogico']['guia_laboratorio'];
        $material_path = BASE_PATH . '/' . $guia['url'];
        $filename = $guia['filename'];
    }

    // Material complementario
    elseif ($tipo === 'complementario') {
        $index = intval($_GET['index'] ?? 0);

        if ($index < 0 || !isset($actividad['material_pedagogico']['material_complementario'][$index])) {
            responderJSON(['error' => 'Material no encontrado'], 404);
        }

        $material = $actividad['material_pedagogico']['material_complementario'][$index];

        if ($material['tipo'] === 'link') {
            // Registrar descarga de link externo
            registrarLog('INFO', 'Descarga material externo', [
                'actividad_id' => $actividad_id,
                'url' => $material['url'],
                'ip' => obtenerIP()
            ]);

            // Redirigir a link externo
            header('Location: ' . $material['url']);
            exit;
        }

        $material_path = BASE_PATH . '/' . $material['url'];
        $filename = $material['filename'];
    }

    else {
        responderJSON(['error' => 'Tipo de material no válido'], 400);
    }
    
    // Verificar que existe el archivo
    if (!file_exists($material_path)) {
        responderJSON(['error' => 'Archivo no encontrado en el servidor'], 404);
    }

    // Validar que el path está dentro de la carpeta permitida (prevenir path traversal)
    $real_path = realpath($material_path);
    $real_base = realpath(BASE_PATH);

    if ($real_path === false || strpos($real_path, $real_base) !== 0) {
        registrarEventoSeguridad('Intento de acceso a archivo fuera de directorio permitido', [
            'material_path' => $material_path,
            'real_path' => $real_path,
            'ip' => obtenerIP()
        ]);
        responderJSON(['error' => 'Acceso denegado'], 403);
    }

    // Registrar descarga
    registrarLog('INFO', 'Descarga de material', [
        'actividad_id' => $actividad_id,
        'tipo' => $tipo,
        'filename' => $filename,
        'ip' => obtenerIP()
    ]);

    // Descargar archivo
    $mime_type = mime_content_type($material_path);

    header('Content-Type: ' . $mime_type);
    header('Content-Disposition: attachment; filename="' . basename($filename) . '"');
    header('Content-Length: ' . filesize($material_path));
    header('X-Content-Type-Options: nosniff');

    readfile($material_path);
    exit;

} catch (Exception $e) {
    registrarLog('ERROR', 'Error en descarga de material', [
        'error' => $e->getMessage(),
        'file' => $e->getFile(),
        'line' => $e->getLine()
    ]);
    responderJSON(['error' => 'Error del servidor'], 500);
}