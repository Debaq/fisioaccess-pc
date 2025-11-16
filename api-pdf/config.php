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

// Archivos de seguridad y logging
define('RATE_LIMIT_FILE', DATA_PATH . '/rate_limits.json');
define('LOG_FILE', DATA_PATH . '/logs/app.log');
define('SECURITY_LOG_FILE', DATA_PATH . '/logs/security.log');

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

// Configuración de rate limiting
define('RATE_LIMIT_WINDOW', 3600); // Ventana de 1 hora
define('RATE_LIMIT_MAX_ATTEMPTS_IP', 10); // Máximo 10 intentos por IP por hora
define('RATE_LIMIT_MAX_ATTEMPTS_EMAIL', 5); // Máximo 5 intentos por email por hora
define('RATE_LIMIT_LOGIN_ATTEMPTS', 5); // Máximo 5 intentos de login fallidos

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

    // Usar file locking para prevenir race conditions
    $json = json_encode($datos, JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE);
    $fp = fopen($archivo, 'c');

    if ($fp) {
        if (flock($fp, LOCK_EX)) {
            ftruncate($fp, 0);
            fwrite($fp, $json);
            fflush($fp);
            flock($fp, LOCK_UN);
            fclose($fp);
            return true;
        } else {
            fclose($fp);
            registrarLog('ERROR', "No se pudo obtener lock para: $archivo");
            return false;
        }
    }

    registrarLog('ERROR', "No se pudo abrir archivo: $archivo");
    return false;
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

// ============================================================================
// SISTEMA DE LOGGING
// ============================================================================

/**
 * Registrar evento en log
 * @param string $nivel Nivel: INFO, WARNING, ERROR, SECURITY
 * @param string $mensaje Mensaje a registrar
 * @param array $contexto Contexto adicional (opcional)
 */
function registrarLog($nivel, $mensaje, $contexto = []) {
    $archivo_log = ($nivel === 'SECURITY') ? SECURITY_LOG_FILE : LOG_FILE;

    $dir = dirname($archivo_log);
    if (!is_dir($dir)) {
        mkdir($dir, 0755, true);
    }

    $timestamp = date('Y-m-d H:i:s');
    $ip = $_SERVER['REMOTE_ADDR'] ?? 'unknown';
    $user_agent = $_SERVER['HTTP_USER_AGENT'] ?? 'unknown';
    $uri = $_SERVER['REQUEST_URI'] ?? '';

    $contexto_json = !empty($contexto) ? json_encode($contexto, JSON_UNESCAPED_UNICODE) : '';

    $linea = sprintf(
        "[%s] [%s] [IP: %s] %s %s %s\n",
        $timestamp,
        $nivel,
        $ip,
        $mensaje,
        $uri,
        $contexto_json
    );

    // Escribir en archivo con lock
    $fp = fopen($archivo_log, 'a');
    if ($fp) {
        if (flock($fp, LOCK_EX)) {
            fwrite($fp, $linea);
            flock($fp, LOCK_UN);
        }
        fclose($fp);
    }

    // También registrar en error_log de PHP para errores críticos
    if (in_array($nivel, ['ERROR', 'SECURITY'])) {
        error_log($mensaje);
    }
}

/**
 * Registrar evento de seguridad
 */
function registrarEventoSeguridad($evento, $detalles = []) {
    registrarLog('SECURITY', $evento, $detalles);
}

// ============================================================================
// RATE LIMITING
// ============================================================================

/**
 * Verificar rate limit por clave (IP, email, etc.)
 * @param string $tipo Tipo de limite: 'ip', 'email', 'login'
 * @param string $clave Identificador (IP, email, username)
 * @param int $max_intentos Máximo de intentos permitidos
 * @return bool true si está dentro del límite, false si excedió
 */
