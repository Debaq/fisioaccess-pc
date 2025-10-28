<?php
/**
 * api/auth.php - API de autenticación
 *
 * Endpoints:
 * POST /api/auth.php?action=login
 * POST /api/auth.php?action=logout
 * GET  /api/auth.php?action=verify
 */

require_once '../config.php';

header('Content-Type: application/json; charset=utf-8');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: POST, GET, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type, Authorization');

// Manejar preflight OPTIONS
if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    http_response_code(200);
    exit;
}

$action = $_GET['action'] ?? $_POST['action'] ?? '';

switch ($action) {
    case 'login':
        handleLogin();
        break;

    case 'logout':
        handleLogout();
        break;

    case 'verify':
        handleVerify();
        break;

    default:
        responderJSON([
            'success' => false,
            'error' => 'Acción no válida'
        ], 400);
}

/**
 * Login de usuario (admin, profesor, estudiante)
 */
function handleLogin() {
    if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
        responderJSON(['error' => 'Método no permitido'], 405);
    }

    $rol = $_POST['rol'] ?? '';
    $username = $_POST['username'] ?? '';
    $rut = $_POST['rut'] ?? '';
    $password = $_POST['password'] ?? '';

    if (empty($rol)) {
        responderJSON([
            'success' => false,
            'error' => 'Se requiere especificar el rol (admin, profesor, estudiante)'
        ], 400);
    }

    // Login según rol
    if ($rol === 'admin') {
        if (empty($username) || empty($password)) {
            responderJSON([
                'success' => false,
                'error' => 'Usuario y contraseña requeridos'
            ], 400);
        }

        $admins = cargarJSON(ADMINS_FILE);

        if (!isset($admins[$username])) {
            responderJSON([
                'success' => false,
                'error' => 'Credenciales incorrectas'
            ], 401);
        }

        $admin = $admins[$username];

        if (!password_verify($password, $admin['password_hash'])) {
            responderJSON([
                'success' => false,
                'error' => 'Credenciales incorrectas'
            ], 401);
        }

        // Actualizar último login
        $admins[$username]['last_login'] = formatearFecha();
        guardarJSON(ADMINS_FILE, $admins);

        // Iniciar sesión
        session_start();
        $_SESSION['authenticated'] = true;
        $_SESSION['rol'] = 'admin';
        $_SESSION['username'] = $username;
        $_SESSION['nombre'] = $admin['nombre'];
        $_SESSION['login_time'] = time();

        responderJSON([
            'success' => true,
            'data' => [
                'rol' => 'admin',
                'username' => $username,
                'nombre' => $admin['nombre']
            ]
        ], 200);
    }

    elseif ($rol === 'profesor') {
        if (empty($rut) || empty($password)) {
            responderJSON([
                'success' => false,
                'error' => 'RUT y contraseña requeridos'
            ], 400);
        }

        $profesores = cargarJSON(PROFESORES_FILE);

        if (!isset($profesores[$rut])) {
            responderJSON([
                'success' => false,
                'error' => 'Credenciales incorrectas'
            ], 401);
        }

        $profesor = $profesores[$rut];

        if (!$profesor['activo']) {
            responderJSON([
                'success' => false,
                'error' => 'Usuario inactivo. Contacte al administrador'
            ], 403);
        }

        if (!password_verify($password, $profesor['password_hash'])) {
            responderJSON([
                'success' => false,
                'error' => 'Credenciales incorrectas'
            ], 401);
        }

        // Actualizar último login
        $profesores[$rut]['last_login'] = formatearFecha();
        guardarJSON(PROFESORES_FILE, $profesores);

        // Iniciar sesión
        session_start();
        $_SESSION['authenticated'] = true;
        $_SESSION['rol'] = 'profesor';
        $_SESSION['rut'] = $rut;
        $_SESSION['nombre'] = $profesor['nombre'];
        $_SESSION['login_time'] = time();

        responderJSON([
            'success' => true,
            'data' => [
                'rol' => 'profesor',
                'rut' => $rut,
                'nombre' => $profesor['nombre'],
                'email' => $profesor['email']
            ]
        ], 200);
    }

    elseif ($rol === 'estudiante') {
        if (empty($rut)) {
            responderJSON([
                'success' => false,
                'error' => 'RUT requerido'
            ], 400);
        }

        $estudiantes = cargarJSON(ESTUDIANTES_FILE);

        if (!isset($estudiantes[$rut])) {
            responderJSON([
                'success' => false,
                'error' => 'Estudiante no registrado'
            ], 401);
        }

        $estudiante = $estudiantes[$rut];

        if (!$estudiante['activo']) {
            responderJSON([
                'success' => false,
                'error' => 'Usuario inactivo. Contacte a su profesor'
            ], 403);
        }

        // Iniciar sesión
        session_start();
        $_SESSION['authenticated'] = true;
        $_SESSION['rol'] = 'estudiante';
        $_SESSION['rut'] = $rut;
        $_SESSION['nombre'] = $estudiante['nombre'];
        $_SESSION['login_time'] = time();

        responderJSON([
            'success' => true,
            'data' => [
                'rol' => 'estudiante',
                'rut' => $rut,
                'nombre' => $estudiante['nombre'],
                'email' => $estudiante['email'],
                'actividades' => $estudiante['actividades']
            ]
        ], 200);
    }

    else {
        responderJSON([
            'success' => false,
            'error' => 'Rol no válido'
        ], 400);
    }
}

/**
 * Logout
 */
function handleLogout() {
    session_start();
    session_destroy();

    // Si es GET (desde navegador), redirigir al index
    if ($_SERVER['REQUEST_METHOD'] === 'GET') {
        header('Location: ../index.html');
        exit;
    }

    // Si es POST (desde API), responder JSON
    responderJSON([
        'success' => true,
        'message' => 'Sesión cerrada exitosamente'
    ], 200);
}

/**
 * Verificar sesión activa
 */
function handleVerify() {
    session_start();

    if (!verificarSesion()) {
        responderJSON([
            'success' => false,
            'authenticated' => false
        ], 401);
    }

    responderJSON([
        'success' => true,
        'authenticated' => true,
        'data' => [
            'rol' => $_SESSION['rol'] ?? null,
            'nombre' => $_SESSION['nombre'] ?? null,
            'rut' => $_SESSION['rut'] ?? null,
            'username' => $_SESSION['username'] ?? null
        ]
    ], 200);
}
