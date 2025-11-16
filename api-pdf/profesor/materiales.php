<?php
/**
 * profesor/materiales.php - Subir material pedagógico de actividad
 */

require_once '../config.php';

session_start();

if (!verificarRol('profesor')) {
    header('Location: login.php');
    exit;
}

$rut = $_SESSION['rut'];

// Sanitizar y validar actividad_id
$actividad_id = sanitizarString($_GET['id'] ?? '', ['max_length' => 50]);

if (empty($actividad_id)) {
    header('Location: actividades.php');
    exit;
}

// Prevenir path traversal
if (preg_match('/[\.\/\\\\]/', $actividad_id)) {
    registrarEventoSeguridad('Intento de path traversal en materiales', [
        'actividad_id' => $actividad_id,
        'profesor_rut' => $rut,
        'ip' => obtenerIP()
    ]);
    header('Location: actividades.php');
    exit;
}

$mensaje = '';
$tipo_mensaje = '';

// Verificar que la actividad existe y pertenece al profesor
$actividades = cargarJSON(ACTIVIDADES_FILE);
if (!isset($actividades[$actividad_id]) || $actividades[$actividad_id]['profesor_rut'] !== $rut) {
    registrarEventoSeguridad('Intento de acceso no autorizado a materiales de actividad', [
        'actividad_id' => $actividad_id,
        'profesor_rut' => $rut,
        'ip' => obtenerIP()
    ]);
    header('Location: actividades.php');
    exit;
}

$actividad = $actividades[$actividad_id];
$materiales_dir = UPLOADS_PATH . '/' . $actividad_id . '/materiales';

// Subir guía de laboratorio
if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_FILES['guia'])) {
    // Validar CSRF token
    $csrf_token = $_POST['csrf_token'] ?? '';
    if (!validarTokenCSRF($csrf_token)) {
        $mensaje = 'Token de seguridad inválido. Intenta nuevamente.';
        $tipo_mensaje = 'error';
        registrarEventoSeguridad('CSRF token inválido en upload guía', [
            'profesor_rut' => $rut,
            'actividad_id' => $actividad_id,
            'ip' => obtenerIP()
        ]);
    } elseif ($_FILES['guia']['error'] === UPLOAD_ERR_OK) {
        // Validar extensión (solo PDF)
        $ext = strtolower(pathinfo($_FILES['guia']['name'], PATHINFO_EXTENSION));
        if ($ext !== 'pdf') {
            $mensaje = 'Solo se permiten archivos PDF para la guía de laboratorio';
            $tipo_mensaje = 'error';
        } elseif ($_FILES['guia']['size'] > PDF_MAX_SIZE) {
            $mensaje = 'El archivo excede el tamaño máximo permitido (' . (PDF_MAX_SIZE / 1024 / 1024) . ' MB)';
            $tipo_mensaje = 'error';
        } else {
            $filename = 'guia_laboratorio.pdf';
            $destination = $materiales_dir . '/' . $filename;

            // Validar path de destino
            if (!is_dir($materiales_dir)) {
                mkdir($materiales_dir, 0755, true);
            }

            $real_dest = realpath(dirname($destination));
            $real_base = realpath(UPLOADS_PATH);
            if ($real_dest === false || strpos($real_dest, $real_base) !== 0) {
                $mensaje = 'Ruta de destino inválida';
                $tipo_mensaje = 'error';
                registrarEventoSeguridad('Intento de path traversal en destino de archivo', [
                    'destination' => $destination,
                    'profesor_rut' => $rut,
                    'ip' => obtenerIP()
                ]);
            } elseif (move_uploaded_file($_FILES['guia']['tmp_name'], $destination)) {
                $actividades[$actividad_id]['material_pedagogico']['guia_laboratorio'] = [
                    'filename' => $filename,
                    'url' => 'data/uploads/' . $actividad_id . '/materiales/' . $filename,
                    'uploaded' => formatearFecha()
                ];

                guardarJSON(ACTIVIDADES_FILE, $actividades);

                // Logging
                registrarLog('INFO', 'Guía de laboratorio subida', [
                    'actividad_id' => $actividad_id,
                    'profesor_rut' => $rut,
                    'filename' => $filename,
                    'size' => $_FILES['guia']['size'],
                    'ip' => obtenerIP()
                ]);

                $mensaje = 'Guía de laboratorio subida exitosamente';
                $tipo_mensaje = 'success';
            } else {
                $mensaje = 'Error al subir la guía';
                $tipo_mensaje = 'error';
            }
        }
    }
}