function verificarRateLimit($tipo, $clave, $max_intentos = null) {
    // Determinar máximo según tipo
    if ($max_intentos === null) {
        switch ($tipo) {
            case 'ip':
                $max_intentos = RATE_LIMIT_MAX_ATTEMPTS_IP;
                break;
            case 'email':
                $max_intentos = RATE_LIMIT_MAX_ATTEMPTS_EMAIL;
                break;
            case 'login':
                $max_intentos = RATE_LIMIT_LOGIN_ATTEMPTS;
                break;
            default:
                $max_intentos = 10;
        }
    }

    $rate_limits = cargarJSON(RATE_LIMIT_FILE);
    $tiempo_actual = time();
    $key = $tipo . ':' . $clave;

    // Limpiar entradas expiradas
    foreach ($rate_limits as $k => $data) {
        if ($tiempo_actual - $data['first_attempt'] > RATE_LIMIT_WINDOW) {
            unset($rate_limits[$k]);
        }
    }

    // Verificar si existe y si está bloqueado
    if (isset($rate_limits[$key])) {
        $data = $rate_limits[$key];

        // Si está fuera de la ventana, resetear
        if ($tiempo_actual - $data['first_attempt'] > RATE_LIMIT_WINDOW) {
            unset($rate_limits[$key]);
            guardarJSON(RATE_LIMIT_FILE, $rate_limits);
            return true;
        }

        // Verificar si excedió el límite
        if ($data['attempts'] >= $max_intentos) {
            $tiempo_restante = RATE_LIMIT_WINDOW - ($tiempo_actual - $data['first_attempt']);
            registrarEventoSeguridad("Rate limit excedido: $tipo - $clave", [
                'attempts' => $data['attempts'],
                'tiempo_restante' => $tiempo_restante
            ]);
            return false;
        }
    }

    return true;
}

/**
 * Registrar intento (incrementar contador de rate limit)
 */
function registrarIntento($tipo, $clave, $exitoso = false) {
    $rate_limits = cargarJSON(RATE_LIMIT_FILE);
    $tiempo_actual = time();
    $key = $tipo . ':' . $clave;

    if (!isset($rate_limits[$key])) {
        $rate_limits[$key] = [
            'first_attempt' => $tiempo_actual,
            'attempts' => 1,
            'last_attempt' => $tiempo_actual,
            'exitoso' => $exitoso
        ];
    } else {
        // Si la ventana expiró, resetear
        if ($tiempo_actual - $rate_limits[$key]['first_attempt'] > RATE_LIMIT_WINDOW) {
            $rate_limits[$key] = [
                'first_attempt' => $tiempo_actual,
                'attempts' => 1,
                'last_attempt' => $tiempo_actual,
                'exitoso' => $exitoso
            ];
        } else {
            // Incrementar
            $rate_limits[$key]['attempts']++;
            $rate_limits[$key]['last_attempt'] = $tiempo_actual;
            $rate_limits[$key]['exitoso'] = $exitoso;
        }
    }

    // Si fue exitoso, resetear contador (solo para login)
    if ($exitoso && $tipo === 'login') {
        unset($rate_limits[$key]);
    }

    guardarJSON(RATE_LIMIT_FILE, $rate_limits);
}

/**
 * Limpiar rate limits expirados
 */
function limpiarRateLimits() {
    $rate_limits = cargarJSON(RATE_LIMIT_FILE);
    $tiempo_actual = time();
    $limpios = [];

    foreach ($rate_limits as $key => $data) {
        if ($tiempo_actual - $data['first_attempt'] <= RATE_LIMIT_WINDOW) {
            $limpios[$key] = $data;
        }
    }

    if (count($limpios) !== count($rate_limits)) {
        guardarJSON(RATE_LIMIT_FILE, $limpios);
    }
}

// ============================================================================
// VALIDACIONES CENTRALIZADAS
// ============================================================================

/**
 * Validar RUT chileno
 */
