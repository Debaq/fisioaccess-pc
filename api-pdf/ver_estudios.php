<?php
/**
 * ver_estudios.php - Visualización de estudios por actividad
 * 
 * Requiere autenticación
 * Muestra actividades disponibles y permite ver estudios filtrados
 */

session_start();

$dataDir = __DIR__ . '/data/';
$actividadesFile = $dataDir . 'actividades.json';

// Constantes
const TIPOS_ESTUDIO = [
    'espirometria' => 'Espirometría',
    'ecg' => 'Electrocardiograma',
    'emg' => 'Electromiografía',
    'eeg' => 'Electroencefalograma'
];

function cargarActividades() {
    global $actividadesFile;
    if (!file_exists($actividadesFile)) {
        return [];
    }
    return json_decode(file_get_contents($actividadesFile), true) ?: [];
}

function cargarEstudiosActividad($actividadId) {
    global $dataDir;
    $actividadDir = $dataDir . 'uploads/' . $actividadId . '/';
    
    if (!is_dir($actividadDir)) {
        return [];
    }
    
    $estudios = [];
    foreach (glob($actividadDir . 'metadata_*.json') as $file) {
        $data = json_decode(file_get_contents($file), true);
        if ($data) {
            $estudios[] = $data;
        }
    }
    
    // Ordenar por fecha (más recientes primero)
    usort($estudios, function($a, $b) {
        return strtotime($b['uploaded']) - strtotime($a['uploaded']);
    });
    
    return $estudios;
}

// Manejar peticiones AJAX
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    header('Content-Type: application/json');
    
    $action = $_POST['action'] ?? '';
    
    if ($action === 'get_estudios') {
        $actividadId = $_POST['actividad_id'] ?? '';
        
        if (empty($actividadId)) {
            echo json_encode(['error' => 'ID de actividad requerido']);
            exit;
        }
        
        $estudios = cargarEstudiosActividad($actividadId);
        
        echo json_encode([
            'success' => true,
            'estudios' => $estudios
        ]);
        exit;
    }
}