// Subir material complementario
if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_FILES['material'])) {
    // Validar CSRF token
    $csrf_token = $_POST['csrf_token'] ?? '';
    if (!validarTokenCSRF($csrf_token)) {
        $mensaje = 'Token de seguridad inválido. Intenta nuevamente.';
        $tipo_mensaje = 'error';
        registrarEventoSeguridad('CSRF token inválido en upload material', [
            'profesor_rut' => $rut,
            'actividad_id' => $actividad_id,
            'ip' => obtenerIP()
        ]);
    } elseif ($_FILES['material']['error'] === UPLOAD_ERR_OK) {
        // Sanitizar inputs
        $tipo = sanitizarString($_POST['tipo_material'] ?? 'pdf', ['max_length' => 20]);
        $titulo = sanitizarString($_POST['titulo_material'] ?? '', ['max_length' => 200]);

        // Validar tipo contra whitelist
        $tipos_validos = ['pdf', 'video', 'imagen', 'otro'];
        if (!in_array($tipo, $tipos_validos)) {
            $mensaje = 'Tipo de material inválido';
            $tipo_mensaje = 'error';
        } elseif (validarNoVacio($titulo) !== true) {
            $mensaje = 'El título es requerido';
            $tipo_mensaje = 'error';
        } else {
            // Validar extensión de archivo
            $ext = strtolower(pathinfo($_FILES['material']['name'], PATHINFO_EXTENSION));
            $extensiones_permitidas = ['pdf', 'doc', 'docx', 'ppt', 'pptx', 'xls', 'xlsx', 'jpg', 'jpeg', 'png', 'gif', 'mp4', 'avi', 'mov', 'zip'];

            if (!in_array($ext, $extensiones_permitidas)) {
                $mensaje = 'Tipo de archivo no permitido. Extensiones permitidas: ' . implode(', ', $extensiones_permitidas);
                $tipo_mensaje = 'error';
            } elseif ($_FILES['material']['size'] > PDF_MAX_SIZE) {
                $mensaje = 'El archivo excede el tamaño máximo permitido (' . (PDF_MAX_SIZE / 1024 / 1024) . ' MB)';
                $tipo_mensaje = 'error';
            } else {
                // Generar nombre seguro (sin usar nombre original directamente)
                $filename = time() . '_' . bin2hex(random_bytes(8)) . '.' . $ext;
                $destination = $materiales_dir . '/' . $filename;

                // Validar path de destino
                if (!is_dir($materiales_dir)) {
                    mkdir($materiales_dir, 0755, true);
                }

                $real_dest = realpath(dirname($destination));
                $real_base = realpath(UPLOADS_PATH);
                if ($real_dest === false || strpos($real_dest, $real_base) !== 0) {
                    $mensaje = 'Ruta de destino inválida';
                    $tipo_mensaje = 'error';
                    registrarEventoSeguridad('Intento de path traversal en destino de material', [
                        'destination' => $destination,
                        'profesor_rut' => $rut,
                        'ip' => obtenerIP()
                    ]);
                } elseif (move_uploaded_file($_FILES['material']['tmp_name'], $destination)) {
                    $actividades[$actividad_id]['material_pedagogico']['material_complementario'][] = [
                        'tipo' => $tipo,
                        'titulo' => $titulo,
                        'filename' => $filename,
                        'url' => 'data/uploads/' . $actividad_id . '/materiales/' . $filename,
                        'uploaded' => formatearFecha()
                    ];

                    guardarJSON(ACTIVIDADES_FILE, $actividades);

                    // Logging
                    registrarLog('INFO', 'Material complementario subido', [
                        'actividad_id' => $actividad_id,
                        'profesor_rut' => $rut,
                        'tipo' => $tipo,
                        'titulo' => $titulo,
                        'filename' => $filename,
                        'size' => $_FILES['material']['size'],
                        'ip' => obtenerIP()
                    ]);

                    $mensaje = 'Material complementario subido exitosamente';
                    $tipo_mensaje = 'success';
                } else {
                    $mensaje = 'Error al subir el material';
                    $tipo_mensaje = 'error';
                }
            }
        }
    }
}

