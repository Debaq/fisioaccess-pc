<?php
/**
 * api/actividades.php - API CRUD de actividades
 * 
 * Endpoints:
 * GET    /api/actividades.php                      - Listar todas
 * GET    /api/actividades.php?id=ACT123           - Ver una
 * GET    /api/actividades.php?abiertas=1          - Listar abiertas
 * GET    /api/actividades.php?tipo=espirometria   - Filtrar por tipo
 */

require_once '../config.php';

header('Content-Type: application/json; charset=utf-8');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: GET, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type');

if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    http_response_code(200);
    exit;
}

if ($_SERVER['REQUEST_METHOD'] !== 'GET') {
    responderJSON(['error' => 'Método no permitido'], 405);
}

try {
    $actividades = cargarJSON(ACTIVIDADES_FILE);
    
    // Ver actividad específica
    if (isset($_GET['id'])) {
        $id = $_GET['id'];
        
        if (!isset($actividades[$id])) {
            responderJSON([
                'success' => false,
                'error' => 'Actividad no encontrada'
            ], 404);
        }
        
        responderJSON([
            'success' => true,
            'data' => $actividades[$id]
        ], 200);
    }
    
    // Filtros
    $filtradas = $actividades;
    
    // Filtrar por actividades abiertas
    if (isset($_GET['abiertas']) && $_GET['abiertas'] == '1') {
        $ahora = time();
        $filtradas = array_filter($filtradas, function($act) use ($ahora) {
            $fecha_inicio = strtotime($act['info_basica']['fecha_inicio']);
            $fecha_cierre = strtotime($act['info_basica']['fecha_cierre']);
            return $fecha_inicio <= $ahora && $fecha_cierre >= $ahora;
        });
    }
    
    // Filtrar por tipo de estudio
    if (isset($_GET['tipo'])) {
        $tipo = $_GET['tipo'];
        $filtradas = array_filter($filtradas, function($act) use ($tipo) {
            return $act['info_basica']['tipo_estudio'] === $tipo;
        });
    }
    
    // Filtrar por profesor
    if (isset($_GET['profesor_rut'])) {
        $rut = $_GET['profesor_rut'];
        $filtradas = array_filter($filtradas, function($act) use ($rut) {
            return $act['profesor_rut'] === $rut;
        });
    }
    
    responderJSON([
        'success' => true,
        'count' => count($filtradas),
        'data' => array_values($filtradas)
    ], 200);
    
} catch (Exception $e) {
    responderJSON([
        'success' => false,
        'error' => 'Error del servidor: ' . $e->getMessage()
    ], 500);
}