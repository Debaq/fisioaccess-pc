<?php
/**
 * estudiante/actividad_detalle.php - Ver detalles completos de una actividad
 */

require_once '../config.php';

session_start();

if (!verificarRol('estudiante')) {
    header('Location: ../index.html');
    exit;
}

$rut = $_SESSION['rut'];
$actividad_id = $_GET['id'] ?? '';

if (empty($actividad_id)) {
    header('Location: dashboard.php');
    exit;
}

// Cargar actividad
$actividades = cargarJSON(ACTIVIDADES_FILE);

if (!isset($actividades[$actividad_id])) {
    header('Location: dashboard.php');
    exit;
}

$actividad = $actividades[$actividad_id];

// Verificar que el estudiante esté inscrito
if (!in_array($rut, $actividad['estudiantes_inscritos'] ?? [])) {
    header('Location: dashboard.php');
    exit;
}

// Cargar profesor
$profesores = cargarJSON(PROFESORES_FILE);
$profesor = $profesores[$actividad['profesor_rut']] ?? null;
?>
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title><?= htmlspecialchars($actividad['info_basica']['nombre']) ?> - FisioaccessPC</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: linear-gradient(135deg, #c084fc 0%, #a855f7 50%, #7c3aed 100%);
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
            color: white;
        }
        
        .navbar-brand {
            font-size: 20px;
            font-weight: 600;
        }
        
        .container {
            max-width: 900px;
            margin: 0 auto;
        }
        
        .section {
            background: rgba(255, 255, 255, 0.15);
            backdrop-filter: blur(10px);
            border-radius: 16px;
            border: 1px solid rgba(255, 255, 255, 0.3);
            padding: 25px;
            margin-bottom: 20px;
            color: white;
        }
        
        .section-title {
            font-size: 22px;
            font-weight: 600;
            margin-bottom: 20px;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .info-grid {
            display: grid;
            gap: 15px;
        }
        
        .info-item {
            background: rgba(255, 255, 255, 0.1);
            padding: 15px;
            border-radius: 10px;
        }
        
        .info-label {
            font-size: 13px;
            opacity: 0.8;
            margin-bottom: 5px;
        }
        
        .info-value {
            font-size: 16px;
            font-weight: 500;
        }
        
        .archivos-list {
            display: grid;
            gap: 10px;
        }
        
        .archivo-item {
            background: rgba(255, 255, 255, 0.1);
            padding: 15px;
            border-radius: 10px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .archivo-info {
            flex: 1;
        }
        
        .archivo-nombre {
            font-weight: 500;
            margin-bottom: 5px;
        }
        
        .archivo-tipo {
            font-size: 13px;
            opacity: 0.8;
        }
        
        .btn {
            padding: 10px 20px;
            border: none;
            border-radius: 8px;
            font-size: 14px;
            font-weight: 500;
            cursor: pointer;
            text-decoration: none;
            display: inline-block;
            transition: all 0.2s;
        }
        
        .btn-primary {
            background: white;
            color: #7c3aed;
        }
        
        .btn-primary:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
        }
        
        .btn-secondary {
            background: rgba(255, 255, 255, 0.2);
            color: white;
            border: 1px solid rgba(255, 255, 255, 0.3);
        }
        
        .btn-secondary:hover {
            background: rgba(255, 255, 255, 0.3);
        }
        
        .btn-small {
            padding: 6px 12px;
            font-size: 13px;
        }
        
        .objetivos-list, .protocolo-list {
            list-style: none;
            padding: 0;
        }
        
        .objetivos-list li, .protocolo-list li {
            background: rgba(255, 255, 255, 0.1);
            padding: 10px 15px;
            border-radius: 8px;
            margin-bottom: 8px;
            padding-left: 35px;
            position: relative;
        }
        
        .objetivos-list li:before {
            content: '✓';
            position: absolute;
            left: 12px;
            color: #10b981;
            font-weight: 700;
        }
        
        .protocolo-list li:before {
            content: attr(data-num);
            position: absolute;
            left: 12px;
            color: #7c3aed;
            font-weight: 700;
            background: white;
            width: 20px;
            height: 20px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 11px;
        }
        
        .empty-state {
            text-align: center;
            padding: 40px;
            opacity: 0.7;
        }
    </style>
</head>
<body>
    <div class="navbar">
        <div class="navbar-brand">🫁 FisioaccessPC</div>
        <a href="dashboard.php" class="btn btn-secondary btn-small">← Volver al Dashboard</a>
    </div>
    
    <div class="container">
        <!-- Información Básica -->
        <div class="section">
            <h1 style="font-size: 28px; margin-bottom: 20px;">
                <?= htmlspecialchars($actividad['info_basica']['nombre']) ?>
            </h1>
            
            <div class="info-grid">
                <div class="info-item">
                    <div class="info-label">📊 Tipo de Estudio</div>
                    <div class="info-value"><?= htmlspecialchars($actividad['info_basica']['tipo_estudio'] ?? 'No especificado') ?></div>
                </div>
                
                <div class="info-item">
                    <div class="info-label">🎯 Tipo de Sesión</div>
                    <div class="info-value"><?= htmlspecialchars($actividad['info_basica']['tipo_sesion'] ?? 'No especificado') ?></div>
                </div>
                
                <div class="info-item">
                    <div class="info-label">👨‍🏫 Profesor</div>
                    <div class="info-value"><?= $profesor ? htmlspecialchars($profesor['nombre']) : 'Desconocido' ?></div>
                </div>
                
                <div class="info-item">
                    <div class="info-label">📅 Fecha de Inicio</div>
                    <div class="info-value"><?= date('d/m/Y H:i', strtotime($actividad['info_basica']['fecha_inicio'])) ?></div>
                </div>
                
                <div class="info-item">
                    <div class="info-label">🕐 Fecha de Cierre</div>
                    <div class="info-value"><?= date('d/m/Y H:i', strtotime($actividad['info_basica']['fecha_cierre'])) ?></div>
                </div>
            </div>
        </div>
        
        <!-- Descripción -->
        <div class="section">
            <div class="section-title">📝 Descripción</div>
            <p style="line-height: 1.6;"><?= nl2br(htmlspecialchars($actividad['info_basica']['descripcion'])) ?></p>
        </div>
        
        <!-- Objetivos -->
        <?php if (!empty($actividad['contenido']['objetivos'])): ?>
        <div class="section">
            <div class="section-title">🎯 Objetivos de Aprendizaje</div>
            <ul class="objetivos-list">
                <?php foreach ($actividad['contenido']['objetivos'] as $objetivo): ?>
                    <li><?= htmlspecialchars($objetivo) ?></li>
                <?php endforeach; ?>
            </ul>
        </div>
        <?php endif; ?>
        
        <!-- Protocolo -->
        <?php if (!empty($actividad['contenido']['protocolo'])): ?>
        <div class="section">
            <div class="section-title">📋 Protocolo / Instrucciones</div>
            <ul class="protocolo-list">
                <?php foreach ($actividad['contenido']['protocolo'] as $index => $paso): ?>
                    <li data-num="<?= $index + 1 ?>"><?= htmlspecialchars($paso) ?></li>
                <?php endforeach; ?>
            </ul>
        </div>
        <?php endif; ?>
        
        <!-- Archivos y Materiales -->
        <div class="section">
            <div class="section-title">📎 Archivos y Materiales</div>
            
            <div class="archivos-list">
                <?php if (isset($actividad['archivos']['pdf_path']) && $actividad['archivos']['pdf_path']): ?>
                <div class="archivo-item">
                    <div class="archivo-info">
                        <div class="archivo-nombre">📄 Documento PDF Principal</div>
                        <div class="archivo-tipo">Archivo PDF de la actividad</div>
                    </div>
                    <a href="../<?= htmlspecialchars($actividad['archivos']['pdf_path']) ?>" 
                       download 
                       class="btn btn-primary btn-small">
                        ⬇️ Descargar
                    </a>
                </div>
                <?php endif; ?>
                
                <?php if (isset($actividad['archivos']['material_complementario']) && $actividad['archivos']['material_complementario']): ?>
                <div class="archivo-item">
                    <div class="archivo-info">
                        <div class="archivo-nombre">📎 Material Complementario</div>
                        <div class="archivo-tipo">Material adicional de apoyo</div>
                    </div>
                    <a href="../<?= htmlspecialchars($actividad['archivos']['material_complementario']) ?>" 
                       download 
                       class="btn btn-primary btn-small">
                        ⬇️ Descargar
                    </a>
                </div>
                <?php endif; ?>
                
                <?php if ((!isset($actividad['archivos']['pdf_path']) || !$actividad['archivos']['pdf_path']) && 
                          (!isset($actividad['archivos']['material_complementario']) || !$actividad['archivos']['material_complementario'])): ?>
                <div class="empty-state">
                    📭 No hay archivos disponibles para esta actividad
                </div>
                <?php endif; ?>
            </div>
        </div>
        
        <!-- Cuotas de Estudios -->
        <?php if (isset($actividad['configuracion']['cuotas'])): ?>
        <div class="section">
            <div class="section-title">📊 Cuotas de Estudios Permitidos</div>
            <div class="info-grid" style="grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));">
                <?php foreach ($actividad['configuracion']['cuotas'] as $tipo => $cuota): ?>
                    <?php if ($cuota > 0): ?>
                    <div class="info-item">
                        <div class="info-label"><?= TIPOS_ESTUDIO[$tipo] ?? $tipo ?></div>
                        <div class="info-value"><?= $cuota ?> estudio(s)</div>
                    </div>
                    <?php endif; ?>
                <?php endforeach; ?>
            </div>
        </div>
        <?php endif; ?>
        
        <!-- Evaluación -->
        <?php if ($actividad['evaluacion']['es_calificada']): ?>
        <div class="section">
            <div class="section-title">📝 Evaluación</div>
            <div class="info-grid">
                <div class="info-item">
                    <div class="info-label">Ponderación</div>
                    <div class="info-value"><?= $actividad['evaluacion']['ponderacion'] ?>%</div>
                </div>
                <div class="info-item">
                    <div class="info-label">Escala</div>
                    <div class="info-value"><?= $actividad['evaluacion']['escala'] ?></div>
                </div>
                <div class="info-item">
                    <div class="info-label">Retroalimentación</div>
                    <div class="info-value"><?= $actividad['evaluacion']['permite_retroalimentacion'] ? '✓ Sí' : '✗ No' ?></div>
                </div>
            </div>
        </div>
        <?php endif; ?>
    </div>
</body>
</html>