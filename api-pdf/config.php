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

// Cargar variables de entorno desde .env
function cargarEnv($archivo = null) {
    if ($archivo === null) {
        $archivo = BASE_PATH . '/.env';
    }

    if (!file_exists($archivo)) {
        return;
    }

    $lineas = file($archivo, FILE_IGNORE_NEW_LINES | FILE_SKIP_EMPTY_LINES);
    foreach ($lineas as $linea) {
        // Ignorar comentarios
        if (strpos(trim($linea), '#') === 0) {
            continue;
        }

        // Parsear línea
        if (strpos($linea, '=') !== false) {
            list($nombre, $valor) = explode('=', $linea, 2);
            $nombre = trim($nombre);
            $valor = trim($valor);

            // Establecer variable de entorno si no existe
            if (!getenv($nombre)) {
                putenv("$nombre=$valor");
                $_ENV[$nombre] = $valor;
            }
        }
    }
}

// Función auxiliar para obtener variable de entorno con fallback
function env($nombre, $default = null) {
    $valor = getenv($nombre);
    if ($valor === false) {
        return $default;
    }

    // Convertir strings especiales
    $lower = strtolower($valor);
    if ($lower === 'true') return true;
    if ($lower === 'false') return false;
    if ($lower === 'null') return null;

    return $valor;
}

// Cargar .env
cargarEnv();

// ⬇️ Cargar PHPMailer si está disponible (DESPUÉS de BASE_PATH)
// Si PHPMailer no está instalado, se usará mail() nativo de PHP
if (file_exists(BASE_PATH . '/lib/PHPMailer/src/PHPMailer.php')) {
    require_once BASE_PATH . '/lib/PHPMailer/src/Exception.php';
    require_once BASE_PATH . '/lib/PHPMailer/src/PHPMailer.php';
    require_once BASE_PATH . '/lib/PHPMailer/src/SMTP.php';
}

// Archivos de datos
define('CONFIG_FILE', DATA_PATH . '/config.json');
define('ADMINS_FILE', DATA_PATH . '/admins.json');
define('PROFESORES_FILE', DATA_PATH . '/profesores.json');
define('ESTUDIANTES_FILE', DATA_PATH . '/estudiantes.json');
define('ACTIVIDADES_FILE', DATA_PATH . '/actividades.json');
define('ENTREGAS_FILE', DATA_PATH . '/entregas.json');
define('RESERVAS_FILE', DATA_PATH . '/reservas_ids.json');

// Nuevos archivos para accesos estudiantes
define('SESIONES_ESTUDIANTES_FILE', DATA_PATH . '/sesiones_estudiantes.json');
define('TOKENS_APP_FILE', DATA_PATH . '/tokens_app.json');
define('CODIGOS_VERIFICACION_FILE', DATA_PATH . '/codigos_verificacion.json');

// Configuración de sesiones
ini_set('session.cookie_httponly', 1);
ini_set('session.use_only_cookies', 1);
ini_set('session.cookie_secure', 0); // Cambiar a 1 si usas HTTPS
ini_set('session.cookie_samesite', 'Strict'); // Protección CSRF

// Timeout de sesión (2 horas)
define('SESSION_TIMEOUT', 7200);

// Timeout de token de app (4 horas)
define('TOKEN_APP_TIMEOUT', 14400);

// Timeout de código de verificación (20 minutos)
define('CODIGO_VERIFICACION_TIMEOUT', 1200);

// Límites de archivos
define('PDF_MAX_SIZE', 10 * 1024 * 1024); // 10MB
define('RAW_MAX_SIZE', 5 * 1024 * 1024);  // 5MB


// Configuración de email (desde .env)
define('SMTP_HOST', env('SMTP_HOST', 'mail.tmeduca.org'));
define('SMTP_PORT', env('SMTP_PORT', 465));  // SSL
define('SMTP_FROM', env('SMTP_FROM', 'fisioaccess@tmeduca.org'));
define('SMTP_FROM_NAME', env('SMTP_FROM_NAME', 'FisioaccessPC'));
define('SMTP_USER', env('SMTP_USER', 'fisioaccess@tmeduca.org'));
define('SMTP_PASS', env('SMTP_PASS', ''));  // ⚠️ Nunca hardcodear contraseñas

// Configuración de seguridad CORS
define('ALLOWED_ORIGINS', array_filter(array_map('trim', explode(',', env('ALLOWED_ORIGINS', '*')))));
define('DEBUG_MODE', env('DEBUG_MODE', false));

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

/**
 * Validar y establecer headers CORS de forma segura
 */
function configurarCORS() {
    $origin = $_SERVER['HTTP_ORIGIN'] ?? '';

    // Si ALLOWED_ORIGINS contiene '*', permitir todos
    if (in_array('*', ALLOWED_ORIGINS)) {
        header('Access-Control-Allow-Origin: *');
    } elseif (in_array($origin, ALLOWED_ORIGINS)) {
        header("Access-Control-Allow-Origin: $origin");
        header('Vary: Origin');
    }

    header('Access-Control-Allow-Methods: POST, GET, OPTIONS');
    header('Access-Control-Allow-Headers: Content-Type, X-CSRF-Token');
    header('Access-Control-Allow-Credentials: true');
}

/**
 * Generar token CSRF
 */
