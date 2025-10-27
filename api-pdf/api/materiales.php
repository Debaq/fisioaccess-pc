<?php
/**
 * api/materiales.php - API para descargar materiales de actividades
 * 
 * GET /api/materiales.php?actividad=ACT123&tipo=guia
 * GET /api/materiales.php?actividad=ACT123&tipo=complementario&index=0
 */

require_once '../config.php';

header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: GET, OPTIONS');

if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    http_response_code(200);
    exit;
}

if ($_SERVER['REQUEST_METHOD'] !== 'GET') {
    http_response_code(405);
    die('Método no permitido');
}

try {
    $actividad_id = $_GET['actividad'] ?? '';
    $tipo = $_GET['tipo'] ?? '';
    
    if (empty($actividad_id) || empty($tipo)) {
        http_response_code(400);
        die('Parámetros requeridos: actividad, tipo');
    }
    
    $actividades = cargarJSON(ACTIVIDADES_FILE);
    
    if (!isset($actividades[$actividad_id])) {
        http_response_code(404);
        die('Actividad no encontrada');
    }
    
    $actividad = $actividades[$actividad_id];
    $material_path = null;
    $filename = '';
    
    // Guía de laboratorio
    if ($tipo === 'guia') {
        if (empty($actividad['material_pedagogico']['guia_laboratorio'])) {
            http_response_code(404);
            die('Guía de laboratorio no disponible');
        }
        
        $guia = $actividad['material_pedagogico']['guia_laboratorio'];
        $material_path = BASE_PATH . '/' . $guia['url'];
        $filename = $guia['filename'];
    }
    
    // Material complementario
    elseif ($tipo === 'complementario') {
        $index = intval($_GET['index'] ?? 0);
        
        if (!isset($actividad['material_pedagogico']['material_complementario'][$index])) {
            http_response_code(404);
            die('Material no encontrado');
        }
        
        $material = $actividad['material_pedagogico']['material_complementario'][$index];
        
        if ($material['tipo'] === 'link') {
            // Redirigir a link externo
            header('Location: ' . $material['url']);
            exit;
        }
        
        $material_path = BASE_PATH . '/' . $material['url'];
        $filename = $material['filename'];
    }
    
    else {
        http_response_code(400);
        die('Tipo de material no válido');
    }
    
    // Verificar que existe el archivo
    if (!file_exists($material_path)) {
        http_response_code(404);
        die('Archivo no encontrado en el servidor');
    }
    
    // Descargar archivo
    $mime_type = mime_content_type($material_path);
    
    header('Content-Type: ' . $mime_type);
    header('Content-Disposition: attachment; filename="' . $filename . '"');
    header('Content-Length: ' . filesize($material_path));
    
    readfile($material_path);
    exit;
    
} catch (Exception $e) {
    http_response_code(500);
    die('Error del servidor: ' . $e->getMessage());
}