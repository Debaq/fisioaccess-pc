<?php
/**
 * admin/profesores.php - Gestión de profesores
 */

require_once '../config.php';

session_start();

if (!verificarRol('admin')) {
    header('Location: login.php');
    exit;
}

$mensaje = '';
$tipo_mensaje = '';

// Procesar acciones
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    // Validar CSRF token
    $csrf_token = $_POST['csrf_token'] ?? '';
    if (!validarTokenCSRF($csrf_token)) {
        $mensaje = 'Token de seguridad inválido. Intenta nuevamente.';
        $tipo_mensaje = 'error';
        registrarEventoSeguridad('CSRF token inválido en profesores', [
            'admin_rut' => $_SESSION['rut'] ?? 'unknown',
            'ip' => obtenerIP()
        ]);
    } else {
        $action = sanitizarString($_POST['action'] ?? '', ['max_length' => 20]);

        $profesores = cargarJSON(PROFESORES_FILE);
        $config = cargarJSON(CONFIG_FILE);

        if ($action === 'crear') {
            // Sanitizar y validar inputs
            $rut = sanitizarString($_POST['rut'] ?? '', ['max_length' => 12]);
            $nombre = sanitizarString($_POST['nombre'] ?? '', ['max_length' => 200]);
            $email = sanitizarString($_POST['email'] ?? '', ['max_length' => 255]);
            $password = $_POST['password'] ?? '';
            $cuota = intval($_POST['cuota_actividades'] ?? $config['cuotas_default']['actividades_profesor']);
            $departamento = sanitizarString($_POST['departamento'] ?? '', ['max_length' => 200]);
            $telefono = sanitizarString($_POST['telefono'] ?? '', ['max_length' => 20]);

            // Validaciones
            if (!validarRUT($rut)) {
                $mensaje = 'RUT inválido';
                $tipo_mensaje = 'error';
            } elseif (!validarEmail($email)) {
                $mensaje = 'Email inválido';
                $tipo_mensaje = 'error';
            } elseif (validarNoVacio($nombre) !== true) {
                $mensaje = 'El nombre es requerido';
                $tipo_mensaje = 'error';
            } elseif (validarNoVacio($password) !== true || !validarLongitud($password, 6, 100)) {
                $mensaje = 'La contraseña debe tener al menos 6 caracteres';
                $tipo_mensaje = 'error';
            } elseif ($cuota < 1 || $cuota > 20) {
                $mensaje = 'La cuota debe estar entre 1 y 20';
                $tipo_mensaje = 'error';
            } elseif (isset($profesores[$rut])) {
                $mensaje = 'Ya existe un profesor con ese RUT';
                $tipo_mensaje = 'error';
            } else {
                $profesores[$rut] = [
                    'rut' => $rut,
                    'nombre' => $nombre,
                    'email' => $email,
                    'password_hash' => password_hash($password, PASSWORD_DEFAULT),
                    'created' => formatearFecha(),
                    'activo' => true,
                    'cuota_actividades' => $cuota,
                    'actividades_usadas' => 0,
                    'departamento' => $departamento,
                    'telefono' => $telefono,
                    'last_login' => null
                ];

                guardarJSON(PROFESORES_FILE, $profesores);

                // Logging
                registrarLog('INFO', 'Profesor creado', [
                    'admin_rut' => $_SESSION['rut'],
                    'profesor_rut' => $rut,
                    'nombre' => $nombre,
                    'email' => $email,
                    'ip' => obtenerIP()
                ]);

                $mensaje = 'Profesor creado exitosamente';
                $tipo_mensaje = 'success';
            }
        }
    

        elseif ($action === 'editar') {
            // Sanitizar y validar inputs
            $rut = sanitizarString($_POST['rut'] ?? '', ['max_length' => 12]);
            $nombre = sanitizarString($_POST['nombre'] ?? '', ['max_length' => 200]);
            $email = sanitizarString($_POST['email'] ?? '', ['max_length' => 255]);
            $password = $_POST['password'] ?? '';
            $cuota = intval($_POST['cuota_actividades'] ?? 4);
            $departamento = sanitizarString($_POST['departamento'] ?? '', ['max_length' => 200]);
            $telefono = sanitizarString($_POST['telefono'] ?? '', ['max_length' => 20]);

            // Validaciones
            if (!validarRUT($rut)) {
                $mensaje = 'RUT inválido';
                $tipo_mensaje = 'error';
            } elseif (!validarEmail($email)) {
                $mensaje = 'Email inválido';
                $tipo_mensaje = 'error';
            } elseif (validarNoVacio($nombre) !== true) {
                $mensaje = 'El nombre es requerido';
                $tipo_mensaje = 'error';
            } elseif ($cuota < 1 || $cuota > 20) {
                $mensaje = 'La cuota debe estar entre 1 y 20';
                $tipo_mensaje = 'error';
            } elseif (!empty($password) && !validarLongitud($password, 6, 100)) {
                $mensaje = 'La contraseña debe tener al menos 6 caracteres';
                $tipo_mensaje = 'error';
            } elseif (!isset($profesores[$rut])) {
                $mensaje = 'Profesor no encontrado';
                $tipo_mensaje = 'error';
            } else {
                $profesores[$rut]['nombre'] = $nombre;
                $profesores[$rut]['email'] = $email;
                $profesores[$rut]['departamento'] = $departamento;
                $profesores[$rut]['telefono'] = $telefono;
                $profesores[$rut]['cuota_actividades'] = $cuota;

                if (!empty($password)) {
                    $profesores[$rut]['password_hash'] = password_hash($password, PASSWORD_DEFAULT);
                }

                guardarJSON(PROFESORES_FILE, $profesores);

                // Logging
                registrarLog('INFO', 'Profesor editado', [
                    'admin_rut' => $_SESSION['rut'],
                    'profesor_rut' => $rut,
                    'nombre' => $nombre,
                    'email' => $email,
                    'password_changed' => !empty($password),
                    'ip' => obtenerIP()
                ]);

                $mensaje = 'Profesor actualizado exitosamente';
                $tipo_mensaje = 'success';
            }
        }

        elseif ($action === 'toggle_activo') {
            $rut = sanitizarString($_POST['rut'] ?? '', ['max_length' => 12]);

            if (!validarRUT($rut)) {
                $mensaje = 'RUT inválido';
                $tipo_mensaje = 'error';
            } elseif (!isset($profesores[$rut])) {
                $mensaje = 'Profesor no encontrado';
                $tipo_mensaje = 'error';
            } else {
                $profesores[$rut]['activo'] = !$profesores[$rut]['activo'];
                guardarJSON(PROFESORES_FILE, $profesores);

                $estado = $profesores[$rut]['activo'] ? 'activado' : 'desactivado';

                // Logging
                registrarLog('INFO', "Profesor {$estado}", [
                    'admin_rut' => $_SESSION['rut'],
                    'profesor_rut' => $rut,
                    'nuevo_estado' => $profesores[$rut]['activo'],
                    'ip' => obtenerIP()
                ]);

                $mensaje = "Profesor {$estado} exitosamente";
                $tipo_mensaje = 'success';
            }
        }
    }
}

