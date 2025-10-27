<?php
/**
 * actividades.php - Gestión de actividades (CRUD)
 * 
 * GET: Muestra interfaz HTML para gestionar actividades
 * POST action=crear: Crear nueva actividad
 * POST action=editar: Editar actividad existente
 * POST action=eliminar: Eliminar actividad
 * POST action=listar: Listar todas las actividades
 * 
 * REQUIERE: Autenticación como profesor
 */

session_start();

// ========== VERIFICAR AUTENTICACIÓN ==========
function verificarProfesor() {
    if (!isset($_SESSION['authenticated']) || !$_SESSION['authenticated']) {
        return false;
    }
    
    if ($_SESSION['tipo'] !== 'profesor') {
        return false;
    }
    
    // Verificar timeout de sesión (2 horas)
    $timeout = 7200;
    if (time() - $_SESSION['login_time'] > $timeout) {
        session_destroy();
        return false;
    }
    
    return true;
}

// Verificar autenticación para todas las peticiones
if (!verificarProfesor()) {
    if ($_SERVER['REQUEST_METHOD'] === 'POST') {
        // Respuesta JSON para peticiones AJAX
        header('Content-Type: application/json');
        http_response_code(401);
        echo json_encode(['error' => 'No autorizado. Debe iniciar sesión como profesor.']);
        exit;
    } else {
        // Redireccionar a login para peticiones GET
        header('Location: ver_estudios.php?redirect=actividades');
        exit;
    }
}

$dataDir = __DIR__ . '/data/';
$actividadesFile = $dataDir . 'actividades.json';

// Crear directorio si no existe
if (!is_dir($dataDir)) {
    mkdir($dataDir, 0755, true);
}

// Constantes
const TIPOS_ESTUDIO = [
    'espirometria' => 'Espirometría',
    'ecg' => 'Electrocardiograma',
    'emg' => 'Electromiografía',
    'eeg' => 'Electroencefalograma'
];

// ========== FUNCIONES AUXILIARES ==========

function cargarActividades() {
    global $actividadesFile;
    if (!file_exists($actividadesFile)) {
        return [];
    }
    return json_decode(file_get_contents($actividadesFile), true) ?: [];
}

function guardarActividades($actividades) {
    global $actividadesFile;
    file_put_contents($actividadesFile, json_encode($actividades, JSON_PRETTY_PRINT));
}

function generarIdActividad() {
    return 'ACT' . strtoupper(bin2hex(random_bytes(3)));
}

// ========== MANEJO DE ACCIONES API ==========

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    header('Content-Type: application/json');
    
    $action = $_POST['action'] ?? '';
    
    switch ($action) {
        case 'crear':
            crearActividad();
            break;
        
        case 'editar':
            editarActividad();
            break;
        
        case 'eliminar':
            eliminarActividad();
            break;
        
        case 'listar':
            listarActividades();
            break;
        
        default:
            http_response_code(400);
            echo json_encode(['error' => 'Acción no válida']);
            exit;
    }
}

// ========== CREAR ACTIVIDAD ==========
function crearActividad() {
    // Validar campos requeridos
    $required = ['nombre', 'tipo', 'descripcion', 'profesor', 'password'];
    foreach ($required as $field) {
        if (empty($_POST[$field])) {
            http_response_code(400);
            echo json_encode(['error' => "Campo requerido: $field"]);
            exit;
        }
    }
    
    $actividades = cargarActividades();
    
    // Generar ID único
    $id = generarIdActividad();
    
    // Crear actividad
    $actividades[$id] = [
        'id' => $id,
        'nombre' => trim($_POST['nombre']),
        'tipo' => trim($_POST['tipo']),
        'descripcion' => trim($_POST['descripcion']),
        'profesor' => trim($_POST['profesor']),
        'created' => date('c'),
        'publico' => isset($_POST['publico']) && $_POST['publico'] === 'true',
        'usuarios_permitidos' => [],
        'password_hash' => password_hash($_POST['password'], PASSWORD_DEFAULT)
    ];
    
    // Agregar usuarios permitidos si hay
    if (!empty($_POST['usuarios_permitidos'])) {
        $usuarios = array_map('trim', explode(',', $_POST['usuarios_permitidos']));
        $actividades[$id]['usuarios_permitidos'] = array_filter($usuarios);
    }
    
    guardarActividades($actividades);
    
    echo json_encode([
        'success' => true,
        'actividad' => $actividades[$id],
        'message' => 'Actividad creada exitosamente'
    ]);
}

