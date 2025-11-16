<?php
/**
 * profesor/accesos.php - Gestión de accesos de actividad
 */

require_once '../config.php';

session_start();

if (!verificarRol('profesor')) {
    header('Location: login.php');
    exit;
}

$rut = $_SESSION['rut'];

// Sanitizar y validar actividad_id
$actividad_id = sanitizarString($_GET['actividad'] ?? '', ['max_length' => 50]);

if (empty($actividad_id)) {
    header('Location: actividades.php');
    exit;
}

// Prevenir path traversal
if (preg_match('/[\.\/\\\\]/', $actividad_id)) {
    registrarEventoSeguridad('Intento de path traversal en accesos', [
        'actividad_id' => $actividad_id,
        'profesor_rut' => $rut,
        'ip' => obtenerIP()
    ]);
    header('Location: actividades.php');
    exit;
}

// Verificar que la actividad existe y pertenece al profesor
$actividades = cargarJSON(ACTIVIDADES_FILE);
if (!isset($actividades[$actividad_id]) || $actividades[$actividad_id]['profesor_rut'] !== $rut) {
    registrarEventoSeguridad('Intento de acceso no autorizado a accesos de actividad', [
        'actividad_id' => $actividad_id,
        'profesor_rut' => $rut,
        'ip' => obtenerIP()
    ]);
    header('Location: actividades.php');
    exit;
}

$actividad = $actividades[$actividad_id];

