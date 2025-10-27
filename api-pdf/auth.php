<?php
/**
 * auth.php - Sistema de autenticación y manejo de sesiones
 * 
 * Funciones:
 * - login(): Autenticar usuario (profesor o estudiante)
 * - logout(): Cerrar sesión
 * - checkAuth(): Verificar si hay sesión activa
 * - verificarPassword(): Verificar contraseña de actividad
 */

session_start();

header('Content-Type: application/json');

$dataDir = __DIR__ . '/data/';
$usuariosFile = $dataDir . 'usuarios.json';
$profesoresFile = $dataDir . 'profesores.json';
$actividadesFile = $dataDir . 'actividades.json';

// ========== FUNCIONES AUXILIARES ==========

function cargarUsuarios() {
    global $usuariosFile;
    if (!file_exists($usuariosFile)) {
        return [];
    }
    return json_decode(file_get_contents($usuariosFile), true) ?: [];
}

function cargarProfesores() {
    global $profesoresFile;
    if (!file_exists($profesoresFile)) {
        return [];
    }
    return json_decode(file_get_contents($profesoresFile), true) ?: [];
}

function cargarActividades() {
    global $actividadesFile;
    if (!file_exists($actividadesFile)) {
        return [];
    }
    return json_decode(file_get_contents($actividadesFile), true) ?: [];
}

function responderJSON($data, $codigo = 200) {
    http_response_code($codigo);
    echo json_encode($data);
    exit;
}

// ========== DETERMINAR ACCIÓN ==========
$accion = $_GET['action'] ?? $_POST['action'] ?? '';

switch ($accion) {
    case 'login':
        handleLogin();
        break;
    
    case 'logout':
        handleLogout();
        break;
    
    case 'check':
        handleCheck();
        break;
    
    case 'verificar_password':
        handleVerificarPassword();
        break;
    
    default:
        responderJSON(['error' => 'Acción no válida'], 400);
}

// ========== LOGIN ==========
function handleLogin() {
    if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
        responderJSON(['error' => 'Método no permitido'], 405);
    }
    
    $rut = trim($_POST['rut'] ?? '');
    $tipo = trim($_POST['tipo'] ?? 'estudiante'); // 'estudiante' o 'profesor'
    
    if (empty($rut)) {
        responderJSON(['error' => 'RUT requerido'], 400);
    }
    
    // Login como PROFESOR
    if ($tipo === 'profesor') {
        $password = $_POST['password'] ?? '';
        
        if (empty($password)) {
            responderJSON(['error' => 'Contraseña requerida para profesores'], 400);
        }
        
        // Cargar profesores del archivo JSON
        $profesores = cargarProfesores();
        
        if (empty($profesores)) {
            responderJSON(['error' => 'No hay profesores registrados en el sistema'], 500);
        }
        
        // Verificar que el RUT exista en profesores
        if (!isset($profesores[$rut])) {
            responderJSON(['error' => 'RUT no registrado como profesor'], 401);
        }
        
        $profesor = $profesores[$rut];
        
        // Verificar que el profesor esté activo
        if (!$profesor['activo']) {
            responderJSON(['error' => 'Usuario desactivado. Contacte al administrador'], 401);
        }
        
        // Verificar contraseña
        if (!password_verify($password, $profesor['password_hash'])) {
            responderJSON(['error' => 'Contraseña incorrecta'], 401);
        }
        
        // Guardar sesión de profesor
        $_SESSION['authenticated'] = true;
        $_SESSION['rut'] = $rut;
        $_SESSION['tipo'] = 'profesor';
        $_SESSION['nombre'] = $profesor['nombre'];
        $_SESSION['email'] = $profesor['email'];
        $_SESSION['login_time'] = time();
        
        responderJSON([
            'success' => true,
            'tipo' => 'profesor',
            'rut' => $rut,
            'nombre' => $profesor['nombre'],
            'email' => $profesor['email']
        ]);
    }
    
    // Login como ESTUDIANTE
    else {
        $usuarios = cargarUsuarios();
        
        // Verificar si el estudiante existe en el sistema
        if (!isset($usuarios[$rut])) {
            // Crear usuario nuevo automáticamente
            $usuarios[$rut] = [
                'rut' => $rut,
                'nombre' => $_POST['nombre'] ?? 'Estudiante',
                'actividades' => []
            ];
            
            // Guardar usuario
            if (!is_dir(dirname($GLOBALS['usuariosFile']))) {
                mkdir(dirname($GLOBALS['usuariosFile']), 0755, true);
            }
            file_put_contents($GLOBALS['usuariosFile'], json_encode($usuarios, JSON_PRETTY_PRINT));
        }
        
        $usuario = $usuarios[$rut];
        
        // Guardar sesión de estudiante
        $_SESSION['authenticated'] = true;
        $_SESSION['rut'] = $rut;
        $_SESSION['tipo'] = 'estudiante';
        $_SESSION['nombre'] = $usuario['nombre'];
        $_SESSION['actividades'] = $usuario['actividades'];
        $_SESSION['login_time'] = time();
        
        responderJSON([
            'success' => true,
            'tipo' => 'estudiante',
            'rut' => $rut,
            'nombre' => $usuario['nombre'],
            'actividades' => $usuario['actividades']
        ]);
    }
}

// ========== LOGOUT ==========
function handleLogout() {
    session_destroy();
    responderJSON(['success' => true, 'message' => 'Sesión cerrada']);
}

// ========== CHECK AUTH ==========
function handleCheck() {
    if (!isset($_SESSION['authenticated']) || !$_SESSION['authenticated']) {
        responderJSON(['authenticated' => false], 401);
    }
    
    // Verificar timeout de sesión (2 horas)
    $timeout = 7200; // 2 horas en segundos
    if (time() - $_SESSION['login_time'] > $timeout) {
        session_destroy();
        responderJSON(['authenticated' => false, 'message' => 'Sesión expirada'], 401);
    }
    
    responderJSON([
        'authenticated' => true,
        'tipo' => $_SESSION['tipo'],
        'rut' => $_SESSION['rut'],
        'nombre' => $_SESSION['nombre']
    ]);
}

// ========== VERIFICAR PASSWORD DE ACTIVIDAD ==========
function handleVerificarPassword() {
    if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
        responderJSON(['error' => 'Método no permitido'], 405);
    }
    
    $actividadId = trim($_POST['actividad_id'] ?? '');
    $password = $_POST['password'] ?? '';
    
    if (empty($actividadId) || empty($password)) {
        responderJSON(['error' => 'Faltan campos requeridos'], 400);
    }
    
    $actividades = cargarActividades();
    
    if (!isset($actividades[$actividadId])) {
        responderJSON(['error' => 'Actividad no encontrada'], 404);
    }
    
    $actividad = $actividades[$actividadId];
    
    // Verificar password
    if (!password_verify($password, $actividad['password_hash'])) {
        responderJSON(['error' => 'Contraseña incorrecta'], 401);
    }
    
    // Guardar en sesión que tiene acceso a esta actividad
    if (!isset($_SESSION['actividades_acceso'])) {
        $_SESSION['actividades_acceso'] = [];
    }
    $_SESSION['actividades_acceso'][] = $actividadId;
    
    responderJSON([
        'success' => true,
        'actividad_id' => $actividadId,
        'message' => 'Acceso concedido'
    ]);
}