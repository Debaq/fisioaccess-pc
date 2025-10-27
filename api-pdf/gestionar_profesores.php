<?php
/**
 * gestionar_profesores.php - Herramienta para administrar profesores
 * 
 * IMPORTANTE: Este archivo debe estar protegido o eliminarse en producción
 * 
 * Funciones:
 * - Generar hash de contraseña
 * - Agregar nuevo profesor
 * - Modificar contraseña de profesor
 * - Desactivar/activar profesor
 */

$profesoresFile = __DIR__ . '/data/profesores.json';

// Crear directorio si no existe
if (!is_dir(__DIR__ . '/data/')) {
    mkdir(__DIR__ . '/data/', 0755, true);
}

function cargarProfesores() {
    global $profesoresFile;
    if (!file_exists($profesoresFile)) {
        return [];
    }
    return json_decode(file_get_contents($profesoresFile), true) ?: [];
}

function guardarProfesores($profesores) {
    global $profesoresFile;
    file_put_contents($profesoresFile, json_encode($profesores, JSON_PRETTY_PRINT));
}

// ========== DETERMINAR ACCIÓN ==========
$accion = $_GET['accion'] ?? 'menu';

?>
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Gestionar Profesores - FisioaccessPC</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
            background: #f5f5f5;
            padding: 20px;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            padding: 30px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        h1 { color: #2c3e50; margin-bottom: 20px; }
        h2 { color: #34495e; margin: 20px 0 10px; }
        .warning {
            background: #fff3cd;
            border: 1px solid #ffc107;
            border-radius: 6px;
            padding: 15px;
            margin-bottom: 20px;
        }
        .success {
            background: #d4edda;
            border: 1px solid #28a745;
            border-radius: 6px;
            padding: 15px;
            margin-bottom: 20px;
        }
        .error {
            background: #f8d7da;
            border: 1px solid #dc3545;
            border-radius: 6px;
            padding: 15px;
            margin-bottom: 20px;
        }
        .form-group {
            margin-bottom: 15px;
        }
        label {
            display: block;
            margin-bottom: 5px;
            font-weight: 600;
            color: #2c3e50;
        }
        input[type="text"],
        input[type="password"],
        input[type="email"] {
            width: 100%;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 6px;
            font-size: 14px;
        }
        .btn {
            padding: 10px 20px;
            border: none;
            border-radius: 6px;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            text-decoration: none;
            display: inline-block;
        }
        .btn-primary {
            background: #667eea;
            color: white;
        }
        .btn-success {
            background: #28a745;
            color: white;
        }
        .btn-secondary {
            background: #e0e0e0;
            color: #2c3e50;
        }
        .profesor-list {
            margin-top: 20px;
        }
        .profesor-item {
            border: 1px solid #e0e0e0;
            border-radius: 6px;
            padding: 15px;
            margin-bottom: 10px;
        }
        .profesor-item.inactivo {
            opacity: 0.5;
            background: #f8f9fa;
        }
        code {
            background: #f4f4f4;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
        }
        pre {
            background: #f4f4f4;
            padding: 15px;
            border-radius: 6px;
            overflow-x: auto;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔐 Gestión de Profesores</h1>
        
        <div class="warning">
            <strong>⚠️ ADVERTENCIA:</strong> Esta herramienta debe ser protegida con contraseña o eliminada en producción.
        </div>

        <?php if ($accion === 'menu'): ?>
            
            <h2>Opciones</h2>
            <div style="display: flex; gap: 10px; margin: 20px 0;">
                <a href="?accion=listar" class="btn btn-primary">📋 Listar Profesores</a>
                <a href="?accion=agregar" class="btn btn-success">➕ Agregar Profesor</a>
                <a href="?accion=generar_hash" class="btn btn-secondary">🔑 Generar Hash</a>
            </div>
            
            <h2>Profesores Actuales</h2>
            <?php
            $profesores = cargarProfesores();
            if (empty($profesores)):
            ?>
                <p style="color: #999;">No hay profesores registrados.</p>
            <?php else: ?>
                <div class="profesor-list">
                    <?php foreach ($profesores as $rut => $prof): ?>
                        <div class="profesor-item <?= $prof['activo'] ? '' : 'inactivo' ?>">
                            <strong><?= htmlspecialchars($prof['nombre']) ?></strong>
                            <br>RUT: <?= htmlspecialchars($rut) ?>
                            <br>Email: <?= htmlspecialchars($prof['email']) ?>
                            <br>Estado: <?= $prof['activo'] ? '✅ Activo' : '❌ Inactivo' ?>
                        </div>
                    <?php endforeach; ?>
                </div>
            <?php endif; ?>

        <?php elseif ($accion === 'generar_hash'): ?>
            
            <h2>🔑 Generar Hash de Contraseña</h2>
            <a href="?accion=menu" class="btn btn-secondary">← Volver</a>
            
            <?php
            if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['password'])) {
                $password = $_POST['password'];
                $hash = password_hash($password, PASSWORD_DEFAULT);
                ?>
                <div class="success" style="margin-top: 20px;">
                    <strong>✅ Hash generado:</strong>
                    <pre><?= $hash ?></pre>
                    <p>Copia este hash y úsalo en el campo <code>password_hash</code> del archivo JSON.</p>
                </div>
            <?php } ?>
            
            <form method="POST" style="margin-top: 20px;">
                <div class="form-group">
                    <label for="password">Contraseña</label>
                    <input type="password" id="password" name="password" required>
                </div>
                <button type="submit" class="btn btn-primary">Generar Hash</button>
            </form>

        <?php elseif ($accion === 'agregar'): ?>
            
            <h2>➕ Agregar Nuevo Profesor</h2>
            <a href="?accion=menu" class="btn btn-secondary">← Volver</a>
            
            <?php
            if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['rut'])) {
                $profesores = cargarProfesores();
                
                $rut = trim($_POST['rut']);
                $nombre = trim($_POST['nombre']);
                $email = trim($_POST['email']);
                $password = $_POST['password'];
                
                if (isset($profesores[$rut])) {
                    echo '<div class="error" style="margin-top: 20px;">❌ Ya existe un profesor con ese RUT.</div>';
                } else {
                    $profesores[$rut] = [
                        'rut' => $rut,
                        'nombre' => $nombre,
                        'email' => $email,
                        'password_hash' => password_hash($password, PASSWORD_DEFAULT),
                        'created' => date('c'),
                        'activo' => true
                    ];
                    
                    guardarProfesores($profesores);
                    
                    echo '<div class="success" style="margin-top: 20px;">✅ Profesor agregado exitosamente.</div>';
                }
            }
            ?>
            
            <form method="POST" style="margin-top: 20px;">
                <div class="form-group">
                    <label for="rut">RUT *</label>
                    <input type="text" id="rut" name="rut" placeholder="12345678-9" required>
                </div>
                
                <div class="form-group">
                    <label for="nombre">Nombre Completo *</label>
                    <input type="text" id="nombre" name="nombre" placeholder="Dr. Juan Pérez" required>
                </div>
                
                <div class="form-group">
                    <label for="email">Email *</label>
                    <input type="email" id="email" name="email" placeholder="juan@universidad.cl" required>
                </div>
                
                <div class="form-group">
                    <label for="password">Contraseña *</label>
                    <input type="password" id="password" name="password" required>
                </div>
                
                <button type="submit" class="btn btn-success">Agregar Profesor</button>
            </form>

        <?php elseif ($accion === 'listar'): ?>
            
            <h2>📋 Lista de Profesores</h2>
            <a href="?accion=menu" class="btn btn-secondary">← Volver</a>
            
            <?php
            $profesores = cargarProfesores();
            if (empty($profesores)):
            ?>
                <p style="margin-top: 20px; color: #999;">No hay profesores registrados.</p>
            <?php else: ?>
                <div class="profesor-list">
                    <?php foreach ($profesores as $rut => $prof): ?>
                        <div class="profesor-item <?= $prof['activo'] ? '' : 'inactivo' ?>">
                            <strong><?= htmlspecialchars($prof['nombre']) ?></strong>
                            <br>RUT: <code><?= htmlspecialchars($rut) ?></code>
                            <br>Email: <?= htmlspecialchars($prof['email']) ?>
                            <br>Creado: <?= date('d/m/Y', strtotime($prof['created'])) ?>
                            <br>Estado: <?= $prof['activo'] ? '✅ Activo' : '❌ Inactivo' ?>
                        </div>
                    <?php endforeach; ?>
                </div>
            <?php endif; ?>

        <?php endif; ?>
        
    </div>
</body>
</html>