// ========== EDITAR ACTIVIDAD ==========
function editarActividad() {
    $id = $_POST['id'] ?? '';
    
    if (empty($id)) {
        http_response_code(400);
        echo json_encode(['error' => 'ID de actividad requerido']);
        exit;
    }
    
    $actividades = cargarActividades();
    
    if (!isset($actividades[$id])) {
        http_response_code(404);
        echo json_encode(['error' => 'Actividad no encontrada']);
        exit;
    }
    
    // Actualizar campos
    if (!empty($_POST['nombre'])) {
        $actividades[$id]['nombre'] = trim($_POST['nombre']);
    }
    if (!empty($_POST['descripcion'])) {
        $actividades[$id]['descripcion'] = trim($_POST['descripcion']);
    }
    if (isset($_POST['publico'])) {
        $actividades[$id]['publico'] = $_POST['publico'] === 'true';
    }
    if (!empty($_POST['usuarios_permitidos'])) {
        $usuarios = array_map('trim', explode(',', $_POST['usuarios_permitidos']));
        $actividades[$id]['usuarios_permitidos'] = array_filter($usuarios);
    }
    if (!empty($_POST['password'])) {
        $actividades[$id]['password_hash'] = password_hash($_POST['password'], PASSWORD_DEFAULT);
    }
    
    $actividades[$id]['updated'] = date('c');
    
    guardarActividades($actividades);
    
    echo json_encode([
        'success' => true,
        'actividad' => $actividades[$id],
        'message' => 'Actividad actualizada exitosamente'
    ]);
}

// ========== ELIMINAR ACTIVIDAD ==========
function eliminarActividad() {
    $id = $_POST['id'] ?? '';
    
    if (empty($id)) {
        http_response_code(400);
        echo json_encode(['error' => 'ID de actividad requerido']);
        exit;
    }
    
    $actividades = cargarActividades();
    
    if (!isset($actividades[$id])) {
        http_response_code(404);
        echo json_encode(['error' => 'Actividad no encontrada']);
        exit;
    }
    
    unset($actividades[$id]);
    guardarActividades($actividades);
    
    // TODO: Opcionalmente eliminar archivos asociados
    
    echo json_encode([
        'success' => true,
        'message' => 'Actividad eliminada exitosamente'
    ]);
}

// ========== LISTAR ACTIVIDADES ==========
function listarActividades() {
    $actividades = cargarActividades();
    
    // No incluir password_hash en respuesta
    foreach ($actividades as &$act) {
        unset($act['password_hash']);
    }
    
    echo json_encode([
        'success' => true,
        'actividades' => array_values($actividades)
    ]);
}

