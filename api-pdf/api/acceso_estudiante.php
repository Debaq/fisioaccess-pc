<?php
/**
 * api/acceso_estudiante.php - Validar email y enviar código de verificación
 *
 * POST /api/acceso_estudiante.php
 * Body: {
 *   "token_actividad": "ABC123",
 *   "email": "estudiante@uach.cl",
 *   "reenviar": false
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
    $token_actividad = trim($input['token_actividad'] ?? '');
    $email = strtolower(trim($input['email'] ?? ''));
    $reenviar = $input['reenviar'] ?? false;

    if (empty($token_actividad) || empty($email)) {
        responderJSON([
            'success' => false,
            'error' => 'Token de actividad y email son requeridos'
        ], 400);
    }

    // Validar formato de email usando función centralizada
    $validacion_email = validarEmail($email);
    if (!$validacion_email['valido']) {
        responderJSON([
            'success' => false,
            'error' => $validacion_email['error']
        ], 400);
    }
    $email = $validacion_email['email'];

    // RATE LIMITING: Verificar límite por IP y por email
    $ip = obtenerIP();

    if (!verificarRateLimit('ip', $ip)) {
        registrarEventoSeguridad('Rate limit IP excedido en acceso_estudiante', ['ip' => $ip, 'email' => $email]);
        responderJSON([
            'success' => false,
            'error' => 'Demasiados intentos desde tu IP. Intenta nuevamente en 1 hora.'
        ], 429);
    }

    if (!verificarRateLimit('email', $email)) {
        registrarEventoSeguridad('Rate limit email excedido en acceso_estudiante', ['ip' => $ip, 'email' => $email]);
        responderJSON([
            'success' => false,
            'error' => 'Demasiados intentos con este email. Intenta nuevamente en 1 hora.'
        ], 429);
    }

    // Registrar intento
    registrarIntento('ip', $ip);
    registrarIntento('email', $email);

    // Buscar actividad por token
    $actividades = cargarJSON(ACTIVIDADES_FILE);
    $actividad = null;
    $actividad_id = null;

    foreach ($actividades as $id => $act) {
        if (isset($act['accesos']['token_actividad']) &&
            $act['accesos']['token_actividad'] === $token_actividad) {
            $actividad = $act;
        $actividad_id = $id;
        break;
            }
    }

    if (!$actividad) {
        responderJSON([
            'success' => false,
            'error' => 'Actividad no encontrada'
        ], 404);
    }

    // Verificar que la actividad esté abierta
    $ahora = time();
    $fecha_inicio = strtotime($actividad['info_basica']['fecha_inicio']);
    $fecha_cierre = strtotime($actividad['info_basica']['fecha_cierre']);

    if ($ahora < $fecha_inicio) {
        responderJSON([
            'success' => false,
            'error' => 'La actividad aún no ha comenzado'
        ], 403);
    }

    if ($ahora > $fecha_cierre) {
        responderJSON([
            'success' => false,
            'error' => 'La actividad ha finalizado'
        ], 403);
    }

    // Validar acceso según el modo de registro configurado
    $modo_registro = $actividad['accesos']['modo_registro'] ?? 'abierto';

    switch ($modo_registro) {
        case 'dominio':
            // Validar que el email sea del dominio institucional
            $dominio_requerido = $actividad['accesos']['dominio_email'] ?? '@uach.cl';
            $dominio_usuario = substr(strrchr($email, "@"), 0); // Incluye el @

            if (strtolower($dominio_usuario) !== strtolower($dominio_requerido)) {
                responderJSON([
                    'success' => false,
                    'error' => 'El email debe ser del dominio ' . $dominio_requerido . '. Contacta a tu profesor si necesitas acceso.'
                ], 403);
            }
            break;

        case 'lista_blanca':
            // Validar que el email esté en la lista autorizada
            $emails_autorizados = $actividad['accesos']['emails_autorizados'] ?? [];

            if (empty($emails_autorizados)) {
                responderJSON([
                    'success' => false,
                    'error' => 'Esta actividad requiere lista de estudiantes autorizados pero no está configurada. Contacta a tu profesor.'
                ], 403);
            }

            if (!in_array($email, $emails_autorizados)) {
                responderJSON([
                    'success' => false,
                    'error' => 'No estás autorizado para esta actividad. Contacta a tu profesor para solicitar acceso.'
                ], 403);
            }
            break;

        case 'abierto':
        default:
            // Cualquier email válido es aceptado (ya fue validado arriba)
            break;
    }

    // Limpiar códigos expirados
    limpiarCodigosExpirados();

    // Verificar si ya existe un código reciente (para evitar spam)
    $codigos = cargarJSON(CODIGOS_VERIFICACION_FILE);

    if (isset($codigos[$email]) && !$reenviar) {
        $tiempo_transcurrido = time() - $codigos[$email]['timestamp'];

        // Si han pasado menos de 60 segundos, no enviar otro
        if ($tiempo_transcurrido < 60) {
            responderJSON([
                'success' => false,
                'error' => 'Ya se envió un código recientemente. Espera ' . (60 - $tiempo_transcurrido) . ' segundos.'
            ], 429);
        }
    }

    // Generar código de verificación
    $codigo = generarCodigoVerificacion();

    // Guardar código
    $codigos[$email] = [
        'codigo' => $codigo,
        'token_actividad' => $token_actividad,
        'actividad_id' => $actividad_id,
        'timestamp' => time(),
        'intentos' => 0
    ];

    guardarJSON(CODIGOS_VERIFICACION_FILE, $codigos);

    // Enviar email
    $asunto = 'Código de verificación - ' . $actividad['info_basica']['nombre'];

    $mensaje = '
    <html>
    <head>
    <style>
    body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
    .container { max-width: 600px; margin: 0 auto; padding: 20px; }
    .header { background: linear-gradient(135deg, #7c3aed 0%, #a855f7 100%); color: white; padding: 20px; border-radius: 8px 8px 0 0; }
    .content { background: #f9fafb; padding: 30px; border-radius: 0 0 8px 8px; }
    .code { font-size: 32px; font-weight: bold; color: #7c3aed; letter-spacing: 8px; text-align: center; padding: 20px; background: white; border-radius: 8px; margin: 20px 0; }
    .footer { text-align: center; margin-top: 20px; font-size: 12px; color: #6b7280; }
    </style>
    </head>
    <body>
    <div class="container">
    <div class="header">
    <h2 style="margin: 0;">🫁 FisioaccessPC</h2>
    </div>
    <div class="content">
    <h3>Código de verificación</h3>
    <p>Has solicitado acceso a la actividad:</p>
    <p><strong>' . htmlspecialchars($actividad['info_basica']['nombre']) . '</strong></p>

    <p>Tu código de verificación es:</p>
    <div class="code">' . $codigo . '</div>

    <p><strong>⏱️ Este código expira en 20 minutos.</strong></p>

    <p style="font-size: 14px; color: #6b7280;">
    Si el correo llegó a spam, marca este remitente como seguro para recibir futuros correos.
    </p>

    <div class="footer">
    <p>FisioaccessPC - Sistema de Gestión de Prácticas de Fisiología</p>
    <p>Si no solicitaste este código, ignora este mensaje.</p>
    </div>
    </div>
    </div>
    </body>
    </html>
    ';

    $email_enviado = enviarEmail($email, $asunto, $mensaje);

    if (!$email_enviado) {
        registrarLog('ERROR', 'Fallo al enviar código de verificación', ['email' => $email, 'actividad_id' => $actividad_id]);
        responderJSON([
            'success' => false,
            'error' => 'Error al enviar el email. Intenta nuevamente.'
        ], 500);
    }

    // Registrar evento exitoso
    registrarLog('INFO', 'Código de verificación enviado', ['email' => $email, 'actividad_id' => $actividad_id]);

    responderJSON([
        'success' => true,
        'message' => 'Código de verificación enviado. Revisa tu bandeja de entrada y spam.',
        'data' => [
            'email' => $email,
            'expira_en' => CODIGO_VERIFICACION_TIMEOUT,
            'actividad' => $actividad['info_basica']['nombre']
        ]
    ], 200);

} catch (Exception $e) {
    responderJSON([
        'success' => false,
        'error' => 'Error del servidor: ' . $e->getMessage()
    ], 500);
}
?>
