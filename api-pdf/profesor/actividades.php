<?php
/**
 * profesor/actividades.php - Gestión de actividades del profesor
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

// Procesar acciones
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $action = $_POST['action'] ?? '';
    
    $actividades = cargarJSON(ACTIVIDADES_FILE);
    $profesores = cargarJSON(PROFESORES_FILE);
    $profesor = $profesores[$rut];
    
    if ($action === 'crear') {
        // Verificar cuota
        if ($profesor['actividades_usadas'] >= $profesor['cuota_actividades']) {
            $mensaje = 'Has alcanzado tu cuota máxima de actividades';
            $tipo_mensaje = 'error';
        } else {
            $id = generarID('ACT');
            $config = cargarJSON(CONFIG_FILE);
            
            $actividades[$id] = [
                'id' => $id,
                'profesor_rut' => $rut,
                'info_basica' => [
                    'nombre' => trim($_POST['nombre']),
                    'tipo_estudio' => $_POST['tipo_estudio'],
                    'tipo_sesion' => $_POST['tipo_sesion'] ?? 'real',
                    'descripcion' => trim($_POST['descripcion']),
                    'fecha_inicio' => $_POST['fecha_inicio'],
                    'fecha_cierre' => $_POST['fecha_cierre'],
                    'created' => formatearFecha()
                ],
                'material_pedagogico' => [
                    'objetivos' => array_filter(array_map('trim', explode("\n", $_POST['objetivos'] ?? ''))),
                    'protocolo' => trim($_POST['protocolo'] ?? ''),
                    'guia_laboratorio' => null,
                    'material_complementario' => [],
                    'criterios_analisis' => trim($_POST['criterios_analisis'] ?? '')
                ],
                'evaluacion' => [
                    'es_calificada' => isset($_POST['es_calificada']),
                    'permite_retroalimentacion' => isset($_POST['permite_retroalimentacion']),
                    'ponderacion' => floatval($_POST['ponderacion'] ?? 0),
                    'escala' => $_POST['escala'] ?? '1.0-7.0',
                    'rubrica' => null,
                    'criterios' => []
                ],
                'configuracion' => [
                    'cuota_estudios' => [
                        'espirometria' => intval($_POST['cuota_espirometria'] ?? $config['cuotas_default']['estudios_por_tipo']),
                        'ecg' => intval($_POST['cuota_ecg'] ?? $config['cuotas_default']['estudios_por_tipo']),
                        'emg' => intval($_POST['cuota_emg'] ?? $config['cuotas_default']['estudios_por_tipo']),
                        'eeg' => intval($_POST['cuota_eeg'] ?? $config['cuotas_default']['estudios_por_tipo'])
                    ],
                    'permite_reentregas' => isset($_POST['permite_reentregas']),
                    'visibilidad' => $_POST['visibilidad'] ?? 'privada',
                    'password_hash' => password_hash($_POST['password'], PASSWORD_DEFAULT),
                    'estudiantes_inscritos' => []
                ],
                'estadisticas' => [
                    'total_estudiantes' => 0,
                    'entregas_realizadas' => 0,
                    'entregas_pendientes' => 0,
                    'entregas_revisadas' => 0,
                    'promedio_nota' => 0
                ]
            ];
            
            guardarJSON(ACTIVIDADES_FILE, $actividades);
            
            // Actualizar cuota del profesor
            $profesores[$rut]['actividades_usadas']++;
            guardarJSON(PROFESORES_FILE, $profesores);
            
            // Crear carpeta para materiales y entregas
            $actividad_dir = UPLOADS_PATH . '/' . $id;
            mkdir($actividad_dir . '/materiales', 0755, true);
            mkdir($actividad_dir . '/entregas', 0755, true);
            
            $mensaje = 'Actividad creada exitosamente';
            $tipo_mensaje = 'success';
        }
    }
    
    elseif ($action === 'editar') {
        $id = $_POST['id'];
        
        if (isset($actividades[$id]) && $actividades[$id]['profesor_rut'] === $rut) {
            $actividades[$id]['info_basica']['nombre'] = trim($_POST['nombre']);
            $actividades[$id]['info_basica']['descripcion'] = trim($_POST['descripcion']);
            $actividades[$id]['info_basica']['fecha_cierre'] = $_POST['fecha_cierre'];
            
            $actividades[$id]['material_pedagogico']['objetivos'] = array_filter(array_map('trim', explode("\n", $_POST['objetivos'] ?? '')));
            $actividades[$id]['material_pedagogico']['protocolo'] = trim($_POST['protocolo'] ?? '');
            $actividades[$id]['material_pedagogico']['criterios_analisis'] = trim($_POST['criterios_analisis'] ?? '');
            
            $actividades[$id]['evaluacion']['es_calificada'] = isset($_POST['es_calificada']);
            $actividades[$id]['evaluacion']['permite_retroalimentacion'] = isset($_POST['permite_retroalimentacion']);
            $actividades[$id]['evaluacion']['ponderacion'] = floatval($_POST['ponderacion'] ?? 0);
            
            $actividades[$id]['configuracion']['permite_reentregas'] = isset($_POST['permite_reentregas']);
            
            if (!empty($_POST['password'])) {
                $actividades[$id]['configuracion']['password_hash'] = password_hash($_POST['password'], PASSWORD_DEFAULT);
            }
            
            guardarJSON(ACTIVIDADES_FILE, $actividades);
            
            $mensaje = 'Actividad actualizada exitosamente';
            $tipo_mensaje = 'success';
        }
    }
    
    elseif ($action === 'eliminar') {
        $id = $_POST['id'];
        
        if (isset($actividades[$id]) && $actividades[$id]['profesor_rut'] === $rut) {
            unset($actividades[$id]);
            guardarJSON(ACTIVIDADES_FILE, $actividades);
            
            // Reducir cuota usada
            $profesores[$rut]['actividades_usadas']--;
            guardarJSON(PROFESORES_FILE, $profesores);
            
            $mensaje = 'Actividad eliminada exitosamente';
            $tipo_mensaje = 'success';
        }
    }
}

// Cargar actividades del profesor
$todas_actividades = cargarJSON(ACTIVIDADES_FILE);
$mis_actividades = array_filter($todas_actividades, fn($a) => $a['profesor_rut'] === $rut);

$profesores = cargarJSON(PROFESORES_FILE);
$profesor = $profesores[$rut];
$config = cargarJSON(CONFIG_FILE);
?>
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Mis Actividades - FisioaccessPC</title>
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
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        
        .header {
            background: rgba(255, 255, 255, 0.15);
            backdrop-filter: blur(10px);
            border-radius: 16px;
            border: 1px solid rgba(255, 255, 255, 0.3);
            padding: 25px;
            margin-bottom: 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        h1 {
            color: white;
            font-size: 28px;
        }
        
        .cuota-info {
            color: white;
            font-size: 14px;
            background: rgba(255, 255, 255, 0.1);
            padding: 10px 15px;
            border-radius: 10px;
        }
        
        .btn {
            padding: 10px 20px;
            border: none;
            border-radius: 10px;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            text-decoration: none;
            display: inline-block;
            transition: all 0.3s;
        }
        
        .btn-primary {
            background: white;
            color: #7c3aed;
        }
        
        .btn-primary:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(255, 255, 255, 0.3);
        }
        
        .btn-primary:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }
        
        .btn-secondary {
            background: rgba(255, 255, 255, 0.2);
            color: white;
            border: 1px solid rgba(255, 255, 255, 0.3);
        }
        
        .btn-danger {
            background: rgba(239, 68, 68, 0.3);
            color: white;
            border: 1px solid rgba(239, 68, 68, 0.5);
        }
        
        .btn-small {
            padding: 6px 12px;
            font-size: 12px;
        }
        
        .mensaje {
            background: rgba(255, 255, 255, 0.15);
            backdrop-filter: blur(10px);
            border-radius: 12px;
            padding: 15px;
            margin-bottom: 20px;
            color: white;
        }
        
        .mensaje.success {
            background: rgba(34, 197, 94, 0.3);
            border: 1px solid rgba(34, 197, 94, 0.5);
        }
        
        .mensaje.error {
            background: rgba(239, 68, 68, 0.3);
            border: 1px solid rgba(239, 68, 68, 0.5);
        }
        
        .card {
            background: rgba(255, 255, 255, 0.15);
            backdrop-filter: blur(10px);
            border-radius: 16px;
            border: 1px solid rgba(255, 255, 255, 0.3);
            padding: 25px;
            margin-bottom: 20px;
        }
        
        .actividades-grid {
            display: grid;
            gap: 15px;
        }
        
        .actividad-card {
            background: rgba(255, 255, 255, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 12px;
            padding: 20px;
            color: white;
        }
        
        .actividad-header {
            display: flex;
            justify-content: space-between;
            align-items: start;
            margin-bottom: 15px;
        }
        
        .actividad-titulo {
            font-size: 20px;
            font-weight: 600;
            margin-bottom: 5px;
        }
        
        .actividad-id {
            font-size: 12px;
            opacity: 0.8;
        }
        
        .actividad-info {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 10px;
            margin-bottom: 15px;
            font-size: 14px;
        }
        
        .actividad-actions {
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
        }
        
        .badge {
            display: inline-block;
            padding: 4px 10px;
            border-radius: 6px;
            font-size: 12px;
            font-weight: 600;
        }
        
        .badge-tipo {
            background: rgba(59, 130, 246, 0.3);
            border: 1px solid rgba(59, 130, 246, 0.5);
        }
        
        .badge-calificada {
            background: rgba(34, 197, 94, 0.3);
            border: 1px solid rgba(34, 197, 94, 0.5);
        }
        
        .modal {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.5);
            z-index: 1000;
            overflow-y: auto;
            padding: 20px;
        }
        
        .modal-content {
            background: rgba(124, 58, 237, 0.95);
            backdrop-filter: blur(10px);
            border-radius: 16px;
            border: 1px solid rgba(255, 255, 255, 0.3);
            padding: 30px;
            max-width: 800px;
            margin: 50px auto;
        }
        
        .modal-header {
            color: white;
            margin-bottom: 25px;
            font-size: 24px;
        }
        
        .form-group {
            margin-bottom: 15px;
        }
        
        label {
            display: block;
            color: white;
            margin-bottom: 6px;
            font-weight: 500;
            font-size: 14px;
        }
        
        input, select, textarea {
            width: 100%;
            padding: 10px;
            border: 1px solid rgba(255, 255, 255, 0.3);
            border-radius: 10px;
            background: rgba(255, 255, 255, 0.1);
            color: white;
            font-size: 14px;
            font-family: inherit;
        }
        
        textarea {
            resize: vertical;
            min-height: 80px;
        }
        
        input::placeholder, textarea::placeholder {
            color: rgba(255, 255, 255, 0.6);
        }
        
        input:focus, select:focus, textarea:focus {
            outline: none;
            border-color: rgba(255, 255, 255, 0.6);
            background: rgba(255, 255, 255, 0.15);
        }
        
        .form-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 15px;
        }
        
        .form-full {
            grid-column: 1 / -1;
        }
        
        .checkbox-group {
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        .checkbox-group input[type="checkbox"] {
            width: auto;
        }
        
        .help-text {
            font-size: 12px;
            color: rgba(255, 255, 255, 0.8);
            margin-top: 4px;
        }
    </style>
</head>
<body>
    <div class="navbar">
        <div class="navbar-brand">🫁 FisioaccessPC</div>
        <a href="dashboard.php" class="btn btn-secondary btn-small">← Volver al Dashboard</a>
    </div>
    
    <div class="container">
        <div class="header">
            <div>
                <h1>📚 Mis Actividades</h1>
                <div class="cuota-info">
                    📊 Cuota: <?= $profesor['actividades_usadas'] ?>/<?= $profesor['cuota_actividades'] ?> actividades usadas
                </div>
            </div>
            <button class="btn btn-primary" onclick="abrirModal()" 
                    <?= $profesor['actividades_usadas'] >= $profesor['cuota_actividades'] ? 'disabled' : '' ?>>
                + Nueva Actividad
            </button>
        </div>
        
        <?php if ($mensaje): ?>
            <div class="mensaje <?= $tipo_mensaje ?>">
                <?= htmlspecialchars($mensaje) ?>
            </div>
        <?php endif; ?>
        
        <div class="card">
            <?php if (empty($mis_actividades)): ?>
                <p style="color: white; text-align: center; opacity: 0.8;">
                    No tienes actividades creadas. Crea tu primera actividad usando el botón superior.
                </p>
            <?php else: ?>
                <div class="actividades-grid">
                    <?php foreach ($mis_actividades as $id => $act): ?>
                        <div class="actividad-card">
                            <div class="actividad-header">
                                <div>
                                    <div class="actividad-titulo"><?= htmlspecialchars($act['info_basica']['nombre']) ?></div>
                                    <div class="actividad-id">ID: <?= $id ?></div>
                                </div>
                                <div style="display: flex; gap: 5px;">
                                    <span class="badge badge-tipo">
                                        <?= TIPOS_ESTUDIO[$act['info_basica']['tipo_estudio']] ?>
                                    </span>
                                    <?php if ($act['evaluacion']['es_calificada']): ?>
                                        <span class="badge badge-calificada">✅ Calificada</span>
                                    <?php endif; ?>
                                </div>
                            </div>
                            
                            <div class="actividad-info">
                                <div>📅 Cierre: <?= date('d/m/Y', strtotime($act['info_basica']['fecha_cierre'])) ?></div>
                                <div>👥 Estudiantes: <?= $act['estadisticas']['total_estudiantes'] ?></div>
                                <div>📊 Entregas: <?= $act['estadisticas']['entregas_realizadas'] ?></div>
                                <div>⏳ Pendientes: <?= $act['estadisticas']['entregas_pendientes'] ?></div>
                            </div>
                            
                            <div style="margin-bottom: 15px; font-size: 14px; opacity: 0.9;">
                                <?= htmlspecialchars(substr($act['info_basica']['descripcion'], 0, 150)) ?>...
                            </div>
                            
                            <div class="actividad-actions">
                                <button class="btn btn-secondary btn-small" onclick='editarActividad(<?= json_encode($act) ?>)'>
                                    ✏️ Editar
                                </button>
                                <a href="materiales.php?id=<?= $id ?>" class="btn btn-secondary btn-small">
                                    📎 Material
                                </a>
                                <a href="estudiantes.php?actividad=<?= $id ?>" class="btn btn-secondary btn-small">
                                    👥 Estudiantes
                                </a>
                                <form method="POST" style="display: inline;" onsubmit="return confirm('¿Eliminar esta actividad?')">
                                    <input type="hidden" name="action" value="eliminar">
                                    <input type="hidden" name="id" value="<?= $id ?>">
                                    <button type="submit" class="btn btn-danger btn-small">🗑️ Eliminar</button>
                                </form>
                            </div>
                        </div>
                    <?php endforeach; ?>
                </div>
            <?php endif; ?>
        </div>
    </div>
    
    <!-- Modal Crear/Editar -->
    <div id="modalActividad" class="modal">
        <div class="modal-content">
            <h2 class="modal-header" id="modal-titulo">Nueva Actividad</h2>
            
            <!-- Leyenda versión de prueba -->
            <div style="background: rgba(251, 191, 36, 0.2); border: 1px solid rgba(251, 191, 36, 0.5); padding: 10px; border-radius: 8px; margin-bottom: 20px; color: #fbbf24; font-size: 13px; text-align: center;">
                ⚠️ <strong>Versión de Prueba</strong> - Asistente IA en desarrollo
            </div>
            
            <!-- Botones de IA -->
            <div style="display: flex; gap: 10px; margin-bottom: 20px;">
                <button type="button" class="btn btn-secondary" onclick="generarPromptIA()" style="flex: 1;">
                    🤖 Generar Prompt IA
                </button>
                <button type="button" class="btn btn-secondary" onclick="abrirModalPegarIA()" style="flex: 1;">
                    📋 Pegar Respuesta IA
                </button>
            </div>
            
            <form method="POST" id="formActividad">
                <input type="hidden" name="action" id="form-action" value="crear">
                <input type="hidden" name="id" id="form-id">
                
                <div class="form-grid">
                    <div class="form-full">
                        <label>Nombre de la Actividad *</label>
                        <input type="text" name="nombre" id="form-nombre" 
                               placeholder="Práctico 3: Análisis de Espirometría" required>
                    </div>
                    
                    <div>
                        <label>Tipo de Estudio *</label>
                        <select name="tipo_estudio" id="form-tipo" required>
                            <?php foreach (TIPOS_ESTUDIO as $key => $value): ?>
                                <option value="<?= $key ?>"><?= $value ?></option>
                            <?php endforeach; ?>
                        </select>
                    </div>
                    
                    <div>
                        <label>Tipo de Sesión *</label>
                        <select name="tipo_sesion" id="form-sesion">
                            <?php foreach (TIPOS_SESION as $key => $value): ?>
                                <option value="<?= $key ?>" <?= $key === 'real' ? 'selected' : '' ?>><?= $value ?></option>
                            <?php endforeach; ?>
                        </select>
                    </div>
                    
                    <div>
                        <label>Fecha de Inicio *</label>
                        <input type="datetime-local" name="fecha_inicio" id="form-inicio" required>
                    </div>
                    
                    <div>
                        <label>Fecha de Cierre *</label>
                        <input type="datetime-local" name="fecha_cierre" id="form-cierre" required>
                    </div>
                    
                    <div class="form-full">
                        <label>Descripción *</label>
                        <textarea name="descripcion" id="form-descripcion" 
                                  placeholder="Análisis comparativo de función pulmonar..." required></textarea>
                    </div>
                    
                    <div class="form-full">
                        <label>Objetivos de Aprendizaje (uno por línea)</label>
                        <textarea name="objetivos" id="form-objetivos" 
                                  placeholder="Comprender los parámetros espirométricos..."></textarea>
                    </div>
                    
                    <div class="form-full">
                        <label>Protocolo / Instrucciones</label>
                        <textarea name="protocolo" id="form-protocolo" 
                                  placeholder="1. Calibrar equipo..."></textarea>
                    </div>
                    
                    <div class="form-full">
                        <label>Criterios de Análisis</label>
                        <textarea name="criterios_analisis" id="form-criterios" 
                                  placeholder="Comparar valores pre y post ejercicio..."></textarea>
                    </div>
                    
                    <div class="form-full" style="border-top: 1px solid rgba(255,255,255,0.2); padding-top: 15px; margin-top: 10px;">
                        <h3 style="color: white; margin-bottom: 15px; font-size: 16px;">Evaluación</h3>
                    </div>
                    
                    <div class="form-full">
                        <div class="checkbox-group">
                            <input type="checkbox" name="es_calificada" id="form-calificada">
                            <label style="margin: 0;">Esta actividad será calificada</label>
                        </div>
                    </div>
                    
                    <div class="form-full">
                        <div class="checkbox-group">
                            <input type="checkbox" name="permite_retroalimentacion" id="form-retro" checked>
                            <label style="margin: 0;">Permitir retroalimentación</label>
                        </div>
                    </div>
                    
                    <div>
                        <label>Ponderación (%)</label>
                        <input type="number" name="ponderacion" id="form-ponderacion" 
                               value="0" min="0" max="100" step="0.1">
                    </div>
                    
                    <div>
                        <label>Escala de Calificación</label>
                        <select name="escala" id="form-escala">
                            <option value="1.0-7.0">1.0 - 7.0</option>
                            <option value="0-100">0 - 100</option>
                            <option value="A-F">A - F</option>
                        </select>
                    </div>
                    
                    <div class="form-full" style="border-top: 1px solid rgba(255,255,255,0.2); padding-top: 15px; margin-top: 10px;">
                        <h3 style="color: white; margin-bottom: 15px; font-size: 16px;">Configuración</h3>
                    </div>
                    
                    <div>
                        <label>Cuota Espirometría</label>
                        <input type="number" name="cuota_espirometria" value="<?= $config['cuotas_default']['estudios_por_tipo'] ?>" min="0" max="10">
                    </div>
                    
                    <div>
                        <label>Cuota ECG</label>
                        <input type="number" name="cuota_ecg" value="<?= $config['cuotas_default']['estudios_por_tipo'] ?>" min="0" max="10">
                    </div>
                    
                    <div>
                        <label>Cuota EMG</label>
                        <input type="number" name="cuota_emg" value="<?= $config['cuotas_default']['estudios_por_tipo'] ?>" min="0" max="10">
                    </div>
                    
                    <div>
                        <label>Cuota EEG</label>
                        <input type="number" name="cuota_eeg" value="<?= $config['cuotas_default']['estudios_por_tipo'] ?>" min="0" max="10">
                    </div>
                    
                    <div class="form-full">
                        <div class="checkbox-group">
                            <input type="checkbox" name="permite_reentregas" id="form-reentregas">
                            <label style="margin: 0;">Permitir reentregas</label>
                        </div>
                    </div>
                    
                    <div>
                        <label>Visibilidad</label>
                        <select name="visibilidad" id="form-visibilidad">
                            <option value="privada">Privada (solo estudiantes inscritos)</option>
                            <option value="publica">Pública (todos pueden ver)</option>
                        </select>
                    </div>
                    
                    <div>
                        <label>Contraseña de Acceso <span id="password-label">*</span></label>
                        <input type="password" name="password" id="form-password" placeholder="••••••••">
                        <div class="help-text" id="password-hint">Los estudiantes necesitarán esta contraseña</div>
                    </div>
                </div>
                
                <div style="display: flex; gap: 10px; margin-top: 25px;">
                    <button type="submit" class="btn btn-primary" style="flex: 1;">Guardar Actividad</button>
                    <button type="button" class="btn btn-secondary" style="flex: 1;" onclick="cerrarModal()">Cancelar</button>
                </div>
            </form>
        </div>
    </div>
    
    <!-- Modal para pegar respuesta IA -->
    <div id="modalPegarIA" class="modal">
        <div class="modal-content" style="max-width: 600px;">
            <h2 class="modal-header">📋 Pegar Respuesta del LLM</h2>
            <p style="color: white; margin-bottom: 15px; opacity: 0.9;">
                Pega aquí la respuesta completa que te dio tu LLM (Claude, ChatGPT, etc.)
            </p>
            <textarea id="textarea-respuesta-ia" 
                      style="width: 100%; min-height: 300px; padding: 12px; border-radius: 8px; 
                             background: rgba(255,255,255,0.1); color: white; border: 1px solid rgba(255,255,255,0.3);
                             font-family: monospace; font-size: 13px;"
                      placeholder='Pega aquí todo el texto que te dio el LLM, incluyendo:
```json
{
  "nombre": "...",
  "descripcion": "...",
  ...
}
```'></textarea>
            <div id="error-parse" style="color: #ef4444; margin-top: 10px; display: none;"></div>
            <div style="display: flex; gap: 10px; margin-top: 15px;">
                <button type="button" class="btn btn-primary" onclick="procesarRespuestaIA()" style="flex: 1;">
                    Llenar Formulario
                </button>
                <button type="button" class="btn btn-secondary" onclick="cerrarModalIA()" style="flex: 1;">
                    Cancelar
                </button>
            </div>
        </div>
    </div>
    
    <script>
        // ============================================
        // FUNCIONES DEL ASISTENTE IA
        // ============================================
        
        function generarPromptIA() {
            const form = document.getElementById('formActividad');
            const formData = new FormData(form);
            
            // Recopilar campos llenos y vacíos
            const camposLlenos = {};
            const camposVacios = [];
            
            const campos = {
                'nombre': 'Nombre de la Actividad',
                'tipo_estudio': 'Tipo de Estudio',
                'tipo_sesion': 'Tipo de Sesión',
                'descripcion': 'Descripción',
                'fecha_inicio': 'Fecha de Inicio',
                'fecha_cierre': 'Fecha de Cierre',
                'objetivos': 'Objetivos de Aprendizaje',
                'protocolo': 'Protocolo/Instrucciones',
                'criterios_analisis': 'Criterios de Análisis',
                'ponderacion': 'Ponderación (%)',
                'escala': 'Escala de Calificación'
            };
            
            for (const [key, label] of Object.entries(campos)) {
                const valor = formData.get(key);
                if (valor && valor.trim() !== '') {
                    camposLlenos[label] = valor;
                } else {
                    camposVacios.push(label);
                }
            }
            
            // Generar el prompt
            let prompt = `Soy profesor de fisiología y necesito ayuda para completar la información de una actividad práctica de laboratorio.

CONTEXTO - Campos ya completados:
${Object.entries(camposLlenos).map(([k, v]) => `- ${k}: ${v}`).join('\n')}

NECESITO QUE COMPLETES ESTOS CAMPOS:
${camposVacios.map(c => `- ${c}`).join('\n')}

INSTRUCCIONES IMPORTANTES:
1. Responde SOLO con un objeto JSON
2. NO agregues texto explicativo antes o después
3. Puedes envolver el JSON en \`\`\`json ... \`\`\` si quieres
4. Genera contenido apropiado para una actividad universitaria de fisiología
5. Los objetivos deben ser una lista separada por saltos de línea
6. El protocolo debe tener pasos numerados

FORMATO DE RESPUESTA REQUERIDO:
\`\`\`json
{
  "nombre": "Nombre descriptivo de la actividad",
  "tipo_estudio": "espirometria|ecg|emg|eeg",
  "tipo_sesion": "real|simulado_con_equipo|simulado_sin_equipo",
  "descripcion": "Descripción detallada de 2-3 oraciones",
  "objetivos": "Objetivo 1\\nObjetivo 2\\nObjetivo 3",
  "protocolo": "1. Paso uno\\n2. Paso dos\\n3. Paso tres",
  "criterios_analisis": "Criterios para analizar los resultados",
  "ponderacion": 15.0,
  "escala": "1.0-7.0"
}
\`\`\`

Por favor genera el JSON completo ahora:`;

            // Copiar al portapapeles
            navigator.clipboard.writeText(prompt).then(() => {
                alert('✅ Prompt copiado al portapapeles!\n\n1. Pégalo en tu LLM favorito (Claude, ChatGPT, etc.)\n2. Copia la respuesta completa\n3. Usa el botón "Pegar Respuesta IA"');
            }).catch(() => {
                // Fallback: mostrar en un textarea
                const textarea = document.createElement('textarea');
                textarea.value = prompt;
                textarea.style.cssText = 'position:fixed;top:50%;left:50%;transform:translate(-50%,-50%);width:80%;height:80%;z-index:10000;padding:20px;background:white;color:black;border:2px solid #333;';
                document.body.appendChild(textarea);
                textarea.select();
                alert('Copia este prompt manualmente (Ctrl+C) y cierra esta ventana');
                textarea.addEventListener('blur', () => textarea.remove());
            });
        }
        
        function abrirModalPegarIA() {
            document.getElementById('modalPegarIA').style.display = 'block';
            document.getElementById('textarea-respuesta-ia').value = '';
            document.getElementById('error-parse').style.display = 'none';
        }
        
        function cerrarModalIA() {
            document.getElementById('modalPegarIA').style.display = 'none';
        }
        
        function extractJSON(text) {
            // 1. Buscar bloques de código markdown con ```json
            let match = text.match(/```(?:json)?\s*(\{[\s\S]*?\})\s*```/);
            if (match) return match[1];
            
            // 2. Buscar bloques de código markdown sin especificar lenguaje
            match = text.match(/```\s*(\{[\s\S]*?\})\s*```/);
            if (match) return match[1];
            
            // 3. Buscar JSON puro (primeras llaves hasta las últimas)
            match = text.match(/\{[\s\S]*\}/);
            if (match) return match[0];
            
            return null;
        }
        
        function procesarRespuestaIA() {
            const textarea = document.getElementById('textarea-respuesta-ia');
            const errorDiv = document.getElementById('error-parse');
            const input = textarea.value.trim();
            
            if (!input) {
                errorDiv.textContent = 'Por favor pega la respuesta del LLM';
                errorDiv.style.display = 'block';
                return;
            }
            
            try {
                // Extraer JSON
                const jsonStr = extractJSON(input);
                if (!jsonStr) {
                    throw new Error('No se encontró ningún JSON válido en el texto');
                }
                
                // Parsear JSON
                const data = JSON.parse(jsonStr);
                
                // Llenar formulario
                if (data.nombre) document.getElementById('form-nombre').value = data.nombre;
                if (data.tipo_estudio) document.getElementById('form-tipo').value = data.tipo_estudio;
                if (data.tipo_sesion) document.getElementById('form-sesion').value = data.tipo_sesion;
                if (data.descripcion) document.getElementById('form-descripcion').value = data.descripcion;
                if (data.objetivos) document.getElementById('form-objetivos').value = data.objetivos;
                if (data.protocolo) document.getElementById('form-protocolo').value = data.protocolo;
                if (data.criterios_analisis) document.getElementById('form-criterios').value = data.criterios_analisis;
                if (data.ponderacion !== undefined) document.getElementById('form-ponderacion').value = data.ponderacion;
                if (data.escala) document.getElementById('form-escala').value = data.escala;
                
                // Cerrar modal y mostrar éxito
                cerrarModalIA();
                alert('✅ Formulario completado exitosamente!\n\nRevisa los campos y ajusta si es necesario.');
                
            } catch (error) {
                errorDiv.textContent = '❌ Error: ' + error.message + '\n\nAsegúrate de copiar la respuesta completa del LLM, incluyendo el JSON.';
                errorDiv.style.display = 'block';
                console.error('Error al parsear:', error);
            }
        }
        
        // ============================================
        // FUNCIONES ORIGINALES DEL FORMULARIO
        // ============================================
        
        function abrirModal() {
            document.getElementById('modal-titulo').textContent = 'Nueva Actividad';
            document.getElementById('form-action').value = 'crear';
            document.getElementById('formActividad').reset();
            document.getElementById('form-password').required = true;
            document.getElementById('password-label').textContent = '*';
            document.getElementById('password-hint').textContent = 'Los estudiantes necesitarán esta contraseña';
            
            // Fecha actual
            const now = new Date();
            now.setMinutes(now.getMinutes() - now.getTimezoneOffset());
            document.getElementById('form-inicio').value = now.toISOString().slice(0,16);
            
            // Fecha cierre (1 semana después)
            const cierre = new Date(now.getTime() + 7 * 24 * 60 * 60 * 1000);
            document.getElementById('form-cierre').value = cierre.toISOString().slice(0,16);
            
            document.getElementById('modalActividad').style.display = 'block';
        }
        
        function editarActividad(actividad) {
            document.getElementById('modal-titulo').textContent = 'Editar Actividad';
            document.getElementById('form-action').value = 'editar';
            document.getElementById('form-id').value = actividad.id;
            document.getElementById('form-nombre').value = actividad.info_basica.nombre;
            document.getElementById('form-tipo').value = actividad.info_basica.tipo_estudio;
            document.getElementById('form-sesion').value = actividad.info_basica.tipo_sesion;
            document.getElementById('form-descripcion').value = actividad.info_basica.descripcion;
            document.getElementById('form-cierre').value = actividad.info_basica.fecha_cierre.slice(0,16);
            document.getElementById('form-objetivos').value = actividad.material_pedagogico.objetivos.join('\n');
            document.getElementById('form-protocolo').value = actividad.material_pedagogico.protocolo;
            document.getElementById('form-criterios').value = actividad.material_pedagogico.criterios_analisis;
            document.getElementById('form-calificada').checked = actividad.evaluacion.es_calificada;
            document.getElementById('form-retro').checked = actividad.evaluacion.permite_retroalimentacion;
            document.getElementById('form-ponderacion').value = actividad.evaluacion.ponderacion;
            document.getElementById('form-escala').value = actividad.evaluacion.escala;
            document.getElementById('form-reentregas').checked = actividad.configuracion.permite_reentregas;
            document.getElementById('form-visibilidad').value = actividad.configuracion.visibilidad;
            
            document.getElementById('form-password').value = '';
            document.getElementById('form-password').required = false;
            document.getElementById('password-label').textContent = '(opcional)';
            document.getElementById('password-hint').textContent = 'Dejar en blanco para mantener la actual';
            
            document.getElementById('modalActividad').style.display = 'block';
        }
        
        function cerrarModal() {
            document.getElementById('modalActividad').style.display = 'none';
        }
        
        window.onclick = function(event) {
            const modal = document.getElementById('modalActividad');
            if (event.target === modal) {
                cerrarModal();
            }
        }
    </script>
</body>
</html>