// Agregar link externo
if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['agregar_link'])) {
    // Validar CSRF token
    $csrf_token = $_POST['csrf_token'] ?? '';
    if (!validarTokenCSRF($csrf_token)) {
        $mensaje = 'Token de seguridad inválido. Intenta nuevamente.';
        $tipo_mensaje = 'error';
        registrarEventoSeguridad('CSRF token inválido en agregar link', [
            'profesor_rut' => $rut,
            'actividad_id' => $actividad_id,
            'ip' => obtenerIP()
        ]);
    } else {
        // Sanitizar inputs
        $titulo_link = sanitizarString($_POST['titulo_link'] ?? '', ['max_length' => 200]);
        $url_link = sanitizarString($_POST['url_link'] ?? '', ['max_length' => 500]);

        // Validar título
        if (validarNoVacio($titulo_link) !== true) {
            $mensaje = 'El título del link es requerido';
            $tipo_mensaje = 'error';
        } elseif (validarNoVacio($url_link) !== true) {
            $mensaje = 'La URL es requerida';
            $tipo_mensaje = 'error';
        } else {
            // Validar URL
            $url_validada = filter_var($url_link, FILTER_VALIDATE_URL);
            if ($url_validada === false) {
                $mensaje = 'URL inválida. Debe comenzar con http:// o https://';
                $tipo_mensaje = 'error';
            } else {
                $actividades[$actividad_id]['material_pedagogico']['material_complementario'][] = [
                    'tipo' => 'link',
                    'titulo' => $titulo_link,
                    'url' => $url_validada,
                    'uploaded' => formatearFecha()
                ];

                guardarJSON(ACTIVIDADES_FILE, $actividades);

                // Logging
                registrarLog('INFO', 'Link externo agregado', [
                    'actividad_id' => $actividad_id,
                    'profesor_rut' => $rut,
                    'titulo' => $titulo_link,
                    'url' => $url_validada,
                    'ip' => obtenerIP()
                ]);

                $mensaje = 'Link agregado exitosamente';
                $tipo_mensaje = 'success';
            }
        }
    }
}

// Eliminar material
if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['eliminar_material'])) {
    // Validar CSRF token
    $csrf_token = $_POST['csrf_token'] ?? '';
    if (!validarTokenCSRF($csrf_token)) {
        $mensaje = 'Token de seguridad inválido. Intenta nuevamente.';
        $tipo_mensaje = 'error';
        registrarEventoSeguridad('CSRF token inválido en eliminar material', [
            'profesor_rut' => $rut,
            'actividad_id' => $actividad_id,
            'ip' => obtenerIP()
        ]);
    } else {
        $index = intval($_POST['material_index'] ?? -1);

        // Validar que el índice existe
        if ($index < 0 || !isset($actividades[$actividad_id]['material_pedagogico']['material_complementario'][$index])) {
            $mensaje = 'Material no encontrado';
            $tipo_mensaje = 'error';
        } else {
            $material = $actividades[$actividad_id]['material_pedagogico']['material_complementario'][$index];

            // Eliminar archivo si no es link
            if ($material['tipo'] !== 'link' && isset($material['filename'])) {
                // Sanitizar filename y prevenir path traversal
                $filename = basename($material['filename']);
                $archivo = $materiales_dir . '/' . $filename;

                // Validar que el archivo está dentro del directorio permitido
                $real_file = realpath($archivo);
                $real_base = realpath($materiales_dir);
                if ($real_file !== false && strpos($real_file, $real_base) === 0 && file_exists($archivo)) {
                    unlink($archivo);
                }
            }

            array_splice($actividades[$actividad_id]['material_pedagogico']['material_complementario'], $index, 1);
            guardarJSON(ACTIVIDADES_FILE, $actividades);

            // Logging
            registrarLog('INFO', 'Material eliminado', [
                'actividad_id' => $actividad_id,
                'profesor_rut' => $rut,
                'material_tipo' => $material['tipo'],
                'material_titulo' => $material['titulo'],
                'ip' => obtenerIP()
            ]);

            $mensaje = 'Material eliminado exitosamente';
            $tipo_mensaje = 'success';
        }
    }
}

