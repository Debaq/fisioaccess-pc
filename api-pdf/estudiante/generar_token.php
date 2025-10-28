<?php
/**
 * estudiante/generar_token.php - Genera token de acceso para software desktop
 */

require_once '../config.php';

session_start();
header('Content-Type: application/json');

// Verificar autenticación
if (!isset($_SESSION['rol']) || $_SESSION['rol'] !== 'estudiante') {
    echo json_encode([
        'success' => false,
        'message' => 'No autenticado'
    ]);
    exit;
}

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    echo json_encode([
        'success' => false,
        'message' => 'Método no permitido'
    ]);
    exit;
}

try {
    $rut = $_SESSION['rut'];

    // Generar token simple de 6 caracteres alfanuméricos
    $caracteres = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ';
    $token = '';
    for ($i = 0; $i < 6; $i++) {
        $token .= $caracteres[random_int(0, strlen($caracteres) - 1)];
    }

    // Cargar tokens existentes
    $tokens_file = DATA_PATH . '/tokens.json';
    $tokens = file_exists($tokens_file) ? json_decode(file_get_contents($tokens_file), true) : [];

    // Revocar tokens anteriores del mismo estudiante (opcional)
    $tokens = array_filter($tokens, fn($t) => $t['rut'] !== $rut);

    // Guardar nuevo token
    $tokens[$token] = [
        'rut' => $rut,
        'rol' => 'estudiante',
        'creado' => formatearFecha(),
        'expira' => date('Y-m-d H:i:s', strtotime('+1 year')), // Token válido por 1 año
        'ultimo_uso' => null
    ];

    guardarJSON($tokens_file, $tokens);

    echo json_encode([
        'success' => true,
        'token' => $token,
        'expira' => $tokens[$token]['expira']
    ]);

} catch (Exception $e) {
    echo json_encode([
        'success' => false,
        'message' => 'Error al generar token: ' . $e->getMessage()
    ]);
}
