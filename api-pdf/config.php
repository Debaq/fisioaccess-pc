<?php
/**
 * config.php - Configuración global del sistema
 */

// Zona horaria
date_default_timezone_set('America/Santiago');

// Rutas
define('BASE_PATH', __DIR__);
define('DATA_PATH', BASE_PATH . '/data');
define('UPLOADS_PATH', DATA_PATH . '/uploads');

// Archivos de datos
define('CONFIG_FILE', DATA_PATH . '/config.json');
define('ADMINS_FILE', DATA_PATH . '/admins.json');
define('PROFESORES_FILE', DATA_PATH . '/profesores.json');
define('ESTUDIANTES_FILE', DATA_PATH . '/estudiantes.json');
define('ACTIVIDADES_FILE', DATA_PATH . '/actividades.json');
define('ENTREGAS_FILE', DATA_PATH . '/entregas.json');
define('RESERVAS_FILE', DATA_PATH . '/reservas_ids.json');

// Configuración de sesiones
ini_set('session.cookie_httponly', 1);
ini_set('session.use_only_cookies', 1);
ini_set('session.cookie_secure', 0); // Cambiar a 1 si usas HTTPS

// Timeout de sesión (2 horas)
define('SESSION_TIMEOUT', 7200);

// Límites de archivos
define('PDF_MAX_SIZE', 10 * 1024 * 1024); // 10MB
define('RAW_MAX_SIZE', 5 * 1024 * 1024);  // 5MB

// Tipos de estudio
define('TIPOS_ESTUDIO', [
    'espirometria' => 'Espirometría',
    'ecg' => 'Electrocardiograma',
    'emg' => 'Electromiografía',
    'eeg' => 'Electroencefalograma'
]);

// Tipos de sesión
define('TIPOS_SESION', [
    'real' => 'Práctico con equipo real',
    'simulado_con_equipo' => 'Simulación con equipo',
    'simulado_sin_equipo' => 'Simulación virtual'
]);

// Funciones auxiliares
function cargarJSON($archivo) {
    if (!file_exists($archivo)) {
        return [];
    }
    $contenido = file_get_contents($archivo);
    return json_decode($contenido, true) ?: [];
}

function guardarJSON($archivo, $datos) {
    $dir = dirname($archivo);
    if (!is_dir($dir)) {
        mkdir($dir, 0755, true);
    }
    return file_put_contents($archivo, json_encode($datos, JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE));
}

function verificarSesion() {
    if (session_status() === PHP_SESSION_NONE) {
        session_start();
    }
    
    if (!isset($_SESSION['authenticated']) || !$_SESSION['authenticated']) {
        return false;
    }
    
    // Verificar timeout
    if (time() - ($_SESSION['login_time'] ?? 0) > SESSION_TIMEOUT) {
        session_destroy();
        return false;
    }
    
    return true;
}

function verificarRol($rol_requerido) {
    if (!verificarSesion()) {
        return false;
    }
    
    return ($_SESSION['rol'] ?? '') === $rol_requerido;
}

function responderJSON($datos, $codigo = 200) {
    http_response_code($codigo);
    header('Content-Type: application/json; charset=utf-8');
    echo json_encode($datos, JSON_UNESCAPED_UNICODE);
    exit;
}

function generarID($prefijo = 'ID') {
    return strtoupper($prefijo . bin2hex(random_bytes(4)));
}

function formatearFecha($timestamp = null) {
    if ($timestamp === null) {
        $timestamp = time();
    }
    return date('c', is_numeric($timestamp) ? $timestamp : strtotime($timestamp));
}
?>