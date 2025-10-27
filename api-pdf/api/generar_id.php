<?php
/**
 * api/generar_id.php - Generar IDs únicos para reserva
 * 
 * GET /api/generar_id.php?tipo=entrega
 * GET /api/generar_id.php?tipo=actividad
 */

require_once '../config.php';

header('Content-Type: application/json; charset=utf-8');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: GET, OPTIONS');

if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    http_response_code(200);
    exit;
}

if ($_SERVER['REQUEST_METHOD'] !== 'GET') {
    responderJSON(['error' => 'Método no permitido'], 405);
}

try {
    $tipo = $_GET['tipo'] ?? 'entrega';
    
    $prefijos = [
        'entrega' => 'ENT',
        'actividad' => 'ACT',
        'estudiante' => 'EST'
    ];
    
    if (!isset($prefijos[$tipo])) {
        responderJSON([
            'success' => false,
            'error' => 'Tipo no válido. Use: entrega, actividad, estudiante'
        ], 400);
    }
    
    $id = generarID($prefijos[$tipo]);
    
    // Guardar en reservas (opcional, para tracking)
    $reservas = cargarJSON(RESERVAS_FILE);
    $reservas[$id] = [
        'id' => $id,
        'tipo' => $tipo,
        'generado' => formatearFecha(),
        'usado' => false
    ];
    guardarJSON(RESERVAS_FILE, $reservas);
    
    responderJSON([
        'success' => true,
        'data' => [
            'id' => $id,
            'tipo' => $tipo,
            'timestamp' => $reservas[$id]['generado']
        ]
    ], 200);
    
} catch (Exception $e) {
    responderJSON([
        'success' => false,
        'error' => 'Error del servidor: ' . $e->getMessage()
    ], 500);
}