<?php
/**
 * api/generar_id.php - Generar IDs únicos para reserva
 * 
 * GET /api/generar_id.php?tipo=entrega
 * GET /api/generar_id.php?tipo=actividad
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

if ($_SERVER['REQUEST_METHOD'] !== 'GET') {
    responderJSON(['error' => 'Método no permitido'], 405);
}

// Rate limiting por IP (20 intentos/hora para generación de IDs)
$ip = obtenerIP();
if (!verificarRateLimit('generar_id_ip', $ip, 20, 3600)) {
    registrarEventoSeguridad('Rate limit excedido en generar_id', ['ip' => $ip]);
    responderJSON([
        'success' => false,
        'error' => 'Demasiadas solicitudes. Intenta nuevamente más tarde.'
    ], 429);
}

registrarIntento('generar_id_ip', $ip);

try {
    // Sanitizar tipo
    $tipo = sanitizarString($_GET['tipo'] ?? 'entrega', ['max_length' => 20]);
    
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
        'usado' => false,
        'ip' => $ip
    ];
    guardarJSON(RESERVAS_FILE, $reservas);

    // Logging
    registrarLog('INFO', 'ID generado', [
        'id' => $id,
        'tipo' => $tipo,
        'ip' => $ip
    ]);

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