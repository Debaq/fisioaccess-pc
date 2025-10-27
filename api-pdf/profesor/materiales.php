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
$actividad_id = $_GET['id'] ?? '';
$mensaje = '';
$tipo_mensaje = '';

// Verificar que la actividad existe y pertenece al profesor
$actividades = cargarJSON(ACTIVIDADES_FILE);
if (!isset($actividades[$actividad_id]) || $actividades[$actividad_id]['profesor_rut'] !== $rut) {
    header('Location: actividades.php');
    exit;
}

$actividad = $actividades[$actividad_id];
$materiales_dir = UPLOADS_PATH . '/' . $actividad_id . '/materiales';

// Subir guía de laboratorio
if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_FILES['guia'])) {
    if ($_FILES['guia']['error'] === UPLOAD_ERR_OK) {
        $filename = 'guia_laboratorio.pdf';
        $destination = $materiales_dir . '/' . $filename;
        
        if (move_uploaded_file($_FILES['guia']['tmp_name'], $destination)) {
            $actividades[$actividad_id]['material_pedagogico']['guia_laboratorio'] = [
                'filename' => $filename,
                'url' => 'data/uploads/' . $actividad_id . '/materiales/' . $filename,
                'uploaded' => formatearFecha()
            ];
            
            guardarJSON(ACTIVIDADES_FILE, $actividades);
            $mensaje = 'Guía de laboratorio subida exitosamente';
            $tipo_mensaje = 'success';
        } else {
            $mensaje = 'Error al subir la guía';
            $tipo_mensaje = 'error';
        }
    }
}

// Subir material complementario
if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_FILES['material'])) {
    if ($_FILES['material']['error'] === UPLOAD_ERR_OK) {
        $filename = time() . '_' . basename($_FILES['material']['name']);
        $destination = $materiales_dir . '/' . $filename;
        
        if (move_uploaded_file($_FILES['material']['tmp_name'], $destination)) {
            $tipo = $_POST['tipo_material'] ?? 'pdf';
            $titulo = $_POST['titulo_material'] ?? $filename;
            
            $actividades[$actividad_id]['material_pedagogico']['material_complementario'][] = [
                'tipo' => $tipo,
                'titulo' => $titulo,
                'filename' => $filename,
                'url' => 'data/uploads/' . $actividad_id . '/materiales/' . $filename,
                'uploaded' => formatearFecha()
            ];
            
            guardarJSON(ACTIVIDADES_FILE, $actividades);
            $mensaje = 'Material complementario subido exitosamente';
            $tipo_mensaje = 'success';
        }
    }
}

// Agregar link externo
if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['agregar_link'])) {
    $actividades[$actividad_id]['material_pedagogico']['material_complementario'][] = [
        'tipo' => 'link',
        'titulo' => trim($_POST['titulo_link']),
        'url' => trim($_POST['url_link']),
        'uploaded' => formatearFecha()
    ];
    
    guardarJSON(ACTIVIDADES_FILE, $actividades);
    $mensaje = 'Link agregado exitosamente';
    $tipo_mensaje = 'success';
}

// Eliminar material
if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['eliminar_material'])) {
    $index = intval($_POST['material_index']);
    
    if (isset($actividades[$actividad_id]['material_pedagogico']['material_complementario'][$index])) {
        $material = $actividades[$actividad_id]['material_pedagogico']['material_complementario'][$index];
        
        // Eliminar archivo si no es link
        if ($material['tipo'] !== 'link' && isset($material['filename'])) {
            $archivo = $materiales_dir . '/' . $material['filename'];
            if (file_exists($archivo)) {
                unlink($archivo);
            }
        }
        
        array_splice($actividades[$actividad_id]['material_pedagogico']['material_complementario'], $index, 1);
        guardarJSON(ACTIVIDADES_FILE, $actividades);
        
        $mensaje = 'Material eliminado exitosamente';
        $tipo_mensaje = 'success';
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
                                $icono = match($mat['tipo']) {
                                    'pdf' => '📄',
                                    'video' => '🎥',
                                    'imagen' => '🖼️',
                                    'link' => '🔗',
                                    default => '📎'
                                };
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