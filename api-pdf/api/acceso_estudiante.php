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

header('Content-Type: application/json; charset=utf-8');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: POST, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type');

// Manejar preflight OPTIONS
if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    http_response_code(200);
    exit;
}

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
    
    // Validar formato de email
    if (!filter_var($email, FILTER_VALIDATE_EMAIL)) {
        responderJSON([
            'success' => false,
            'error' => 'Formato de email inválido'
        ], 400);
    }
    
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
    
    // Verificar modo de registro
    $modo_registro = $actividad['accesos']['modo_registro'] ?? 'cerrado';
    $dominio_requerido = $actividad['accesos']['dominio_email'] ?? null;
    
    // Validar dominio de email si está configurado
    if ($dominio_requerido) {
        if (!validarEmailInstitucional($email, $dominio_requerido)) {
            responderJSON([
                'success' => false,
                'error' => 'Debes usar tu email institucional ' . $dominio_requerido
            ], 403);
        }
    }
    
    // Si modo cerrado, verificar que esté en la lista
    if ($modo_registro === 'cerrado') {
        $estudiantes = cargarJSON(ESTUDIANTES_FILE);
        $estudiante_valido = false;
        
        // Buscar estudiante por email en la lista de inscritos
        $inscritos = $actividad['configuracion']['estudiantes_inscritos'] ?? [];
        
        foreach ($inscritos as $rut_estudiante) {
            if (isset($estudiantes[$rut_estudiante])) {
                $email_estudiante = strtolower($estudiantes[$rut_estudiante]['email'] ?? '');
                if ($email_estudiante === $email) {
                    $estudiante_valido = true;
                    break;
                }
            }
        }
        
        if (!$estudiante_valido) {
            responderJSON([
                'success' => false,
                'error' => 'No estás inscrito en esta actividad. Contacta a tu profesor.'
            ], 403);
        }
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
        responderJSON([
            'success' => false,
            'error' => 'Error al enviar el email. Intenta nuevamente.'
        ], 500);
    }
    
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