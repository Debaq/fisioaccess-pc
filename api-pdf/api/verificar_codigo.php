<?php
/**
 * api/verificar_codigo.php - Verificar código y crear sesión automática
 *
 * POST /api/verificar_codigo.php
 * Body: {
 *   "email": "estudiante@uach.cl",
 *   "codigo": "123456"
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
    $email = strtolower(trim($input['email'] ?? ''));
    $codigo = trim($input['codigo'] ?? '');

    if (empty($email) || empty($codigo)) {
        responderJSON([
            'success' => false,
            'error' => 'Email y código son requeridos'
        ], 400);
    }

    // Limpiar códigos expirados
    limpiarCodigosExpirados();

    // Verificar código
    $codigos = cargarJSON(CODIGOS_VERIFICACION_FILE);

    if (!isset($codigos[$email])) {
        responderJSON([
            'success' => false,
            'error' => 'Código no encontrado o expirado'
        ], 404);
    }

    $datos_codigo = $codigos[$email];

    // Verificar intentos
    if ($datos_codigo['intentos'] >= 5) {
        // Eliminar código
        unset($codigos[$email]);
        guardarJSON(CODIGOS_VERIFICACION_FILE, $codigos);

        responderJSON([
            'success' => false,
            'error' => 'Demasiados intentos fallidos. Solicita un nuevo código.'
        ], 403);
    }

    // Verificar código
    if ($datos_codigo['codigo'] !== $codigo) {
        // Incrementar intentos
        $codigos[$email]['intentos']++;
        guardarJSON(CODIGOS_VERIFICACION_FILE, $codigos);

        $intentos_restantes = 5 - $codigos[$email]['intentos'];

        responderJSON([
            'success' => false,
            'error' => 'Código incorrecto. Intentos restantes: ' . $intentos_restantes
        ], 400);
    }

    // Código válido - eliminar de la lista
    $actividad_id = $datos_codigo['actividad_id'];
    $token_actividad = $datos_codigo['token_actividad'];

    unset($codigos[$email]);
    guardarJSON(CODIGOS_VERIFICACION_FILE, $codigos);

    // Buscar estudiante por email
    $estudiantes = cargarJSON(ESTUDIANTES_FILE);
    $estudiante = null;
    $rut_estudiante = null;

    foreach ($estudiantes as $rut => $est) {
        if (strtolower($est['email']) === $email) {
            $estudiante = $est;
            $rut_estudiante = $rut;
            break;
        }
    }

    // Si no existe el estudiante, crearlo automáticamente
    if (!$estudiante) {
        // Generar student_id determinístico basado en email (NO RUT falso)
        // Esto permite identificar al estudiante de forma única y consistente
        $rut_estudiante = 'STU-' . strtoupper(substr(hash('sha256', $email), 0, 10));
        $nombre = explode('@', $email)[0];

        $estudiante = [
            'rut' => $rut_estudiante,  // Ahora es un student_id, no un RUT chileno
            'nombre' => ucfirst($nombre),
            'email' => $email,
            'activo' => true,
            'created' => formatearFecha(),
            'actividades' => [$actividad_id],
            'rut_real' => null  // El estudiante puede proveerlo más adelante si es necesario
        ];

        $estudiantes[$rut_estudiante] = $estudiante;
        guardarJSON(ESTUDIANTES_FILE, $estudiantes);
    } else {
        // Si ya existe, agregar la actividad si no está
        if (!in_array($actividad_id, $estudiante['actividades'] ?? [])) {
            $estudiantes[$rut_estudiante]['actividades'][] = $actividad_id;
            guardarJSON(ESTUDIANTES_FILE, $estudiantes);
        }
    }

    // INSCRIBIR AL ESTUDIANTE EN LA ACTIVIDAD
    $actividades = cargarJSON(ACTIVIDADES_FILE);
    if (!in_array($rut_estudiante, $actividades[$actividad_id]['estudiantes_inscritos'] ?? [])) {
        if (!isset($actividades[$actividad_id]['estudiantes_inscritos'])) {
            $actividades[$actividad_id]['estudiantes_inscritos'] = [];
        }
        $actividades[$actividad_id]['estudiantes_inscritos'][] = $rut_estudiante;
        guardarJSON(ACTIVIDADES_FILE, $actividades);
    }

    // CREAR SESIÓN PHP AUTOMÁTICA y regenerar ID por seguridad
    session_start();
    session_regenerate_id(true);
    $_SESSION['authenticated'] = true;
    $_SESSION['rol'] = 'estudiante';
    $_SESSION['rut'] = $rut_estudiante;
    $_SESSION['email'] = $email;
    $_SESSION['nombre'] = $estudiante['nombre'];
    $_SESSION['login_time'] = time();

    // Registrar acceso exitoso
    registrarEventoSeguridad('Estudiante verificado y autenticado', [
        'email' => $email,
        'rut' => $rut_estudiante,
        'actividad_id' => $actividad_id,
        'ip' => obtenerIP()
    ]);

    // Crear sesión de estudiante para el sistema
    $sesiones = cargarJSON(SESIONES_ESTUDIANTES_FILE);
    $session_id = session_id();

    $sesiones[$session_id] = [
        'session_id' => $session_id,
        'email' => $email,
        'rut' => $rut_estudiante,
        'actividad_id' => $actividad_id,
        'timestamp' => time(),
        'ip' => $_SERVER['REMOTE_ADDR'] ?? 'unknown',
        'user_agent' => $_SERVER['HTTP_USER_AGENT'] ?? 'unknown'
    ];

    guardarJSON(SESIONES_ESTUDIANTES_FILE, $sesiones);

    responderJSON([
        'success' => true,
        'message' => 'Código verificado correctamente',
        'data' => [
            'session_id' => $session_id,
            'email' => $email,
            'rut' => $rut_estudiante,
            'nombre' => $estudiante['nombre'],
            'actividad_id' => $actividad_id,
            'redirect' => '../estudiante/dashboard.php'
        ]
    ], 200);

} catch (Exception $e) {
    responderJSON([
        'success' => false,
        'error' => 'Error del servidor: ' . $e->getMessage()
    ], 500);
}
?>
