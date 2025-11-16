<?php
/**
 * api/generar_accesos.php - Generar/obtener accesos de actividad para profesor
 * 
 * GET /api/generar_accesos.php?actividad_id=ACT123
 * POST /api/generar_accesos.php?action=regenerar&actividad_id=ACT123
 */

require_once '../config.php';

// Configurar CORS de forma segura
configurarCORS();

// Manejar preflight OPTIONS
if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    http_response_code(200);
    exit;
}

session_start();

header('Content-Type: application/json; charset=utf-8');

// Verificar autenticación de profesor
if (!verificarRol('profesor')) {
    registrarEventoSeguridad('Intento de acceso no autorizado a generar_accesos', [
        'ip' => obtenerIP()
    ]);
    responderJSON([
        'success' => false,
        'error' => 'No autorizado. Debes ser profesor.'
    ], 403);
}

$rut = $_SESSION['rut'];

// Sanitizar y validar actividad_id
$actividad_id = sanitizarString($_GET['actividad_id'] ?? $_POST['actividad_id'] ?? '', ['max_length' => 50]);

if (empty($actividad_id)) {
    responderJSON([
        'success' => false,
        'error' => 'actividad_id es requerido'
    ], 400);
}

// Prevenir path traversal
if (preg_match('/[\.\/\\\\]/', $actividad_id)) {
    registrarEventoSeguridad('Intento de path traversal en generar_accesos', [
        'actividad_id' => $actividad_id,
        'profesor_rut' => $rut,
        'ip' => obtenerIP()
    ]);
    responderJSON([
        'success' => false,
        'error' => 'Parámetro inválido'
    ], 400);
}

try {
    $actividades = cargarJSON(ACTIVIDADES_FILE);
    
    if (!isset($actividades[$actividad_id])) {
        responderJSON([
            'success' => false,
            'error' => 'Actividad no encontrada'
        ], 404);
    }
    
    $actividad = $actividades[$actividad_id];
    
    // Verificar que la actividad pertenezca al profesor
    if ($actividad['profesor_rut'] !== $rut) {
        responderJSON([
            'success' => false,
            'error' => 'No tienes permiso para acceder a esta actividad'
        ], 403);
    }
    
    // Si es POST con action=regenerar, regenerar token
    if ($_SERVER['REQUEST_METHOD'] === 'POST' && ($_GET['action'] ?? '') === 'regenerar') {
        $nuevo_token = generarToken(12);
        $actividades[$actividad_id]['accesos']['token_actividad'] = $nuevo_token;

        // Regenerar URLs
        $url_base = $actividades[$actividad_id]['accesos']['url_base'];
        $actividades[$actividad_id]['accesos']['link_directo'] = $url_base . '/estudiante/acceso.php?token=' . $nuevo_token;
        $actividades[$actividad_id]['accesos']['html_embed'] = generarHTMLEmbebido($actividades[$actividad_id]);
        $actividades[$actividad_id]['accesos']['fecha_generacion'] = formatearFecha();

        guardarJSON(ACTIVIDADES_FILE, $actividades);

        // Logging de regeneración
        registrarLog('INFO', 'Token de acceso regenerado', [
            'actividad_id' => $actividad_id,
            'profesor_rut' => $rut,
            'ip' => obtenerIP()
        ]);

        $actividad = $actividades[$actividad_id];
    }
    
    // Generar accesos si no existen
    if (empty($actividad['accesos']['link_directo']) || empty($actividad['accesos']['html_embed'])) {
        $token = $actividad['accesos']['token_actividad'];
        $url_base = $actividad['accesos']['url_base'];
        
        $actividades[$actividad_id]['accesos']['link_directo'] = $url_base . '/estudiante/acceso.php?token=' . $token;
        $actividades[$actividad_id]['accesos']['html_embed'] = generarHTMLEmbebido($actividades[$actividad_id]);
        
        guardarJSON(ACTIVIDADES_FILE, $actividades);
        $actividad = $actividades[$actividad_id];
    }
    
    // Obtener estadísticas de accesos
    $estudiantes_registrados = $actividad['accesos']['estudiantes_registrados'] ?? [];
    $total_registrados = count($estudiantes_registrados);
    
    responderJSON([
        'success' => true,
        'data' => [
            'actividad' => [
                'id' => $actividad_id,
                'nombre' => $actividad['info_basica']['nombre'],
                'tipo_estudio' => $actividad['info_basica']['tipo_estudio']
            ],
            'accesos' => [
                'token_actividad' => $actividad['accesos']['token_actividad'],
                'link_directo' => $actividad['accesos']['link_directo'],
                'html_embed' => $actividad['accesos']['html_embed'],
                'modo_registro' => $actividad['accesos']['modo_registro'],
                'dominio_email' => $actividad['accesos']['dominio_email']
            ],
            'estadisticas' => [
                'total_inscritos_csv' => count($actividad['configuracion']['estudiantes_inscritos']),
                'total_registrados' => $total_registrados,
                'estudiantes_registrados' => $estudiantes_registrados
            ]
        ]
    ], 200);
    
} catch (Exception $e) {
    responderJSON([
        'success' => false,
        'error' => 'Error del servidor: ' . $e->getMessage()
    ], 500);
}

/**
 * Generar HTML embebido para Moodle
 */
function generarHTMLEmbebido($actividad) {
    $nombre = htmlspecialchars($actividad['info_basica']['nombre']);
    $descripcion = htmlspecialchars(substr($actividad['info_basica']['descripcion'], 0, 200));
    $fecha_cierre = date('d/m/Y H:i', strtotime($actividad['info_basica']['fecha_cierre']));
    $link = $actividad['accesos']['link_directo'];
    $tipo = TIPOS_ESTUDIO[$actividad['info_basica']['tipo_estudio']];
    
    $html = '<div style="border:2px solid #7c3aed; border-radius:12px; padding:25px; max-width:700px; background:linear-gradient(135deg, #f5f3ff 0%, #ede9fe 100%); font-family: -apple-system, BlinkMacSystemFont, \'Segoe UI\', sans-serif;">
  <h2 style="color:#5b21b6; margin:0 0 15px 0; font-size:24px;">📝 ' . $nombre . '</h2>
  <div style="background:white; padding:15px; border-radius:8px; margin-bottom:15px;">
    <p style="margin:0 0 10px 0; color:#4b5563;"><strong style="color:#7c3aed;">📊 Tipo:</strong> ' . $tipo . '</p>
    <p style="margin:0 0 10px 0; color:#4b5563;"><strong style="color:#7c3aed;">📅 Fecha límite:</strong> ' . $fecha_cierre . '</p>
    <p style="margin:0; color:#4b5563;"><strong style="color:#7c3aed;">📄 Descripción:</strong><br>' . $descripcion . '...</p>
  </div>
  <a href="' . $link . '" 
     style="display:inline-block; background:#7c3aed; color:white; 
            padding:14px 28px; text-decoration:none; border-radius:8px; 
            font-weight:600; font-size:16px; transition: all 0.3s;">
    🎯 Comenzar Actividad
  </a>
</div>';
    
    return $html;
}
?>