// ========== INTERFAZ HTML (GET) ==========
?>
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Gestión de Actividades - FisioaccessPC</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
            background: #f5f5f5;
            padding: 20px;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            padding: 30px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        
        .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 30px;
            padding-bottom: 20px;
            border-bottom: 2px solid #e0e0e0;
        }
        
        h1 {
            color: #2c3e50;
            font-size: 28px;
        }
        
        .btn {
            padding: 10px 20px;
            border: none;
            border-radius: 6px;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
            text-decoration: none;
            display: inline-block;
        }
        
        .btn-primary {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        
        .btn-primary:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
        }
        
        .btn-secondary {
            background: #e0e0e0;
            color: #2c3e50;
        }
        
        .btn-danger {
            background: #e74c3c;
            color: white;
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
        textarea,
        select {
            width: 100%;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 6px;
            font-size: 14px;
        }
        
        textarea {
            resize: vertical;
            min-height: 80px;
        }
        
        .checkbox-group {
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .actividades-lista {
            display: grid;
            gap: 15px;
            margin-top: 20px;
        }
        
        .actividad-card {
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            padding: 20px;
            transition: box-shadow 0.3s;
        }
        
        .actividad-card:hover {
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        }
        
        .actividad-header {
            display: flex;
            justify-content: space-between;
            align-items: start;
            margin-bottom: 10px;
        }
        
        .actividad-id {
            background: #667eea;
            color: white;
            padding: 4px 10px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: 600;
        }
        
        .tipo-badge {
            display: inline-block;
            padding: 4px 10px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: 600;
            margin-left: 10px;
        }
        
        .tipo-espirometria { background: #3498db; color: white; }
        .tipo-ecg { background: #e74c3c; color: white; }
        .tipo-emg { background: #27ae60; color: white; }
        .tipo-eeg { background: #f39c12; color: white; }
        
        .modal {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.5);
            z-index: 1000;
        }
        
        .modal-content {
            position: relative;
            background: white;
            margin: 50px auto;
            padding: 30px;
            max-width: 600px;
            border-radius: 12px;
            max-height: 90vh;
            overflow-y: auto;
        }
        
        .close {
            position: absolute;
            right: 20px;
            top: 20px;
            font-size: 28px;
            cursor: pointer;
            color: #999;
        }
        
        .close:hover {
            color: #333;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div>
                <h1>📚 Gestión de Actividades</h1>
                <p style="color: #7f8c8d; font-size: 14px; margin-top: 5px;">
                    Profesor: <?= htmlspecialchars($_SESSION['nombre']) ?> (<?= htmlspecialchars($_SESSION['rut']) ?>)
                </p>
            </div>
            <div>
                <button class="btn btn-primary" onclick="abrirModalCrear()">+ Nueva Actividad</button>
                <a href="ver_estudios.php" class="btn btn-secondary">📊 Ver Estudios</a>
                <a href="index.html" class="btn btn-secondary">← Volver</a>
            </div>
        </div>
        
        <div id="actividades-container" class="actividades-lista">
            <p style="text-align: center; color: #999;">Cargando actividades...</p>
        </div>
    </div>
    
    <!-- Modal Crear/Editar -->
    <div id="modalActividad" class="modal">
        <div class="modal-content">
            <span class="close" onclick="cerrarModal()">&times;</span>
            <h2 id="modal-titulo">Nueva Actividad</h2>
            <form id="formActividad" onsubmit="guardarActividad(event)">
                <input type="hidden" id="actividad-id" name="id">
                
                <div class="form-group">
                    <label for="nombre">Nombre de la Actividad *</label>
                    <input type="text" id="nombre" name="nombre" required>
                </div>
                
                <div class="form-group">
                    <label for="tipo">Tipo de Estudio *</label>
                    <select id="tipo" name="tipo" required>
                        <?php foreach (TIPOS_ESTUDIO as $key => $value): ?>
                        <option value="<?= $key ?>"><?= $value ?></option>
                        <?php endforeach; ?>
                    </select>
                </div>
                
                <div class="form-group">
                    <label for="descripcion">Descripción *</label>
                    <textarea id="descripcion" name="descripcion" required></textarea>
                </div>
                
                <div class="form-group">
                    <label for="profesor">Profesor a Cargo *</label>
                    <input type="text" id="profesor" name="profesor" required>
                </div>
                
                <div class="form-group">
                    <label for="password">Contraseña de Acceso *</label>
                    <input type="password" id="password" name="password">
                    <small style="color: #999;">Los estudiantes necesitarán esta contraseña para acceder</small>
                </div>
                
                <div class="form-group">
                    <label for="usuarios_permitidos">RUTs Permitidos (opcional)</label>
                    <input type="text" id="usuarios_permitidos" name="usuarios_permitidos" 
                           placeholder="12345678-9, 98765432-1">
                    <small style="color: #999;">Separar por comas. Dejar vacío para permitir todos</small>
                </div>
                
                <div class="form-group checkbox-group">
                    <input type="checkbox" id="publico" name="publico">
                    <label for="publico" style="margin: 0;">Actividad pública (cualquiera puede subir)</label>
                </div>
                
                <div style="display: flex; gap: 10px; margin-top: 20px;">
                    <button type="submit" class="btn btn-primary">Guardar</button>
                    <button type="button" class="btn btn-secondary" onclick="cerrarModal()">Cancelar</button>
                </div>
            </form>
        </div>
    </div>
    
    <script>
        let modoEdicion = false;
        
        // Cargar actividades al inicio
        cargarActividades();
        
        function cargarActividades() {
            fetch('actividades.php', {
                method: 'POST',
                headers: {'Content-Type': 'application/x-www-form-urlencoded'},
                body: 'action=listar'
            })
            .then(r => r.json())
            .then(data => {
                if (data.success) {
                    mostrarActividades(data.actividades);
                }
            })
            .catch(err => console.error('Error:', err));
        }
        
        function mostrarActividades(actividades) {
            const container = document.getElementById('actividades-container');
            
            if (actividades.length === 0) {
                container.innerHTML = '<p style="text-align: center; color: #999;">No hay actividades creadas</p>';
                return;
            }
            
            container.innerHTML = actividades.map(act => `
                <div class="actividad-card">
                    <div class="actividad-header">
                        <div>
                            <span class="actividad-id">${act.id}</span>
                            <span class="tipo-badge tipo-${act.tipo}">${getTipoNombre(act.tipo)}</span>
                        </div>
                        <div>
                            <button class="btn btn-secondary" onclick="editarActividad('${act.id}')">Editar</button>
                            <button class="btn btn-danger" onclick="eliminarActividad('${act.id}')">Eliminar</button>
                        </div>
                    </div>
                    <h3>${act.nombre}</h3>
                    <p style="color: #666; margin: 10px 0;">${act.descripcion}</p>
                    <p style="font-size: 12px; color: #999;">
                        Profesor: ${act.profesor} | Creado: ${new Date(act.created).toLocaleDateString('es-CL')}
                        ${act.publico ? ' | 🌐 Pública' : ' | 🔒 Privada'}
                    </p>
                </div>
            `).join('');
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
        
        function abrirModalCrear() {
            modoEdicion = false;
            document.getElementById('modal-titulo').textContent = 'Nueva Actividad';
            document.getElementById('formActividad').reset();
            document.getElementById('actividad-id').value = '';
            document.getElementById('password').required = true;
            document.getElementById('modalActividad').style.display = 'block';
        }
        
        function editarActividad(id) {
            // TODO: Cargar datos de la actividad y rellenar formulario
            modoEdicion = true;
            document.getElementById('modal-titulo').textContent = 'Editar Actividad';
            document.getElementById('actividad-id').value = id;
            document.getElementById('password').required = false;
            document.getElementById('modalActividad').style.display = 'block';
        }
        
        function cerrarModal() {
            document.getElementById('modalActividad').style.display = 'none';
        }
        
        function guardarActividad(e) {
            e.preventDefault();
            const formData = new FormData(e.target);
            formData.append('action', modoEdicion ? 'editar' : 'crear');
            formData.append('publico', document.getElementById('publico').checked);
            
            fetch('actividades.php', {
                method: 'POST',
                body: new URLSearchParams(formData)
            })
            .then(r => r.json())
            .then(data => {
                if (data.success) {
                    alert(data.message);
                    cerrarModal();
                    cargarActividades();
                } else {
                    alert('Error: ' + data.error);
                }
            })
            .catch(err => {
                console.error('Error:', err);
                alert('Error al guardar actividad');
            });
        }
        
        function eliminarActividad(id) {
            if (!confirm('¿Está seguro de eliminar esta actividad? Esto no eliminará los archivos asociados.')) {
                return;
            }
            
            fetch('actividades.php', {
                method: 'POST',
                headers: {'Content-Type': 'application/x-www-form-urlencoded'},
                body: `action=eliminar&id=${id}`
            })
            .then(r => r.json())
            .then(data => {
                if (data.success) {
                    alert(data.message);
                    cargarActividades();
                } else {
                    alert('Error: ' + data.error);
                }
            });
        }
        
        // Cerrar modal al hacer clic fuera
        window.onclick = function(event) {
            const modal = document.getElementById('modalActividad');
            if (event.target === modal) {
                cerrarModal();
            }
        }
    </script>
</body>
</html>