// Recargar actividad
$actividades = cargarJSON(ACTIVIDADES_FILE);
$actividad = $actividades[$actividad_id];
?>
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Material Pedagógico - FisioaccessPC</title>
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
            max-width: 900px;
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
        
        .card {
            background: rgba(255, 255, 255, 0.15);
            backdrop-filter: blur(10px);
            border-radius: 16px;
            border: 1px solid rgba(255, 255, 255, 0.3);
            padding: 25px;
            margin-bottom: 20px;
        }
        
        .section-title {
            color: white;
            font-size: 18px;
            margin-bottom: 15px;
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
        
        input:focus, select:focus {
            outline: none;
            border-color: rgba(255, 255, 255, 0.6);
            background: rgba(255, 255, 255, 0.15);
        }
        
        input[type="file"] {
            padding: 8px;
        }
        
        .material-item {
            background: rgba(255, 255, 255, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 10px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            color: white;
        }
        
        .material-info {
            flex: 1;
        }
        
        .material-titulo {
            font-weight: 600;
            margin-bottom: 5px;
        }
        
        .material-detalles {
            font-size: 13px;
            opacity: 0.8;
        }
        
        .badge {
            display: inline-block;
            padding: 4px 10px;
            border-radius: 6px;
            font-size: 12px;
            font-weight: 600;
            background: rgba(59, 130, 246, 0.3);
            border: 1px solid rgba(59, 130, 246, 0.5);
        }
    </style>
</head>
<body>
    <div class="navbar">
        <div class="navbar-brand">🫁 FisioaccessPC</div>
        <a href="actividades.php" class="btn btn-secondary btn-small">← Volver a Actividades</a>
    </div>
    
    <div class="container">
        <div class="header">
            <h1>📎 Material Pedagógico</h1>
            <div class="actividad-info">
                <strong><?= htmlspecialchars($actividad['info_basica']['nombre']) ?></strong><br>
                ID: <?= $actividad_id ?>
            </div>
        </div>
        
        <?php if ($mensaje): ?>
            <div class="mensaje <?= $tipo_mensaje ?>">
                <?= htmlspecialchars($mensaje) ?>
            </div>
        <?php endif; ?>
        
        <!-- Guía de Laboratorio -->
        <div class="card">
            <div class="section-title">📘 Guía de Laboratorio (PDF Principal)</div>
            
            <?php if ($actividad['material_pedagogico']['guia_laboratorio']): ?>
                <div class="material-item">
                    <div class="material-info">
                        <div class="material-titulo">
                            📄 <?= htmlspecialchars($actividad['material_pedagogico']['guia_laboratorio']['filename']) ?>
                        </div>
                        <div class="material-detalles">
                            Subido: <?= date('d/m/Y H:i', strtotime($actividad['material_pedagogico']['guia_laboratorio']['uploaded'])) ?>
                        </div>
                    </div>
                    <a href="../<?= $actividad['material_pedagogico']['guia_laboratorio']['url'] ?>" 
                       class="btn btn-secondary btn-small" target="_blank">Ver PDF</a>
                </div>
            <?php endif; ?>
            
            <form method="POST" enctype="multipart/form-data">
                <input type="hidden" name="csrf_token" value="<?= generarTokenCSRF() ?>">
                <div class="form-group">
                    <label>Subir Guía de Laboratorio (reemplaza la anterior)</label>
                    <input type="file" name="guia" accept=".pdf" required>
                </div>
                <button type="submit" class="btn btn-primary">
                    <?= $actividad['material_pedagogico']['guia_laboratorio'] ? 'Reemplazar' : 'Subir' ?> Guía
                </button>
            </form>
        </div>
        
        <!-- Material Complementario (Archivos) -->
        <div class="card">
            <div class="section-title">📚 Material Complementario (Archivos)</div>
            
            <form method="POST" enctype="multipart/form-data">
                <input type="hidden" name="csrf_token" value="<?= generarTokenCSRF() ?>">
                <div class="form-group">
                    <label>Título del Material</label>
                    <input type="text" name="titulo_material" placeholder="Ej: Paper de Miller et al. 2005" required>
                </div>

                <div class="form-group">
                    <label>Tipo</label>
                    <select name="tipo_material">
                        <option value="pdf">PDF / Documento</option>
                        <option value="video">Video</option>
                        <option value="imagen">Imagen</option>
                        <option value="otro">Otro</option>
                    </select>
                </div>

                <div class="form-group">
                    <label>Archivo</label>
                    <input type="file" name="material" required>
                </div>

                <button type="submit" class="btn btn-primary">Subir Material</button>
            </form>
        </div>
        
        <!-- Links Externos -->
        <div class="card">
            <div class="section-title">🔗 Links Externos</div>
            
            <form method="POST">
                <input type="hidden" name="csrf_token" value="<?= generarTokenCSRF() ?>">
                <input type="hidden" name="agregar_link" value="1">

                <div class="form-group">
                    <label>Título del Link</label>
                    <input type="text" name="titulo_link" placeholder="Ej: Calculadora de valores predichos" required>
                </div>

                <div class="form-group">
                    <label>URL</label>
                    <input type="url" name="url_link" placeholder="https://ejemplo.com" required>
                </div>

                <button type="submit" class="btn btn-primary">Agregar Link</button>
            </form>
        </div>
        
        <!-- Lista de Material Complementario -->
        <?php if (!empty($actividad['material_pedagogico']['material_complementario'])): ?>
            <div class="card">
                <div class="section-title">
                    📋 Material Complementario Agregado (<?= count($actividad['material_pedagogico']['material_complementario']) ?>)
                </div>
                
                <?php foreach ($actividad['material_pedagogico']['material_complementario'] as $index => $mat): ?>
                    <div class="material-item">
                        <div class="material-info">
                            <div class="material-titulo">
                                <?php
                                $icono = '📎'; // default
                                switch($mat['tipo']) {
                                    case 'pdf': $icono = '📄'; break;
                                    case 'video': $icono = '🎥'; break;
                                    case 'imagen': $icono = '🖼️'; break;
                                    case 'link': $icono = '🔗'; break;
                                }
                                echo $icono;
                                ?> <?= htmlspecialchars($mat['titulo']) ?>
                            </div>
                            <div class="material-detalles">
                                <span class="badge"><?= strtoupper($mat['tipo']) ?></span> • 
                                <?= date('d/m/Y H:i', strtotime($mat['uploaded'])) ?>
                            </div>
                        </div>
                        <div style="display: flex; gap: 10px;">
                            <?php if ($mat['tipo'] === 'link'): ?>
                                <a href="<?= htmlspecialchars($mat['url']) ?>" class="btn btn-secondary btn-small" target="_blank">Abrir</a>
                            <?php else: ?>
                                <a href="../<?= $mat['url'] ?>" class="btn btn-secondary btn-small" target="_blank">Descargar</a>
                            <?php endif; ?>
                            <form method="POST" style="display: inline;" onsubmit="return confirm('¿Eliminar este material?')">
                                <input type="hidden" name="csrf_token" value="<?= generarTokenCSRF() ?>">
                                <input type="hidden" name="eliminar_material" value="1">
                                <input type="hidden" name="material_index" value="<?= $index ?>">
                                <button type="submit" class="btn btn-danger btn-small">🗑️</button>
                            </form>
                        </div>
                    </div>
                <?php endforeach; ?>
            </div>
        <?php endif; ?>
    </div>
</body>
</html>