$profesores = cargarJSON(PROFESORES_FILE);
$config = cargarJSON(CONFIG_FILE);
?>
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Gestionar Profesores - FisioaccessPC</title>
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
        
        .btn-success {
            background: rgba(34, 197, 94, 0.3);
            color: white;
            border: 1px solid rgba(34, 197, 94, 0.5);
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
        
        input, select {
            width: 100%;
            padding: 10px;
            border: 1px solid rgba(255, 255, 255, 0.3);
            border-radius: 10px;
            background: rgba(255, 255, 255, 0.1);
            color: white;
            font-size: 14px;
        }
        
        input::placeholder {
            color: rgba(255, 255, 255, 0.6);
        }
        
        input:focus {
            outline: none;
            border-color: rgba(255, 255, 255, 0.6);
            background: rgba(255, 255, 255, 0.15);
        }
        
        .profesores-list {
            display: grid;
            gap: 15px;
        }
        
        .profesor-card {
            background: rgba(255, 255, 255, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 12px;
            padding: 20px;
            color: white;
        }
        
        .profesor-card.inactivo {
            opacity: 0.6;
        }
        
        .profesor-header {
            display: flex;
            justify-content: space-between;
            align-items: start;
            margin-bottom: 15px;
        }
        
        .profesor-nombre {
            font-size: 18px;
            font-weight: 600;
            margin-bottom: 5px;
        }
        
        .profesor-rut {
            font-size: 14px;
            opacity: 0.8;
        }
        
        .profesor-info {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 10px;
            margin-bottom: 15px;
            font-size: 14px;
        }
        
        .profesor-actions {
            display: flex;
            gap: 10px;
        }
        
        .badge {
            display: inline-block;
            padding: 4px 10px;
            border-radius: 6px;
            font-size: 12px;
            font-weight: 600;
        }
        
        .badge-success {
            background: rgba(34, 197, 94, 0.3);
            border: 1px solid rgba(34, 197, 94, 0.5);
        }
        
        .badge-danger {
            background: rgba(239, 68, 68, 0.3);
            border: 1px solid rgba(239, 68, 68, 0.5);
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
            max-width: 600px;
            margin: 50px auto;
        }
        
        .modal-header {
            color: white;
            margin-bottom: 25px;
            font-size: 24px;
        }
        
        .form-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 15px;
        }
        
        .form-full {
            grid-column: 1 / -1;
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
            <h1>👨‍🏫 Gestión de Profesores</h1>
            <button class="btn btn-primary" onclick="abrirModal()">+ Nuevo Profesor</button>
        </div>
        
        <?php if ($mensaje): ?>
            <div class="mensaje <?= $tipo_mensaje ?>">
                <?= htmlspecialchars($mensaje) ?>
            </div>
        <?php endif; ?>
        
        <div class="card">
            <?php if (empty($profesores)): ?>
                <p style="color: white; text-align: center; opacity: 0.8;">
                    No hay profesores registrados. Crea el primero usando el botón superior.
                </p>
            <?php else: ?>
                <div class="profesores-list">
                    <?php foreach ($profesores as $rut => $prof): ?>
                        <div class="profesor-card <?= $prof['activo'] ? '' : 'inactivo' ?>">
                            <div class="profesor-header">
                                <div>
                                    <div class="profesor-nombre"><?= htmlspecialchars($prof['nombre']) ?></div>
                                    <div class="profesor-rut">RUT: <?= htmlspecialchars($rut) ?></div>
                                </div>
                                <span class="badge <?= $prof['activo'] ? 'badge-success' : 'badge-danger' ?>">
                                    <?= $prof['activo'] ? '✅ Activo' : '❌ Inactivo' ?>
                                </span>
                            </div>
                            
                            <div class="profesor-info">
                                <div>📧 <?= htmlspecialchars($prof['email']) ?></div>
                                <div>🏢 <?= htmlspecialchars($prof['departamento'] ?: 'Sin departamento') ?></div>
                                <div>📊 Cuota: <?= $prof['actividades_usadas'] ?>/<?= $prof['cuota_actividades'] ?> actividades</div>
                                <div>📅 Creado: <?= date('d/m/Y', strtotime($prof['created'])) ?></div>
                            </div>
                            
                            <div class="profesor-actions">
                                <button class="btn btn-secondary btn-small" onclick='editarProfesor(<?= json_encode($prof) ?>)'>
                                    ✏️ Editar
                                </button>
                                <form method="POST" style="display: inline;">
                                    <input type="hidden" name="csrf_token" value="<?= generarTokenCSRF() ?>">
                                    <input type="hidden" name="action" value="toggle_activo">
                                    <input type="hidden" name="rut" value="<?= $rut ?>">
                                    <button type="submit" class="btn <?= $prof['activo'] ? 'btn-danger' : 'btn-success' ?> btn-small">
                                        <?= $prof['activo'] ? '🚫 Desactivar' : '✅ Activar' ?>
                                    </button>
                                </form>
                            </div>
                        </div>
                    <?php endforeach; ?>
                </div>
            <?php endif; ?>
        </div>
    </div>
    
    <!-- Modal Crear/Editar -->
    <div id="modalProfesor" class="modal">
        <div class="modal-content">
            <h2 class="modal-header" id="modal-titulo">Nuevo Profesor</h2>
            <form method="POST" id="formProfesor">
                <input type="hidden" name="csrf_token" value="<?= generarTokenCSRF() ?>">
                <input type="hidden" name="action" id="form-action" value="crear">
                
                <div class="form-grid">
                    <div class="form-full">
                        <label>RUT *</label>
                        <input type="text" name="rut" id="form-rut" placeholder="12345678-9" required>
                    </div>
                    
                    <div class="form-full">
                        <label>Nombre Completo *</label>
                        <input type="text" name="nombre" id="form-nombre" placeholder="Dr. Juan Pérez" required>
                    </div>
                    
                    <div class="form-full">
                        <label>Email *</label>
                        <input type="email" name="email" id="form-email" placeholder="juan@universidad.cl" required>
                    </div>
                    
                    <div>
                        <label>Departamento</label>
                        <input type="text" name="departamento" id="form-departamento" placeholder="Fisiología">
                    </div>
                    
                    <div>
                        <label>Teléfono</label>
                        <input type="text" name="telefono" id="form-telefono" placeholder="+56912345678">
                    </div>
                    
                    <div>
                        <label>Cuota de Actividades *</label>
                        <input type="number" name="cuota_actividades" id="form-cuota" 
                               value="<?= $config['cuotas_default']['actividades_profesor'] ?>" min="1" required>
                    </div>
                    
                    <div>
                        <label>Contraseña <span id="password-label">*</span></label>
                        <input type="password" name="password" id="form-password" placeholder="••••••••">
                        <small style="color: rgba(255,255,255,0.8); font-size: 12px;" id="password-hint"></small>
                    </div>
                </div>
                
                <div style="display: flex; gap: 10px; margin-top: 25px;">
                    <button type="submit" class="btn btn-primary" style="flex: 1;">Guardar</button>
                    <button type="button" class="btn btn-secondary" style="flex: 1;" onclick="cerrarModal()">Cancelar</button>
                </div>
            </form>
        </div>
    </div>
    
    <script>
        function abrirModal() {
            document.getElementById('modal-titulo').textContent = 'Nuevo Profesor';
            document.getElementById('form-action').value = 'crear';
            document.getElementById('formProfesor').reset();
            document.getElementById('form-rut').readOnly = false;
            document.getElementById('form-password').required = true;
            document.getElementById('password-label').textContent = '*';
            document.getElementById('password-hint').textContent = '';
            document.getElementById('modalProfesor').style.display = 'block';
        }
        
        function editarProfesor(profesor) {
            document.getElementById('modal-titulo').textContent = 'Editar Profesor';
            document.getElementById('form-action').value = 'editar';
            document.getElementById('form-rut').value = profesor.rut;
            document.getElementById('form-rut').readOnly = true;
            document.getElementById('form-nombre').value = profesor.nombre;
            document.getElementById('form-email').value = profesor.email;
            document.getElementById('form-departamento').value = profesor.departamento || '';
            document.getElementById('form-telefono').value = profesor.telefono || '';
            document.getElementById('form-cuota').value = profesor.cuota_actividades;
            document.getElementById('form-password').value = '';
            document.getElementById('form-password').required = false;
            document.getElementById('password-label').textContent = '(opcional)';
            document.getElementById('password-hint').textContent = 'Dejar en blanco para mantener la actual';
            document.getElementById('modalProfesor').style.display = 'block';
        }
        
        function cerrarModal() {
            document.getElementById('modalProfesor').style.display = 'none';
        }
        
        // Cerrar modal al hacer click fuera
        window.onclick = function(event) {
            const modal = document.getElementById('modalProfesor');
            if (event.target === modal) {
                cerrarModal();
            }
        }
    </script>
</body>
</html>