function validarRUT($rut) {
    // Limpiar RUT
    $rut = preg_replace('/[^0-9kK]/', '', strtoupper($rut));

    if (strlen($rut) < 2) {
        return false;
    }

    $dv = substr($rut, -1);
    $numero = substr($rut, 0, -1);

    // Calcular dígito verificador
    $suma = 0;
    $multiplo = 2;

    for ($i = strlen($numero) - 1; $i >= 0; $i--) {
        $suma += $numero[$i] * $multiplo;
        $multiplo = ($multiplo < 7) ? $multiplo + 1 : 2;
    }

    $resto = $suma % 11;
    $dv_calculado = 11 - $resto;

    if ($dv_calculado == 11) $dv_calculado = '0';
    if ($dv_calculado == 10) $dv_calculado = 'K';

    return (string)$dv_calculado === (string)$dv;
}

/**
 * Validar email con opciones adicionales
 */
function validarEmail($email, $opciones = []) {
    // Validación básica
    if (!filter_var($email, FILTER_VALIDATE_EMAIL)) {
        return [
            'valido' => false,
            'error' => 'Formato de email inválido'
        ];
    }

    // Validar dominio si se especifica
    if (isset($opciones['dominio_requerido'])) {
        $dominio = substr(strrchr($email, "@"), 1);
        if (strtolower($dominio) !== strtolower($opciones['dominio_requerido'])) {
            return [
                'valido' => false,
                'error' => 'El email debe ser del dominio ' . $opciones['dominio_requerido']
            ];
        }
    }

    // Validar que no esté en lista negra (opcional)
    if (isset($opciones['blacklist']) && in_array(strtolower($email), $opciones['blacklist'])) {
        return [
            'valido' => false,
            'error' => 'Email no permitido'
        ];
    }

    return [
        'valido' => true,
        'email' => strtolower($email)
    ];
}

/**
 * Sanitizar string para prevenir XSS
 */
function sanitizarString($string, $opciones = []) {
    // Opciones por defecto
    $defaults = [
        'trim' => true,
        'strip_tags' => true,
        'htmlspecialchars' => false,
        'max_length' => null
    ];

    $opts = array_merge($defaults, $opciones);

    if ($opts['trim']) {
        $string = trim($string);
    }

    if ($opts['strip_tags']) {
        $string = strip_tags($string);
    }

    if ($opts['htmlspecialchars']) {
        $string = htmlspecialchars($string, ENT_QUOTES, 'UTF-8');
    }

    if ($opts['max_length'] !== null && strlen($string) > $opts['max_length']) {
        $string = substr($string, 0, $opts['max_length']);
    }

    return $string;
}

/**
 * Validar que un string no esté vacío
 */
function validarNoVacio($valor, $nombre_campo = 'Campo') {
    if (empty(trim($valor))) {
        return [
            'valido' => false,
            'error' => "$nombre_campo es requerido"
        ];
    }

    return ['valido' => true, 'valor' => trim($valor)];
}

/**
 * Validar longitud de string
 */
function validarLongitud($string, $min = null, $max = null, $nombre_campo = 'Campo') {
    $longitud = strlen($string);

    if ($min !== null && $longitud < $min) {
        return [
            'valido' => false,
            'error' => "$nombre_campo debe tener al menos $min caracteres"
        ];
    }

    if ($max !== null && $longitud > $max) {
        return [
            'valido' => false,
            'error' => "$nombre_campo no puede exceder $max caracteres"
        ];
    }

    return ['valido' => true];
}

/**
 * Obtener IP del cliente (considerando proxies)
 */
function obtenerIP() {
    if (!empty($_SERVER['HTTP_CLIENT_IP'])) {
        $ip = $_SERVER['HTTP_CLIENT_IP'];
    } elseif (!empty($_SERVER['HTTP_X_FORWARDED_FOR'])) {
        $ip = explode(',', $_SERVER['HTTP_X_FORWARDED_FOR'])[0];
    } else {
        $ip = $_SERVER['REMOTE_ADDR'] ?? '0.0.0.0';
    }

    return filter_var($ip, FILTER_VALIDATE_IP) ? $ip : '0.0.0.0';
}
?>