function generarTokenCSRF() {
    if (session_status() === PHP_SESSION_NONE) {
        session_start();
    }

    if (!isset($_SESSION['csrf_token'])) {
        $_SESSION['csrf_token'] = bin2hex(random_bytes(32));
    }

    return $_SESSION['csrf_token'];
}

/**
 * Validar token CSRF
 */
function validarTokenCSRF($token) {
    if (session_status() === PHP_SESSION_NONE) {
        session_start();
    }

    if (!isset($_SESSION['csrf_token'])) {
        return false;
    }

    return hash_equals($_SESSION['csrf_token'], $token);
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

    // Si hay error y DEBUG_MODE está desactivado, sanitizar mensaje
    if (!DEBUG_MODE && isset($datos['error']) && $codigo >= 500) {
        $datos['error'] = 'Error interno del servidor. Contacte al administrador.';
        // Log del error real en servidor
        if (isset($datos['error_detail'])) {
            error_log("ERROR: " . $datos['error_detail']);
            unset($datos['error_detail']);
        }
    }

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

/**
 * Generar token aleatorio para actividad o app
 */
function generarToken($longitud = 16) {
    $caracteres = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ';
    $token = '';
    $max = strlen($caracteres) - 1;
    
    for ($i = 0; $i < $longitud; $i++) {
        $token .= $caracteres[random_int(0, $max)];
    }
    
    // Formatear con guiones para legibilidad (ej: ABCD-1234-WXYZ)
    if ($longitud >= 12) {
        $token = substr($token, 0, 4) . '-' . substr($token, 4, 4) . '-' . substr($token, 8);
    }
    
    return $token;
}

/**
 * Generar código numérico de verificación
 */
function generarCodigoVerificacion() {
    return str_pad(random_int(0, 999999), 6, '0', STR_PAD_LEFT);
}

/**
 * Enviar email simple (usando mail() de PHP)
 * Nota: Para producción se recomienda usar PHPMailer o similar
 */
/**
 * Enviar email usando PHPMailer
 */
function enviarEmail($destinatario, $asunto, $mensaje) {
    // Si PHPMailer no está disponible, usar mail() básico
    if (!class_exists('PHPMailer\PHPMailer\PHPMailer')) {
        $headers = [
            'From: ' . SMTP_FROM_NAME . ' <' . SMTP_FROM . '>',
            'Reply-To: ' . SMTP_FROM,
            'X-Mailer: PHP/' . phpversion(),
            'MIME-Version: 1.0',
            'Content-Type: text/html; charset=UTF-8'
        ];

        $headers_string = implode("\r\n", $headers);
        return mail($destinatario, $asunto, $mensaje, $headers_string);
    }

    // Usar PHPMailer si está disponible
    try {
        $mail = new PHPMailer\PHPMailer\PHPMailer(true);

        // Configuración del servidor
        $mail->isSMTP();
        $mail->Host = SMTP_HOST;
        $mail->SMTPAuth = true;
        $mail->Username = SMTP_USER;
        $mail->Password = SMTP_PASS;
        $mail->SMTPSecure = PHPMailer\PHPMailer\PHPMailer::ENCRYPTION_SMTPS; // SSL
        $mail->Port = SMTP_PORT;
        $mail->CharSet = 'UTF-8';

        // Remitente y destinatario
        $mail->setFrom(SMTP_FROM, SMTP_FROM_NAME);
        $mail->addAddress($destinatario);

        // Contenido
        $mail->isHTML(true);
        $mail->Subject = $asunto;
        $mail->Body = $mensaje;

        $mail->send();
        return true;
    } catch (Exception $e) {
        error_log("Error enviando email: {$mail->ErrorInfo}");
        return false;
    }
}

/**
 * Validar formato de email institucional
 */
function validarEmailInstitucional($email, $dominio_requerido = null) {
    // Validar formato básico
    if (!filter_var($email, FILTER_VALIDATE_EMAIL)) {
        return false;
    }
    
    // Si se especifica dominio, validar
    if ($dominio_requerido) {
        $dominio = substr(strrchr($email, "@"), 1);
        return strtolower($dominio) === strtolower($dominio_requerido);
    }
    
    return true;
}

/**
 * Limpiar códigos de verificación expirados
 */
function limpiarCodigosExpirados() {
    $codigos = cargarJSON(CODIGOS_VERIFICACION_FILE);
    $tiempo_actual = time();
    $codigos_validos = [];
    
    foreach ($codigos as $email => $data) {
        if ($tiempo_actual - $data['timestamp'] < CODIGO_VERIFICACION_TIMEOUT) {
            $codigos_validos[$email] = $data;
        }
    }
    
    if (count($codigos_validos) !== count($codigos)) {
        guardarJSON(CODIGOS_VERIFICACION_FILE, $codigos_validos);
    }
    
    return $codigos_validos;
}

/**
 * Limpiar tokens de app expirados
 */
function limpiarTokensExpirados() {
    $tokens = cargarJSON(TOKENS_APP_FILE);
    $tiempo_actual = time();
    $tokens_validos = [];
    
    foreach ($tokens as $token => $data) {
        if ($tiempo_actual - $data['timestamp'] < TOKEN_APP_TIMEOUT) {
            $tokens_validos[$token] = $data;
        }
    }
    
    if (count($tokens_validos) !== count($tokens)) {
        guardarJSON(TOKENS_APP_FILE, $tokens_validos);
    }
    
    return $tokens_validos;
}
?>
