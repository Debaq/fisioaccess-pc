<?php
/**
 * estudiante/generar_token.php - Genera token de acceso para software desktop
 * Token específico por actividad-estudiante
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
    $actividad_id = $_POST['actividad_id'] ?? null;

    if (!$actividad_id) {
        echo json_encode([
            'success' => false,
            'message' => 'ID de actividad requerido'
        ]);
        exit;
    }

    // Verificar que el estudiante esté inscrito en la actividad
    $actividades = cargarJSON(ACTIVIDADES_FILE);

    if (!isset($actividades[$actividad_id])) {
        echo json_encode([
            'success' => false,
            'message' => 'Actividad no encontrada'
        ]);
        exit;
    }

    if (!in_array($rut, $actividades[$actividad_id]['estudiantes_inscritos'] ?? [])) {
        echo json_encode([
            'success' => false,
            'message' => 'No estás inscrito en esta actividad'
        ]);
        exit;
    }

    // Generar token simple de 6 caracteres alfanuméricos
    $caracteres = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ';
    $token = '';
    for ($i = 0; $i < 6; $i++) {
        $token .= $caracteres[random_int(0, strlen($caracteres) - 1)];
    }

    // Cargar tokens existentes
    $tokens_file = DATA_PATH . '/tokens.json';
    $tokens = file_exists($tokens_file) ? json_decode(file_get_contents($tokens_file), true) : [];

    // Revocar tokens anteriores de este estudiante para esta actividad específica
    $tokens = array_filter($tokens, function($t) use ($rut, $actividad_id) {
        return !($t['rut'] === $rut && $t['actividad_id'] === $actividad_id);
    });

    // Guardar nuevo token
    $tokens[$token] = [
        'token' => $token,
        'rut' => $rut,
        'actividad_id' => $actividad_id,
        'rol' => 'estudiante',
        'creado' => formatearFecha(),
        'expira' => date('Y-m-d H:i:s', strtotime('+1 year')),
        'ultimo_uso' => null
    ];

    guardarJSON($tokens_file, $tokens);

    echo json_encode([
        'success' => true,
        'token' => $token,
        'actividad_id' => $actividad_id,
        'actividad_nombre' => $actividades[$actividad_id]['info_basica']['nombre'],
        'expira' => $tokens[$token]['expira']
    ]);

} catch (Exception $e) {
    echo json_encode([
        'success' => false,
        'message' => 'Error al generar token: ' . $e->getMessage()
    ]);
}