// Obtener estadísticas
$estudiantes_registrados = $actividad['accesos']['estudiantes_registrados'] ?? [];
?>
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Accesos de Actividad - FisioaccessPC</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: linear-gradient(135deg, #7c3aed 0%, #a855f7 50%, #c084fc 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .navbar {
            background: rgba(255, 255, 255, 0.15);
            backdrop-filter: blur(10px);
            border-radius: 16px;
            border: 1px solid rgba(255, 255, 255, 0.3);
            padding: 15px 25px;
            margin-bottom: 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .navbar-brand {
            color: white;
            font-size: 20px;
            font-weight: 600;
        }
        
        .container {
            max-width: 1000px;
            margin: 0 auto;
        }
        
        .header {
            background: rgba(255, 255, 255, 0.15);
            backdrop-filter: blur(10px);
            border-radius: 16px;
            border: 1px solid rgba(255, 255, 255, 0.3);
            padding: 25px;
            margin-bottom: 20px;
        }
        
        h1 {
            color: white;
            font-size: 28px;
            margin-bottom: 10px;
        }
        
        .actividad-info {
            color: rgba(255, 255, 255, 0.9);
            font-size: 14px;
        }
        
        .card {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-radius: 16px;
            border: 1px solid rgba(255, 255, 255, 0.3);
            padding: 30px;
            margin-bottom: 20px;
        }
        
        .card-title {
            font-size: 20px;
            font-weight: 600;
            color: #1f2937;
            margin-bottom: 20px;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 30px;
        }
        
        .stat-box {
            background: linear-gradient(135deg, #f5f3ff 0%, #ede9fe 100%);
            padding: 20px;
            border-radius: 12px;
            border: 2px solid #7c3aed;
        }
        
        .stat-value {
            font-size: 32px;
            font-weight: 700;
            color: #7c3aed;
        }
        
        .stat-label {
            color: #6b7280;
            font-size: 14px;
            margin-top: 5px;
        }
        
        .access-section {
            background: #f9fafb;
            padding: 20px;
            border-radius: 12px;
            margin-bottom: 20px;
        }
        
        .access-label {
            font-weight: 600;
            color: #4b5563;
            margin-bottom: 10px;
            font-size: 14px;
        }
        
        .access-input {
            display: flex;
            gap: 10px;
            margin-bottom: 10px;
        }
        
        input[type="text"],
        textarea {
            flex: 1;
            padding: 12px;
            border: 2px solid #e5e7eb;
            border-radius: 8px;
            font-size: 14px;
            font-family: 'Courier New', monospace;
            background: white;
        }
        
        textarea {
            min-height: 120px;
            resize: vertical;
            font-family: monospace;
            font-size: 12px;
        }
        
        .btn {
            padding: 12px 20px;
            background: #7c3aed;
            color: white;
            border: none;
            border-radius: 8px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
            font-size: 14px;
        }
        
        .btn:hover {
            background: #6d28d9;
            transform: translateY(-2px);
        }
        
        .btn-secondary {
            background: #6b7280;
        }
        
        .btn-secondary:hover {
            background: #4b5563;
        }
        
        .btn-success {
            background: #10b981;
        }
        
        .btn-success:hover {
            background: #059669;
        }
        
        .help-text {
            font-size: 13px;
            color: #6b7280;
            margin-top: 8px;
        }
        
        .estudiantes-list {
            max-height: 300px;
            overflow-y: auto;
        }
        
        .estudiante-item {
            display: flex;
            align-items: center;
            gap: 10px;
            padding: 10px;
            background: white;
            border: 1px solid #e5e7eb;
            border-radius: 8px;
            margin-bottom: 8px;
        }
        
        .estudiante-email {
            flex: 1;
            color: #1f2937;
        }
        
        .badge {
            padding: 4px 10px;
            border-radius: 6px;
            font-size: 12px;
            font-weight: 600;
        }
        
        .badge-new {
            background: #dbeafe;
            color: #1e40af;
        }
        
        .preview-iframe {
            width: 100%;
            height: 200px;
            border: 2px solid #e5e7eb;
            border-radius: 8px;
            margin-top: 15px;
        }
    </style>
</head>
<body>
    <div class="navbar">
        <div class="navbar-brand">🫁 FisioaccessPC</div>
        <a href="actividades.php" class="btn btn-secondary">← Volver a Actividades</a>
    </div>
    
    <div class="container">
        <div class="header">
            <h1>🔗 Accesos de Actividad</h1>
            <div class="actividad-info">
                <strong><?= htmlspecialchars($actividad['info_basica']['nombre']) ?></strong><br>
                ID: <?= $actividad_id ?> • Tipo: <?= TIPOS_ESTUDIO[$actividad['info_basica']['tipo_estudio']] ?>
            </div>
        </div>
        
        <!-- Estadísticas -->
        <div class="card">
            <div class="card-title">📊 Estadísticas de Acceso</div>
            <div class="stats-grid">
                <div class="stat-box">
                    <div class="stat-value"><?= count($actividad['configuracion']['estudiantes_inscritos']) ?></div>
                    <div class="stat-label">Inscritos (CSV)</div>
                </div>
                <div class="stat-box">
                    <div class="stat-value"><?= count($estudiantes_registrados) ?></div>
                    <div class="stat-label">Registrados (Web)</div>
                </div>
                <div class="stat-box">
                    <div class="stat-value"><?= $actividad['accesos']['modo_registro'] === 'cerrado' ? 'Cerrado' : 'Abierto' ?></div>
                    <div class="stat-label">Modo de Registro</div>
                </div>
            </div>
        </div>
        
        <!-- Link Directo -->
        <div class="card">
            <div class="card-title">🔗 Link Directo</div>
            <div class="access-section">
                <div class="access-label">URL para compartir:</div>
                <div class="access-input">
                    <input type="text" 
                           id="link-directo" 
                           value="<?= htmlspecialchars($actividad['accesos']['link_directo']) ?>" 
                           readonly>
                    <button class="btn" onclick="copiarTexto('link-directo', this)">📋 Copiar</button>
                </div>
                <div class="help-text">
                    Comparte este link con tus estudiantes o úsalo en Moodle como "URL/Recurso externo"
                </div>
            </div>
        </div>
        
        <!-- HTML Embebido -->
        <div class="card">
            <div class="card-title">💻 Código HTML Embebido</div>
            <div class="access-section">
                <div class="access-label">Código para copiar en Moodle (Etiqueta HTML):</div>
                <div class="access-input">
                    <textarea id="html-embed" readonly><?= htmlspecialchars($actividad['accesos']['html_embed']) ?></textarea>
                </div>
                <button class="btn" onclick="copiarTexto('html-embed', this)" style="margin-bottom: 15px;">📋 Copiar HTML</button>
                
                <div class="help-text" style="margin-bottom: 15px;">
                    <strong>Instrucciones para Moodle:</strong><br>
                    1. Activa edición en tu curso<br>
                    2. Agregar actividad/recurso → Etiqueta<br>
                    3. Click en el botón "&lt;/&gt;" (HTML) en el editor<br>
                    4. Pega el código copiado<br>
                    5. Guarda cambios
                </div>
                
                <div class="access-label">Vista previa:</div>
                <iframe class="preview-iframe" srcdoc="<?= htmlspecialchars($actividad['accesos']['html_embed']) ?>"></iframe>
            </div>
        </div>
        
        <!-- Paquete H5P (Placeholder) -->
        <div class="card">
            <div class="card-title">📦 Paquete H5P</div>
            <div class="access-section">
                <p style="color: #6b7280; margin-bottom: 15px;">
                    Genera un paquete H5P para subir directamente a Moodle como actividad interactiva.
                </p>
                <button class="btn" onclick="alert('Funcionalidad H5P en desarrollo')">
                    📥 Generar paquete H5P
                </button>
                <div class="help-text" style="margin-top: 10px;">
                    Esta funcionalidad estará disponible próximamente
                </div>
            </div>
        </div>
        
        <!-- Estudiantes Registrados -->
        <div class="card">
            <div class="card-title">👥 Estudiantes Registrados</div>
            
            <?php if (empty($estudiantes_registrados)): ?>
                <p style="color: #6b7280; text-align: center; padding: 20px;">
                    Aún no hay estudiantes registrados vía web
                </p>
            <?php else: ?>
                <div class="estudiantes-list">
                    <?php foreach ($estudiantes_registrados as $email): ?>
                        <div class="estudiante-item">
                            <span class="estudiante-email"><?= htmlspecialchars($email) ?></span>
                            <span class="badge badge-new">Web</span>
                        </div>
                    <?php endforeach; ?>
                </div>
            <?php endif; ?>
        </div>
        
        <!-- Configuración -->
        <div class="card">
            <div class="card-title">⚙️ Configuración de Acceso</div>
            <div class="access-section">
                <p style="margin-bottom: 10px;">
                    <strong>Modo de registro:</strong> 
                    <?= $actividad['accesos']['modo_registro'] === 'cerrado' ? 'Cerrado (solo lista CSV)' : 'Abierto (auto-registro)' ?>
                </p>
                <p style="margin-bottom: 10px;">
                    <strong>Dominio de email:</strong> 
                    <?= htmlspecialchars($actividad['accesos']['dominio_email']) ?>
                </p>
                <p style="margin-bottom: 10px;">
                    <strong>Token de actividad:</strong> 
                    <code style="background: #f3f4f6; padding: 4px 8px; border-radius: 4px;">
                        <?= htmlspecialchars($actividad['accesos']['token_actividad']) ?>
                    </code>
                </p>
                
                <div class="help-text" style="margin-top: 15px;">
                    Para cambiar la configuración, edita la actividad desde el panel principal
                </div>
            </div>
        </div>
    </div>
    
    <script>
        function copiarTexto(elementId, button) {
            const element = document.getElementById(elementId);
            element.select();
            document.execCommand('copy');
            
            const originalText = button.textContent;
            button.textContent = '✓ Copiado';
            button.style.background = '#10b981';
            
            setTimeout(() => {
                button.textContent = originalText;
                button.style.background = '#7c3aed';
            }, 2000);
        }
    </script>
</body>
</html>