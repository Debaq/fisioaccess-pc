<?php
/**
 * profesor/revisar.php - Revisar y calificar entregas de estudiantes
 */

require_once '../config.php';

session_start();

if (!verificarRol('profesor')) {
    header('Location: login.php');
    exit;
}

$rut = $_SESSION['rut'];
$mensaje = '';
$tipo_mensaje = '';

// Cargar todas las entregas del profesor
$todas_actividades = cargarJSON(ACTIVIDADES_FILE);
$mis_actividades = array_filter($todas_actividades, fn($a) => $a['profesor_rut'] === $rut);

$todas_entregas = cargarJSON(ENTREGAS_FILE);
$estudiantes_db = cargarJSON(ESTUDIANTES_FILE);

// Filtrar entregas de mis actividades
$mis_entregas = array_filter($todas_entregas, function($e) use ($mis_actividades) {
    return isset($mis_actividades[$e['actividad_id']]);
});

// Procesar revisión
if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['revisar'])) {
    // Validar CSRF token
    $csrf_token = $_POST['csrf_token'] ?? '';
    if (!validarTokenCSRF($csrf_token)) {
        $mensaje = 'Token de seguridad inválido. Intenta nuevamente.';
        $tipo_mensaje = 'error';
        registrarEventoSeguridad('CSRF token inválido en revisar entrega', [
            'profesor_rut' => $rut,
            'ip' => obtenerIP()
        ]);
    } else {
        // Sanitizar inputs
        $entrega_id = sanitizarString($_POST['entrega_id'] ?? '', ['max_length' => 50]);
        $nota = floatval($_POST['nota'] ?? 0);
        $retroalimentacion = sanitizarString($_POST['retroalimentacion'] ?? '', ['max_length' => 2000]);

        if (empty($entrega_id) || !isset($todas_entregas[$entrega_id])) {
            $mensaje = 'Entrega no encontrada';
            $tipo_mensaje = 'error';
        } else {
            $actividad_id = $todas_entregas[$entrega_id]['actividad_id'];
            $actividad = $mis_actividades[$actividad_id];
            $escala = $actividad['evaluacion']['escala'] ?? '1.0-7.0';

            // Validar nota según escala
            $nota_valida = false;
            if ($escala === '1.0-7.0') {
                if ($nota >= 1.0 && $nota <= 7.0) {
                    $nota_valida = true;
                } else {
                    $mensaje = 'La nota debe estar entre 1.0 y 7.0';
                    $tipo_mensaje = 'error';
                }
            } elseif ($escala === '0-100') {
                if ($nota >= 0 && $nota <= 100) {
                    $nota_valida = true;
                } else {
                    $mensaje = 'La nota debe estar entre 0 y 100';
                    $tipo_mensaje = 'error';
                }
            } else {
                // Escala alfanumérica (A-F), validar más adelante si es necesario
                $nota_valida = true;
            }

            if ($nota_valida) {
                // Actualizar revisión
                $todas_entregas[$entrega_id]['revision'] = [
                    'estado' => 'revisada',
                    'nota' => $nota,
                    'retroalimentacion' => $retroalimentacion,
                    'fecha_revision' => formatearFecha(),
                    'revisor_rut' => $rut
                ];

                guardarJSON(ENTREGAS_FILE, $todas_entregas);

                // Logging
                registrarLog('INFO', 'Entrega revisada', [
                    'entrega_id' => $entrega_id,
                    'actividad_id' => $actividad_id,
                    'profesor_rut' => $rut,
                    'estudiante_rut' => $todas_entregas[$entrega_id]['estudiante_rut'],
                    'nota' => $nota,
                    'ip' => obtenerIP()
                ]);
        
        // Actualizar estadísticas de la actividad
        $revisadas = count(array_filter($todas_entregas, function($e) use ($actividad_id) {
            return $e['actividad_id'] === $actividad_id && $e['revision']['estado'] === 'revisada';
        }));
        
        $pendientes = count(array_filter($todas_entregas, function($e) use ($actividad_id) {
            return $e['actividad_id'] === $actividad_id && $e['revision']['estado'] === 'pendiente';
        }));
        
        // Calcular promedio de notas
        $entregas_actividad = array_filter($todas_entregas, fn($e) => $e['actividad_id'] === $actividad_id && $e['revision']['estado'] === 'revisada');
        $sum_notas = array_sum(array_column(array_column($entregas_actividad, 'revision'), 'nota'));
        $promedio = count($entregas_actividad) > 0 ? $sum_notas / count($entregas_actividad) : 0;
        
        $todas_actividades[$actividad_id]['estadisticas']['entregas_revisadas'] = $revisadas;
        $todas_actividades[$actividad_id]['estadisticas']['entregas_pendientes'] = $pendientes;
        $todas_actividades[$actividad_id]['estadisticas']['promedio_nota'] = round($promedio, 2);
        
                guardarJSON(ACTIVIDADES_FILE, $todas_actividades);

                $mensaje = 'Entrega revisada exitosamente';
                $tipo_mensaje = 'success';

                // Recargar datos
                $mis_actividades = array_filter($todas_actividades, fn($a) => $a['profesor_rut'] === $rut);
                $todas_entregas = cargarJSON(ENTREGAS_FILE);
                $mis_entregas = array_filter($todas_entregas, function($e) use ($mis_actividades) {
                    return isset($mis_actividades[$e['actividad_id']]);
                });
            }
        }
    }
}

