<?php
/**
 * profesor/estudiantes.php - Gestión de estudiantes por actividad
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
$actividad_id = $_GET['actividad'] ?? '';

// Verificar que la actividad existe y pertenece al profesor
$actividades = cargarJSON(ACTIVIDADES_FILE);
if (!isset($actividades[$actividad_id]) || $actividades[$actividad_id]['profesor_rut'] !== $rut) {
    header('Location: actividades.php');
    exit;
}

$actividad = $actividades[$actividad_id];

// Procesar CSV
if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_FILES['csv'])) {
    if ($_FILES['csv']['error'] === UPLOAD_ERR_OK) {
        $csv_path = $_FILES['csv']['tmp_name'];
        $estudiantes_db = cargarJSON(ESTUDIANTES_FILE);
        
        $agregados = 0;
        $errores = [];
        
        if (($handle = fopen($csv_path, 'r')) !== false) {
            // Saltar header
            $header = fgetcsv($handle);
            
            while (($data = fgetcsv($handle)) !== false) {
                if (count($data) >= 2) {
                    $est_rut = trim($data[0]);
                    $est_nombre = trim($data[1]);
                    $est_email = trim($data[2] ?? '');
                    $est_carrera = trim($data[3] ?? '');
                    $est_cohorte = trim($data[4] ?? '');
                    
                    if (empty($est_rut) || empty($est_nombre)) {
                        continue;
                    }
                    
                    // Crear o actualizar estudiante
                    if (!isset($estudiantes_db[$est_rut])) {
                        $estudiantes_db[$est_rut] = [
                            'rut' => $est_rut,
                            'nombre' => $est_nombre,
                            'email' => $est_email,
                            'carrera' => $est_carrera,
                            'cohorte' => $est_cohorte,
                            'created' => formatearFecha(),
                            'profesor_registro' => $rut,
                            'actividades' => [],
                            'activo' => true
                        ];
                    }
                    
                    // Agregar a la actividad si no está
                    if (!in_array($actividad_id, $estudiantes_db[$est_rut]['actividades'])) {
                        $estudiantes_db[$est_rut]['actividades'][] = $actividad_id;
                    }
                    
                    // Agregar a la lista de inscritos de la actividad
                    if (!in_array($est_rut, $actividades[$actividad_id]['configuracion']['estudiantes_inscritos'])) {
                        $actividades[$actividad_id]['configuracion']['estudiantes_inscritos'][] = $est_rut;
                        $agregados++;
                    }
                }
            }
            fclose($handle);
            
            // Actualizar estadísticas
            $actividades[$actividad_id]['estadisticas']['total_estudiantes'] = count($actividades[$actividad_id]['configuracion']['estudiantes_inscritos']);
            
            guardarJSON(ESTUDIANTES_FILE, $estudiantes_db);
            guardarJSON(ACTIVIDADES_FILE, $actividades);
            
            $mensaje = "Se agregaron {$agregados} estudiantes a la actividad";
            $tipo_mensaje = 'success';
        } else {
            $mensaje = 'Error al leer el archivo CSV';
            $tipo_mensaje = 'error';
        }
    } else {
        $mensaje = 'Error al subir el archivo';
        $tipo_mensaje = 'error';
    }
}

// Eliminar estudiante de la actividad
if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['eliminar_estudiante'])) {
    $est_rut = $_POST['estudiante_rut'];
    $estudiantes_db = cargarJSON(ESTUDIANTES_FILE);
    
    // Remover de la actividad
    $actividades[$actividad_id]['configuracion']['estudiantes_inscritos'] = array_values(
        array_filter(
            $actividades[$actividad_id]['configuracion']['estudiantes_inscritos'],
            fn($r) => $r !== $est_rut
        )
    );
    
    // Remover actividad del estudiante
    if (isset($estudiantes_db[$est_rut])) {
        $estudiantes_db[$est_rut]['actividades'] = array_values(
            array_filter(
                $estudiantes_db[$est_rut]['actividades'],
                fn($a) => $a !== $actividad_id
            )
        );
    }
    
    // Actualizar estadísticas
    $actividades[$actividad_id]['estadisticas']['total_estudiantes'] = count($actividades[$actividad_id]['configuracion']['estudiantes_inscritos']);
    
    guardarJSON(ESTUDIANTES_FILE, $estudiantes_db);
    guardarJSON(ACTIVIDADES_FILE, $actividades);
    
    $mensaje = 'Estudiante eliminado de la actividad';
    $tipo_mensaje = 'success';
}

// Recargar actividad
$actividades = cargarJSON(ACTIVIDADES_FILE);
$actividad = $actividades[$actividad_id];

// Cargar información de estudiantes
$estudiantes_db = cargarJSON(ESTUDIANTES_FILE);
$estudiantes_inscritos = [];
foreach ($actividad['configuracion']['estudiantes_inscritos'] as $est_rut) {
    if (isset($estudiantes_db[$est_rut])) {
        $estudiantes_inscritos[] = $estudiantes_db[$est_rut];
    }
}
?>
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Estudiantes - FisioaccessPC</title>
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
        
        .section-title {
            color: white;
            font-size: 18px;
            margin-bottom: 15px;
        }
        
        .upload-area {
            background: rgba(255, 255, 255, 0.1);
            border: 2px dashed rgba(255, 255, 255, 0.3);
            border-radius: 12px;
            padding: 30px;
            text-align: center;
            color: white;
        }
        
        .upload-icon {
            font-size: 48px;
            margin-bottom: 15px;
        }
        
        input[type="file"] {
            display: none;
        }
        
        .file-label {
            display: inline-block;
            padding: 10px 20px;
            background: white;
            color: #7c3aed;
            border-radius: 10px;
            cursor: pointer;
            font-weight: 600;
            transition: all 0.3s;
        }
        
        .file-label:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(255, 255, 255, 0.3);
        }
        
        .info-box {
            background: rgba(59, 130, 246, 0.2);
            border: 1px solid rgba(59, 130, 246, 0.4);
            border-radius: 12px;
            padding: 15px;
            margin-bottom: 20px;
            color: white;
            font-size: 14px;
        }
        
        .csv-example {
            background: rgba(0, 0, 0, 0.2);
            padding: 10px;
            border-radius: 8px;
            font-family: monospace;
            font-size: 12px;
            margin-top: 10px;
            overflow-x: auto;
        }
        
        .estudiantes-list {
            display: grid;
            gap: 10px;
        }
        
        .estudiante-card {
            background: rgba(255, 255, 255, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 10px;
            padding: 15px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            color: white;
        }
        
        .estudiante-info {
            flex: 1;
        }
        
        .estudiante-nombre {
            font-weight: 600;
            margin-bottom: 5px;
        }
        
        .estudiante-detalles {
            font-size: 13px;
            opacity: 0.8;
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
            <h1>👥 Estudiantes de la Actividad</h1>
            <div class="actividad-info">
                <strong><?= htmlspecialchars($actividad['info_basica']['nombre']) ?></strong><br>
                ID: <?= $actividad_id ?> • 
                <?= count($estudiantes_inscritos) ?> estudiantes inscritos
            </div>
        </div>
        
        <?php if ($mensaje): ?>
            <div class="mensaje <?= $tipo_mensaje ?>">
                <?= htmlspecialchars($mensaje) ?>
            </div>
        <?php endif; ?>
        
        <div class="card">
            <div class="section-title">📤 Subir Lista de Estudiantes (CSV)</div>
            
            <div class="info-box">
                <strong>📋 Formato del archivo CSV:</strong><br>
                El archivo debe tener las siguientes columnas en orden:<br>
                <code>rut, nombre, email, carrera, cohorte</code>
                
                <div class="csv-example">
rut,nombre,email,carrera,cohorte<br>
12345678-9,María López Silva,maria.lopez@estudiante.cl,Kinesiología,2023<br>
98765432-1,Pedro García Ruiz,pedro.garcia@estudiante.cl,Kinesiología,2023<br>
87654321-0,Ana Martínez Díaz,ana.martinez@estudiante.cl,Medicina,2024
                </div>
            </div>
            
            <form method="POST" enctype="multipart/form-data">
                <div class="upload-area">
                    <div class="upload-icon">📄</div>
                    <p style="margin-bottom: 15px;">Selecciona un archivo CSV con la lista de estudiantes</p>
                    <label for="csv-file" class="file-label">Seleccionar Archivo CSV</label>
                    <input type="file" id="csv-file" name="csv" accept=".csv" required onchange="mostrarNombre(this)">
                    <div id="file-name" style="margin-top: 10px; font-size: 14px;"></div>
                </div>
                <button type="submit" class="btn btn-primary" style="width: 100%; margin-top: 15px;">
                    Importar Estudiantes
                </button>
            </form>
        </div>
        
        <div class="card">
            <div class="section-title">
                📋 Lista de Estudiantes Inscritos (<?= count($estudiantes_inscritos) ?>)
            </div>
            
            <?php if (empty($estudiantes_inscritos)): ?>
                <p style="color: white; text-align: center; opacity: 0.8; padding: 20px;">
                    No hay estudiantes inscritos en esta actividad.<br>
                    Sube un archivo CSV para agregar estudiantes.
                </p>
            <?php else: ?>
                <div class="estudiantes-list">
                    <?php foreach ($estudiantes_inscritos as $est): ?>
                        <div class="estudiante-card">
                            <div class="estudiante-info">
                                <div class="estudiante-nombre"><?= htmlspecialchars($est['nombre']) ?></div>
                                <div class="estudiante-detalles">
                                    RUT: <?= htmlspecialchars($est['rut']) ?> • 
                                    <?= htmlspecialchars($est['email'] ?: 'Sin email') ?> • 
                                    <?= htmlspecialchars($est['carrera'] ?: 'Sin carrera') ?>
                                    <?= $est['cohorte'] ? ' • ' . htmlspecialchars($est['cohorte']) : '' ?>
                                </div>
                            </div>
                            <form method="POST" style="display: inline;" onsubmit="return confirm('¿Eliminar estudiante de esta actividad?')">
                                <input type="hidden" name="eliminar_estudiante" value="1">
                                <input type="hidden" name="estudiante_rut" value="<?= $est['rut'] ?>">
                                <button type="submit" class="btn btn-danger btn-small">🗑️ Eliminar</button>
                            </form>
                        </div>
                    <?php endforeach; ?>
                </div>
            <?php endif; ?>
        </div>
    </div>
    
    <script>
        function mostrarNombre(input) {
            const fileName = input.files[0]?.name || '';
            const display = document.getElementById('file-name');
            if (fileName) {
                display.textContent = '✅ Archivo seleccionado: ' + fileName;
            }
        }
    </script>
</body>
</html>