?>
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Ver Estudios - FisioaccessPC</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
            background: #f5f5f5;
            min-height: 100vh;
        }
        
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        
        .header-content {
            max-width: 1200px;
            margin: 0 auto;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .header h1 {
            font-size: 24px;
        }
        
        .user-info {
            display: flex;
            align-items: center;
            gap: 15px;
            font-size: 14px;
        }
        
        .container {
            max-width: 1200px;
            margin: 30px auto;
            padding: 0 20px;
        }
        
        .login-box {
            background: white;
            border-radius: 12px;
            padding: 40px;
            max-width: 500px;
            margin: 50px auto;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        }
        
        .login-box h2 {
            color: #2c3e50;
            margin-bottom: 30px;
            text-align: center;
        }
        
        .form-group {
            margin-bottom: 20px;
        }
        
        label {
            display: block;
            margin-bottom: 5px;
            color: #2c3e50;
            font-weight: 600;
        }
        
        input[type="text"],
        input[type="password"],
        select {
            width: 100%;
            padding: 12px;
            border: 1px solid #ddd;
            border-radius: 6px;
            font-size: 14px;
        }
        
        .btn {
            padding: 12px 24px;
            border: none;
            border-radius: 6px;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
        }
        
        .btn-primary {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            width: 100%;
        }
        
        .btn-primary:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
        }
        
        .btn-secondary {
            background: #e0e0e0;
            color: #2c3e50;
        }
        
        .btn-small {
            padding: 6px 12px;
            font-size: 12px;
        }
        
        .actividades-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .actividad-card {
            background: white;
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            cursor: pointer;
            transition: all 0.3s;
        }
        
        .actividad-card:hover {
            transform: translateY(-4px);
            box-shadow: 0 8px 20px rgba(0,0,0,0.15);
        }
        
        .actividad-card.selected {
            border: 2px solid #667eea;
        }
        
        .tipo-badge {
            display: inline-block;
            padding: 4px 10px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: 600;
            margin-bottom: 10px;
        }
        
        .tipo-espirometria { background: #3498db; color: white; }
        .tipo-ecg { background: #e74c3c; color: white; }
        .tipo-emg { background: #27ae60; color: white; }
        .tipo-eeg { background: #f39c12; color: white; }
        
        .actividad-card h3 {
            color: #2c3e50;
            margin-bottom: 10px;
        }
        
        .actividad-card p {
            color: #7f8c8d;
            font-size: 14px;
        }
        
        .estudios-section {
            background: white;
            border-radius: 12px;
            padding: 30px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            display: none;
        }
        
        .estudios-section.visible {
            display: block;
        }
        
        .section-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
            padding-bottom: 15px;
            border-bottom: 2px solid #e0e0e0;
        }
        
        .section-header h2 {
            color: #2c3e50;
        }
        
        .estudio-card {
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 15px;
        }
        
        .estudio-header {
            display: flex;
            justify-content: space-between;
            align-items: start;
            margin-bottom: 15px;
        }
        
        .estudio-title {
            font-size: 18px;
            font-weight: 600;
            color: #2c3e50;
        }
        
        .estudio-info {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 10px;
            margin-bottom: 15px;
            font-size: 14px;
        }
        
        .info-label {
            color: #7f8c8d;
            font-weight: 500;
        }
        
        .estudio-actions {
            display: flex;
            gap: 10px;
        }
        
        .btn-pdf {
            background: #e74c3c;
            color: white;
        }
        
        .btn-raw {
            background: #27ae60;
            color: white;
        }
        
        .empty-state {
            text-align: center;
            padding: 60px 20px;
            color: #7f8c8d;
        }
        
        .empty-state-icon {
            font-size: 48px;
            margin-bottom: 15px;
        }
        
        .hidden {
            display: none;
        }
        
        .stats {
            display: flex;
            gap: 20px;
            margin-bottom: 20px;
        }
        
        .stat-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 15px 20px;
            border-radius: 8px;
            flex: 1;
        }
        
        .stat-value {
            font-size: 32px;
            font-weight: 700;
        }
        
        .stat-label {
            font-size: 14px;
            opacity: 0.9;
        }
    </style>
</head>
<body>
    <!-- Header -->
    <div class="header">
        <div class="header-content">
            <h1>📊 Ver Estudios</h1>
            <div class="user-info">
                <span id="user-name"></span>
                <a href="actividades.php" id="btn-gestionar" class="btn btn-secondary btn-small" style="text-decoration: none; display: none;">📚 Gestionar Actividades</a>
                <button class="btn btn-secondary btn-small" onclick="cerrarSesion()">Cerrar Sesión</button>
                <a href="index.html" class="btn btn-secondary btn-small" style="text-decoration: none;">← Inicio</a>
            </div>
        </div>
    </div>
    
    <!-- Login Box -->
    <div id="login-box" class="login-box">
        <h2>🔐 Iniciar Sesión</h2>
        <form onsubmit="iniciarSesion(event)">
            <div class="form-group">
                <label for="rut">RUT</label>
                <input type="text" id="rut" name="rut" placeholder="12345678-9" required>
            </div>
            
            <div class="form-group">
                <label for="nombre">Nombre</label>
                <input type="text" id="nombre" name="nombre" placeholder="Tu nombre completo" required>
            </div>
            
            <div class="form-group">
                <label for="tipo">Tipo de Usuario</label>
                <select id="tipo" name="tipo" onchange="togglePasswordField()">
                    <option value="estudiante">Estudiante</option>
                    <option value="profesor">Profesor</option>
                </select>
            </div>
            
            <div class="form-group hidden" id="password-group">
                <label for="password">Contraseña</label>
                <input type="password" id="password" name="password">
            </div>
            
            <button type="submit" class="btn btn-primary">Ingresar</button>
        </form>
    </div>
    
    <!-- Contenido Principal -->
    <div id="main-content" class="container hidden">
        <!-- Estadísticas -->
        <div class="stats">
            <div class="stat-card">
                <div class="stat-value" id="stat-actividades">0</div>
                <div class="stat-label">Actividades Disponibles</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="stat-estudios">0</div>
                <div class="stat-label">Estudios Totales</div>
            </div>
        </div>
        
        <!-- Actividades -->
        <h2 style="color: #2c3e50; margin-bottom: 20px;">Seleccione una Actividad</h2>
        <div id="actividades-grid" class="actividades-grid"></div>
        
        <!-- Estudios de Actividad Seleccionada -->
        <div id="estudios-section" class="estudios-section">
            <div class="section-header">
                <h2 id="actividad-nombre"></h2>
                <button class="btn btn-secondary btn-small" onclick="volverActividades()">← Volver</button>
            </div>
            <div id="estudios-container"></div>
        </div>
    </div>
    
    <script>
        let actividadesDisponibles = [];
        let actividadSeleccionada = null;
        let sesion = null;
        
        // Verificar sesión al cargar
        window.onload = function() {
            verificarSesion();
        };
        
        function togglePasswordField() {
            const tipo = document.getElementById('tipo').value;
            const passwordGroup = document.getElementById('password-group');
            const passwordInput = document.getElementById('password');
            
            if (tipo === 'profesor') {
                passwordGroup.classList.remove('hidden');
                passwordInput.required = true;
            } else {
                passwordGroup.classList.add('hidden');
                passwordInput.required = false;
            }
        }
        
        function verificarSesion() {
            fetch('auth.php?action=check')
                .then(r => r.json())
                .then(data => {
                    if (data.authenticated) {
                        sesion = data;
                        mostrarContenidoPrincipal();
                    }
                })
                .catch(() => {
                    // No hay sesión, mostrar login
                });
        }
        
        function iniciarSesion(e) {
            e.preventDefault();
            const formData = new FormData(e.target);
            formData.append('action', 'login');
            
            fetch('auth.php', {
                method: 'POST',
                body: new URLSearchParams(formData)
            })
            .then(r => r.json())
            .then(data => {
                if (data.success) {
                    sesion = data;
                    mostrarContenidoPrincipal();
                } else {
                    alert('Error: ' + data.error);
                }
            })
            .catch(err => {
                alert('Error al iniciar sesión');
                console.error(err);
            });
        }
        
        function mostrarContenidoPrincipal() {
            document.getElementById('login-box').classList.add('hidden');
            document.getElementById('main-content').classList.remove('hidden');
            document.getElementById('user-name').textContent = 
                `${sesion.nombre} (${sesion.tipo === 'profesor' ? 'Profesor' : 'Estudiante'})`;
            
            // Mostrar botón de gestionar actividades solo para profesores
            if (sesion.tipo === 'profesor') {
                document.getElementById('btn-gestionar').style.display = 'inline-block';
            }
            
            cargarActividades();
        }
        
        function cargarActividades() {
            fetch('actividades.php', {
                method: 'POST',
                headers: {'Content-Type': 'application/x-www-form-urlencoded'},
                body: 'action=listar'
            })
            .then(r => r.json())
            .then(data => {
                if (data.success) {
                    actividadesDisponibles = data.actividades;
                    
                    // Filtrar actividades según permisos
                    if (sesion.tipo === 'estudiante') {
                        actividadesDisponibles = actividadesDisponibles.filter(act => {
                            return act.publico || 
                                   act.usuarios_permitidos.includes(sesion.rut);
                        });
                    }
                    
                    mostrarActividades();
                    actualizarEstadisticas();
                }
            });
        }
        
        function mostrarActividades() {
            const grid = document.getElementById('actividades-grid');
            
            if (actividadesDisponibles.length === 0) {
                grid.innerHTML = '<div class="empty-state"><div class="empty-state-icon">📚</div><p>No hay actividades disponibles</p></div>';
                return;
            }
            
            grid.innerHTML = actividadesDisponibles.map(act => `
                <div class="actividad-card" onclick="seleccionarActividad('${act.id}')">
                    <span class="tipo-badge tipo-${act.tipo}">${getTipoNombre(act.tipo)}</span>
                    <h3>${act.nombre}</h3>
                    <p>${act.descripcion}</p>
                    <p style="font-size: 12px; margin-top: 10px;">
                        ${act.profesor} ${act.publico ? '🌐' : '🔒'}
                    </p>
                </div>
            `).join('');
        }
        
        function seleccionarActividad(id) {
            actividadSeleccionada = actividadesDisponibles.find(a => a.id === id);
            
            if (!actividadSeleccionada) return;
            
            document.getElementById('actividad-nombre').textContent = actividadSeleccionada.nombre;
            document.getElementById('actividades-grid').style.display = 'none';
            document.getElementById('estudios-section').classList.add('visible');
            
            cargarEstudios(id);
        }
        
        function cargarEstudios(actividadId) {
            fetch('ver_estudios.php', {
                method: 'POST',
                headers: {'Content-Type': 'application/x-www-form-urlencoded'},
                body: `action=get_estudios&actividad_id=${actividadId}`
            })
            .then(r => r.json())
            .then(data => {
                if (data.success) {
                    mostrarEstudios(data.estudios);
                }
            });
        }
        
        function mostrarEstudios(estudios) {
            const container = document.getElementById('estudios-container');
            
            if (estudios.length === 0) {
                container.innerHTML = '<div class="empty-state"><div class="empty-state-icon">📂</div><p>No hay estudios subidos en esta actividad</p></div>';
                return;
            }
            
            container.innerHTML = estudios.map(est => `
                <div class="estudio-card">
                    <div class="estudio-header">
                        <div class="estudio-title">${est.owner}</div>
                        <span class="tipo-badge tipo-${est.tipo}">${getTipoNombre(est.tipo)}</span>
                    </div>
                    
                    <div class="estudio-info">
                        <div>
                            <span class="info-label">RUT:</span> ${est.rut}
                        </div>
                        <div>
                            <span class="info-label">Fecha:</span> ${formatDate(est.uploaded)}
                        </div>
                        <div>
                            <span class="info-label">PDF:</span> ${formatSize(est.pdf.size)}
                        </div>
                        ${est.raw ? `<div><span class="info-label">RAW:</span> ${formatSize(est.raw.size)}</div>` : ''}
                    </div>
                    
                    <div class="estudio-actions">
                        <a href="${est.pdf.url}" class="btn btn-pdf btn-small" target="_blank">📄 Ver PDF</a>
                        ${est.raw ? `<a href="${est.raw.url}" class="btn btn-raw btn-small" download>💾 Descargar RAW</a>` : ''}
                    </div>
                </div>
            `).join('');
        }
        
        function volverActividades() {
            document.getElementById('actividades-grid').style.display = 'grid';
            document.getElementById('estudios-section').classList.remove('visible');
            actividadSeleccionada = null;
        }
        
        function actualizarEstadisticas() {
            document.getElementById('stat-actividades').textContent = actividadesDisponibles.length;
            
            // Contar estudios totales
            // TODO: implementar conteo real
            document.getElementById('stat-estudios').textContent = '...';
        }
        
        function cerrarSesion() {
            fetch('auth.php?action=logout')
                .then(() => {
                    location.reload();
                });
        }
        
        function getTipoNombre(tipo) {
            const tipos = {
                'espirometria': 'Espirometría',
                'ecg': 'ECG',
                'emg': 'EMG',
                'eeg': 'EEG'
            };
            return tipos[tipo] || tipo;
        }
        
        function formatDate(isoString) {
            const date = new Date(isoString);
            return date.toLocaleDateString('es-CL', { 
                year: 'numeric', 
                month: 'short', 
                day: 'numeric',
                hour: '2-digit',
                minute: '2-digit'
            });
        }
        
        function formatSize(bytes) {
            if (bytes < 1024) return bytes + ' B';
            if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
            return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
        }
    </script>
</body>
</html>