// Filtros - Sanitizar
$filtro_actividad = sanitizarString($_GET['actividad'] ?? '', ['max_length' => 50]);
$filtro_estado = sanitizarString($_GET['estado'] ?? 'pendiente', ['max_length' => 20]);

// Validar filtro_estado contra whitelist
$estados_validos = ['pendiente', 'revisada', 'todas'];
if (!in_array($filtro_estado, $estados_validos)) {
    $filtro_estado = 'pendiente';
}

// Aplicar filtros
$entregas_filtradas = $mis_entregas;

if (!empty($filtro_actividad)) {
    $entregas_filtradas = array_filter($entregas_filtradas, fn($e) => $e['actividad_id'] === $filtro_actividad);
}

if ($filtro_estado !== 'todas') {
    $entregas_filtradas = array_filter($entregas_filtradas, fn($e) => $e['revision']['estado'] === $filtro_estado);
}

// Ordenar por fecha (más recientes primero)
usort($entregas_filtradas, fn($a, $b) => strtotime($b['timestamp']) - strtotime($a['timestamp']));
?>
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Revisar Entregas - FisioaccessPC</title>
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
        }
        
        .navbar-brand {
            color: white;
            font-size: 20px;
            font-weight: 600;
            text-decoration: none;
        }
        
        .navbar-user {
            color: white;
            font-size: 14px;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
        }
        
        .page-header {
            background: rgba(255, 255, 255, 0.15);
            backdrop-filter: blur(10px);
            border-radius: 16px;
            border: 1px solid rgba(255, 255, 255, 0.3);
            padding: 20px 30px;
            margin-bottom: 20px;
            color: white;
        }
        
        .page-title {
            font-size: 24px;
            font-weight: 600;
            margin-bottom: 5px;
        }
        
        .page-subtitle {
            font-size: 14px;
            opacity: 0.9;
        }
        
        .filters {
            background: rgba(255, 255, 255, 0.15);
            backdrop-filter: blur(10px);
            border-radius: 16px;
            border: 1px solid rgba(255, 255, 255, 0.3);
            padding: 20px;
            margin-bottom: 20px;
            display: flex;
            gap: 15px;
            flex-wrap: wrap;
            align-items: center;
        }
        
        .filter-group {
            display: flex;
            flex-direction: column;
            gap: 5px;
        }
        
        .filter-label {
            color: white;
            font-size: 12px;
            font-weight: 500;
            text-transform: uppercase;
            opacity: 0.8;
        }
        
        select {
            padding: 8px 12px;
            border-radius: 8px;
            border: 1px solid rgba(255, 255, 255, 0.3);
            background: rgba(255, 255, 255, 0.2);
            color: white;
            font-size: 14px;
            cursor: pointer;
        }
        
        select option {
            background: #7c3aed;
            color: white;
        }
        
        .btn {
            padding: 8px 16px;
            border-radius: 8px;
            border: none;
            font-size: 14px;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.3s;
            text-decoration: none;
            display: inline-block;
        }
        
        .btn-primary {
            background: rgba(255, 255, 255, 0.25);
            color: white;
            border: 1px solid rgba(255, 255, 255, 0.3);
        }
        
        .btn-primary:hover {
            background: rgba(255, 255, 255, 0.35);
        }
        
        .alert {
            padding: 15px 20px;
            border-radius: 12px;
            margin-bottom: 20px;
            font-size: 14px;
            border: 1px solid rgba(255, 255, 255, 0.3);
        }
        
        .alert-success {
            background: rgba(34, 197, 94, 0.2);
            color: white;
            border-color: rgba(34, 197, 94, 0.3);
        }
        
        .alert-error {
            background: rgba(239, 68, 68, 0.2);
            color: white;
            border-color: rgba(239, 68, 68, 0.3);
        }
        
        .entregas-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
            gap: 20px;
        }
        
        .entrega-card {
            background: rgba(255, 255, 255, 0.15);
            backdrop-filter: blur(10px);
            border-radius: 16px;
            border: 1px solid rgba(255, 255, 255, 0.3);
            padding: 20px;
            color: white;
            transition: transform 0.3s;
        }
        
        .entrega-card:hover {
            transform: translateY(-5px);
        }
        
        .entrega-header {
            display: flex;
            justify-content: space-between;
            align-items: start;
            margin-bottom: 15px;
            padding-bottom: 15px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.2);
        }
        
        .entrega-estudiante {
            font-size: 16px;
            font-weight: 600;
        }
        
        .entrega-rut {
            font-size: 12px;
            opacity: 0.8;
            margin-top: 3px;
        }
        
        .estado-badge {
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 11px;
            font-weight: 600;
            text-transform: uppercase;
        }
        
        .estado-pendiente {
            background: rgba(251, 191, 36, 0.3);
            color: #fbbf24;
            border: 1px solid rgba(251, 191, 36, 0.5);
        }
        
        .estado-revisada {
            background: rgba(34, 197, 94, 0.3);
            color: #22c55e;
            border: 1px solid rgba(34, 197, 94, 0.5);
        }
        
        .entrega-info {
            margin-bottom: 15px;
        }
        
        .info-row {
            display: flex;
            justify-content: space-between;
            margin-bottom: 8px;
            font-size: 13px;
        }
        
        .info-label {
            opacity: 0.8;
        }
        
        .info-value {
            font-weight: 500;
        }
        
        .entrega-archivos {
            display: flex;
            gap: 10px;
            margin-bottom: 15px;
        }
        
        .archivo-btn {
            flex: 1;
            padding: 8px 12px;
            border-radius: 8px;
            background: rgba(255, 255, 255, 0.2);
            border: 1px solid rgba(255, 255, 255, 0.3);
            color: white;
            font-size: 12px;
            text-decoration: none;
            text-align: center;
            transition: all 0.3s;
        }
        
        .archivo-btn:hover {
            background: rgba(255, 255, 255, 0.3);
        }
        
        .entrega-acciones {
            display: flex;
            gap: 10px;
        }
        
        .btn-revisar {
            flex: 1;
            background: rgba(139, 92, 246, 0.8);
            color: white;
            padding: 10px;
            border: none;
            border-radius: 8px;
            font-size: 13px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
        }
        
        .btn-revisar:hover {
            background: rgba(139, 92, 246, 1);
        }
        
        .btn-ver-revision {
            flex: 1;
            background: rgba(34, 197, 94, 0.3);
            color: white;
            padding: 10px;
            border: none;
            border-radius: 8px;
            font-size: 13px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
        }
        
        .btn-ver-revision:hover {
            background: rgba(34, 197, 94, 0.5);
        }
        
        .nota-display {
            background: rgba(34, 197, 94, 0.2);
            padding: 15px;
            border-radius: 8px;
            margin-top: 15px;
            border: 1px solid rgba(34, 197, 94, 0.3);
        }
        
        .nota-valor {
            font-size: 24px;
            font-weight: 700;
            color: #22c55e;
            margin-bottom: 5px;
        }
        
        .nota-label {
            font-size: 11px;
            opacity: 0.8;
            text-transform: uppercase;
        }
        
        .retroalimentacion-display {
            background: rgba(255, 255, 255, 0.1);
            padding: 12px;
            border-radius: 8px;
            margin-top: 10px;
            font-size: 13px;
            line-height: 1.5;
            border: 1px solid rgba(255, 255, 255, 0.2);
        }
        
        .empty-state {
            background: rgba(255, 255, 255, 0.15);
            backdrop-filter: blur(10px);
            border-radius: 16px;
            border: 1px solid rgba(255, 255, 255, 0.3);
            padding: 60px 40px;
            text-align: center;
            color: white;
        }
        
        .empty-icon {
            font-size: 64px;
            margin-bottom: 20px;
            opacity: 0.5;
        }
        
        .empty-title {
            font-size: 20px;
            font-weight: 600;
            margin-bottom: 10px;
        }
        
        .empty-text {
            opacity: 0.8;
            font-size: 14px;
        }
        
        /* Modal */
        .modal {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.7);
            backdrop-filter: blur(5px);
            z-index: 1000;
            overflow-y: auto;
            padding: 20px;
        }
        
        .modal.active {
            display: flex;
            justify-content: center;
            align-items: center;
        }
        
        .modal-content {
            background: linear-gradient(135deg, #c084fc 0%, #a855f7 50%, #7c3aed 100%);
            border-radius: 20px;
            width: 100%;
            max-width: 700px;
            max-height: 90vh;
            overflow-y: auto;
            border: 2px solid rgba(255, 255, 255, 0.3);
        }
        
        .modal-header {
            padding: 25px 30px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.3);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .modal-title {
            color: white;
            font-size: 20px;
            font-weight: 600;
        }
        
        .modal-close {
            background: rgba(255, 255, 255, 0.2);
            border: none;
            color: white;
            font-size: 24px;
            cursor: pointer;
            width: 36px;
            height: 36px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: all 0.3s;
        }
        
        .modal-close:hover {
            background: rgba(255, 255, 255, 0.3);
        }
        
        .modal-body {
            padding: 30px;
        }
        
        .form-group {
            margin-bottom: 20px;
        }
        
        .form-label {
            display: block;
            color: white;
            font-size: 14px;
            font-weight: 500;
            margin-bottom: 8px;
        }
        
        .form-input {
            width: 100%;
            padding: 12px;
            border-radius: 8px;
            border: 1px solid rgba(255, 255, 255, 0.3);
            background: rgba(255, 255, 255, 0.2);
            color: white;
            font-size: 14px;
        }
        
        .form-input::placeholder {
            color: rgba(255, 255, 255, 0.6);
        }
        
        textarea.form-input {
            resize: vertical;
            min-height: 120px;
            font-family: inherit;
        }
        
        .form-info {
            background: rgba(255, 255, 255, 0.1);
            padding: 15px;
            border-radius: 8px;
            border: 1px solid rgba(255, 255, 255, 0.2);
            margin-bottom: 20px;
        }
        
        .info-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 12px;
            color: white;
            font-size: 13px;
        }
        
        .info-item {
            display: flex;
            flex-direction: column;
        }
        
        .info-item-label {
            opacity: 0.7;
            font-size: 11px;
            text-transform: uppercase;
            margin-bottom: 4px;
        }
        
        .info-item-value {
            font-weight: 600;
        }
        
        .modal-footer {
            padding: 20px 30px;
            border-top: 1px solid rgba(255, 255, 255, 0.3);
            display: flex;
            gap: 10px;
            justify-content: flex-end;
        }
        
        .btn-modal {
            padding: 12px 24px;
            border-radius: 8px;
            border: none;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
        }
        
        .btn-cancel {
            background: rgba(255, 255, 255, 0.2);
            color: white;
        }
        
        .btn-cancel:hover {
            background: rgba(255, 255, 255, 0.3);
        }
        
        .btn-submit {
            background: rgba(139, 92, 246, 0.8);
            color: white;
        }
        
        .btn-submit:hover {
            background: rgba(139, 92, 246, 1);
        }
        
        @media (max-width: 768px) {
            .entregas-grid {
                grid-template-columns: 1fr;
            }
            
            .filters {
                flex-direction: column;
                align-items: stretch;
            }
            
            .info-grid {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <div class="navbar">
        <a href="dashboard.php" class="navbar-brand">🫁 FisioaccessPC</a>
        <div class="navbar-user">
            Profesor • <a href="login.php" style="color: white;">Cerrar Sesión</a>
        </div>
    </div>
    
    <div class="container">
        <div class="page-header">
            <div class="page-title">✅ Revisar Entregas</div>
            <div class="page-subtitle">Califica y retroalimenta las entregas de tus estudiantes</div>
        </div>
        
        <?php if ($mensaje): ?>
            <div class="alert alert-<?= $tipo_mensaje ?>">
                <?= $mensaje ?>
            </div>
        <?php endif; ?>
        
        <div class="filters">
            <div class="filter-group">
                <label class="filter-label">Actividad</label>
                <select id="filtro-actividad" onchange="aplicarFiltros()">
                    <option value="">Todas las actividades</option>
                    <?php foreach ($mis_actividades as $act_id => $act): ?>
                        <option value="<?= $act_id ?>" <?= $filtro_actividad === $act_id ? 'selected' : '' ?>>
                            <?= htmlspecialchars($act['info_basica']['nombre']) ?>
                        </option>
                    <?php endforeach; ?>
                </select>
            </div>
            
            <div class="filter-group">
                <label class="filter-label">Estado</label>
                <select id="filtro-estado" onchange="aplicarFiltros()">
                    <option value="pendiente" <?= $filtro_estado === 'pendiente' ? 'selected' : '' ?>>Pendientes</option>
                    <option value="revisada" <?= $filtro_estado === 'revisada' ? 'selected' : '' ?>>Revisadas</option>
                    <option value="todas" <?= $filtro_estado === 'todas' ? 'selected' : '' ?>>Todas</option>
                </select>
            </div>
            
            <div style="margin-left: auto;">
                <a href="dashboard.php" class="btn btn-primary">← Volver al Dashboard</a>
            </div>
        </div>
        
        <?php if (empty($entregas_filtradas)): ?>
            <div class="empty-state">
                <div class="empty-icon">📭</div>
                <div class="empty-title">No hay entregas</div>
                <div class="empty-text">
                    <?php if ($filtro_estado === 'pendiente'): ?>
                        No tienes entregas pendientes de revisar en este momento
                    <?php elseif ($filtro_estado === 'revisada'): ?>
                        No has revisado entregas aún
                    <?php else: ?>
                        No hay entregas disponibles con los filtros seleccionados
                    <?php endif; ?>
                </div>
            </div>
        <?php else: ?>
            <div class="entregas-grid">
                <?php foreach ($entregas_filtradas as $ent_id => $entrega): ?>
                    <?php 
                        $actividad = $mis_actividades[$entrega['actividad_id']];
                        $estudiante = $estudiantes_db[$entrega['estudiante_rut']] ?? ['nombre' => 'Estudiante desconocido', 'rut' => $entrega['estudiante_rut']];
                        $fecha = new DateTime($entrega['timestamp']);
                    ?>
                    <div class="entrega-card">
                        <div class="entrega-header">
                            <div>
                                <div class="entrega-estudiante"><?= htmlspecialchars($estudiante['nombre']) ?></div>
                                <div class="entrega-rut"><?= htmlspecialchars($estudiante['rut']) ?></div>
                            </div>
                            <span class="estado-badge estado-<?= $entrega['revision']['estado'] ?>">
                                <?= $entrega['revision']['estado'] ?>
                            </span>
                        </div>
                        
                        <div class="entrega-info">
                            <div class="info-row">
                                <span class="info-label">Actividad:</span>
                                <span class="info-value"><?= htmlspecialchars($actividad['info_basica']['nombre']) ?></span>
                            </div>
                            <div class="info-row">
                                <span class="info-label">Tipo:</span>
                                <span class="info-value"><?= TIPOS_ESTUDIO[$actividad['info_basica']['tipo_estudio']] ?></span>
                            </div>
                            <div class="info-row">
                                <span class="info-label">Fecha entrega:</span>
                                <span class="info-value"><?= $fecha->format('d/m/Y H:i') ?></span>
                            </div>
                        </div>
                        
                        <div class="entrega-archivos">
                            <a href="../<?= htmlspecialchars($entrega['archivos']['pdf']) ?>" target="_blank" class="archivo-btn">
                                📄 Ver PDF
                            </a>
                            <a href="../<?= htmlspecialchars($entrega['archivos']['raw']) ?>" download class="archivo-btn">
                                💾 Descargar RAW
                            </a>
                        </div>
                        
                        <?php if ($entrega['revision']['estado'] === 'pendiente'): ?>
                            <div class="entrega-acciones">
                                <button class="btn-revisar" onclick="abrirModalRevision('<?= $ent_id ?>')">
                                    Revisar Entrega
                                </button>
                            </div>
                        <?php else: ?>
                            <div class="nota-display">
                                <div class="nota-valor">
                                    <?= number_format($entrega['revision']['nota'], 1) ?>
                                </div>
                                <div class="nota-label">Calificación</div>
                            </div>
                            
                            <?php if (!empty($entrega['revision']['retroalimentacion'])): ?>
                                <div class="retroalimentacion-display">
                                    <strong>Retroalimentación:</strong><br>
                                    <?= nl2br(htmlspecialchars($entrega['revision']['retroalimentacion'])) ?>
                                </div>
                            <?php endif; ?>
                            
                            <div class="entrega-acciones" style="margin-top: 15px;">
                                <button class="btn-ver-revision" onclick="abrirModalRevision('<?= $ent_id ?>')">
                                    Editar Revisión
                                </button>
                            </div>
                        <?php endif; ?>
                    </div>
                <?php endforeach; ?>
            </div>
        <?php endif; ?>
    </div>
    
    <!-- Modal de Revisión -->
    <div id="modalRevision" class="modal">
        <div class="modal-content">
            <div class="modal-header">
                <h3 class="modal-title" id="modal-title">Revisar Entrega</h3>
                <button class="modal-close" onclick="cerrarModal()">&times;</button>
            </div>
            
            <form method="POST" id="form-revision">
                <div class="modal-body">
                    <input type="hidden" name="csrf_token" value="<?= generarTokenCSRF() ?>">
                    <input type="hidden" name="entrega_id" id="modal-entrega-id">
                    
                    <div class="form-info" id="modal-info">
                        <!-- Se llena dinámicamente -->
                    </div>
                    
                    <div class="form-group">
                        <label class="form-label">Calificación <span id="modal-escala"></span></label>
                        <input type="number" name="nota" id="modal-nota" class="form-input" 
                               step="0.1" required>
                    </div>
                    
                    <div class="form-group">
                        <label class="form-label">Retroalimentación</label>
                        <textarea name="retroalimentacion" id="modal-retroalimentacion" 
                                  class="form-input" 
                                  placeholder="Escribe comentarios, sugerencias y retroalimentación para el estudiante..."></textarea>
                    </div>
                </div>
                
                <div class="modal-footer">
                    <button type="button" class="btn-modal btn-cancel" onclick="cerrarModal()">Cancelar</button>
                    <button type="submit" name="revisar" class="btn-modal btn-submit">Guardar Revisión</button>
                </div>
            </form>
        </div>
    </div>
    
    <script>
        const entregas = <?= json_encode($entregas_filtradas) ?>;
        const actividades = <?= json_encode($mis_actividades) ?>;
        const estudiantes = <?= json_encode($estudiantes_db) ?>;
        
        function aplicarFiltros() {
            const actividad = document.getElementById('filtro-actividad').value;
            const estado = document.getElementById('filtro-estado').value;
            
            let url = 'revisar.php?';
            if (actividad) url += 'actividad=' + actividad + '&';
            if (estado) url += 'estado=' + estado;
            
            window.location.href = url;
        }
        
        function abrirModalRevision(entregaId) {
            const entrega = entregas[entregaId];
            const actividad = actividades[entrega.actividad_id];
            const estudiante = estudiantes[entrega.estudiante_rut];
            
            // Llenar información
            document.getElementById('modal-entrega-id').value = entregaId;
            document.getElementById('modal-nota').value = entrega.revision.nota || '';
            document.getElementById('modal-retroalimentacion').value = entrega.revision.retroalimentacion || '';
            
            // Configurar rango de nota según escala
            const notaInput = document.getElementById('modal-nota');
            const escalaSpan = document.getElementById('modal-escala');
            
            if (actividad.evaluacion.escala === '1.0-7.0') {
                notaInput.min = 1.0;
                notaInput.max = 7.0;
                escalaSpan.textContent = '(1.0 - 7.0)';
            } else if (actividad.evaluacion.escala === '0-100') {
                notaInput.min = 0;
                notaInput.max = 100;
                notaInput.step = 1;
                escalaSpan.textContent = '(0 - 100)';
            } else {
                notaInput.type = 'text';
                escalaSpan.textContent = '(A - F)';
            }
            
            // Información de la entrega
            const infoDiv = document.getElementById('modal-info');
            const fecha = new Date(entrega.timestamp);
            
            infoDiv.innerHTML = `
                <div class="info-grid">
                    <div class="info-item">
                        <span class="info-item-label">Estudiante</span>
                        <span class="info-item-value">${estudiante.nombre}</span>
                    </div>
                    <div class="info-item">
                        <span class="info-item-label">RUT</span>
                        <span class="info-item-value">${estudiante.rut}</span>
                    </div>
                    <div class="info-item">
                        <span class="info-item-label">Actividad</span>
                        <span class="info-item-value">${actividad.info_basica.nombre}</span>
                    </div>
                    <div class="info-item">
                        <span class="info-item-label">Fecha Entrega</span>
                        <span class="info-item-value">${fecha.toLocaleDateString('es-CL')} ${fecha.toLocaleTimeString('es-CL', {hour: '2-digit', minute: '2-digit'})}</span>
                    </div>
                </div>
            `;
            
            document.getElementById('modalRevision').classList.add('active');
        }
        
        function cerrarModal() {
            document.getElementById('modalRevision').classList.remove('active');
        }
        
        // Cerrar modal al hacer clic fuera
        document.getElementById('modalRevision').addEventListener('click', function(e) {
            if (e.target === this) {
                cerrarModal();
            }
        });
    </script>
</body>
</html>