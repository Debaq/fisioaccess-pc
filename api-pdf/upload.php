<?php
/**
 * upload.php - Recibe archivos PDF y RAW con ID único pre-generado
 * 
 * POST con:
 *   - upload_id: ID único generado por generar_id.php
 *   - pdf: archivo PDF (requerido)
 *   - raw: archivo RAW/JSON (opcional)
 *   - owner: nombre del estudiante (opcional, se puede obtener de BD)
 */

header('Content-Type: application/json');

// Solo POST
if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    http_response_code(405);
    echo json_encode(['error' => 'Método no permitido']);
    exit;
}

$dataDir = __DIR__ . '/data/';
$reservasFile = $dataDir . 'reservas_ids.json';
$uploadBaseDir = $dataDir . 'uploads/';

// ========== VALIDAR UPLOAD_ID ==========
if (empty($_POST['upload_id'])) {
    http_response_code(400);
    echo json_encode(['error' => 'Falta el campo upload_id']);
    exit;
}

$uploadId = trim($_POST['upload_id']);

// ========== CARGAR Y VALIDAR RESERVA ==========
if (!file_exists($reservasFile)) {
    http_response_code(404);
    echo json_encode(['error' => 'No hay reservas de IDs']);
    exit;
}

$reservas = json_decode(file_get_contents($reservasFile), true) ?: [];

if (!isset($reservas[$uploadId])) {
    http_response_code(404);
    echo json_encode(['error' => 'ID de upload no encontrado o inválido']);
    exit;
}

$reserva = $reservas[$uploadId];

// ========== VALIDAR QUE NO HA EXPIRADO ==========
if ($reserva['expires_at'] < time()) {
    // Limpiar reserva expirada
    unset($reservas[$uploadId]);
    file_put_contents($reservasFile, json_encode($reservas, JSON_PRETTY_PRINT));
    
    http_response_code(410);
    echo json_encode(['error' => 'ID de upload expirado. Solicite uno nuevo.']);
    exit;
}

// ========== VALIDAR PDF ==========
if (!isset($_FILES['pdf']) || $_FILES['pdf']['error'] !== UPLOAD_ERR_OK) {
    http_response_code(400);
    echo json_encode(['error' => 'No se recibió el archivo PDF']);
    exit;
}

// Validar que sea PDF
$finfo = finfo_open(FILEINFO_MIME_TYPE);
$mime = finfo_file($finfo, $_FILES['pdf']['tmp_name']);
finfo_close($finfo);

if ($mime !== 'application/pdf') {
    http_response_code(400);
    echo json_encode(['error' => 'El archivo no es un PDF válido']);
    exit;
}

// ========== VALIDAR RAW (OPCIONAL) ==========
$hasRaw = isset($_FILES['raw']) && $_FILES['raw']['error'] === UPLOAD_ERR_OK;

// ========== CREAR ESTRUCTURA DE DIRECTORIOS ==========
$actividadId = $reserva['actividad_id'];
$actividadDir = $uploadBaseDir . $actividadId . '/';
$filesDir = $actividadDir . 'files/';

if (!is_dir($filesDir)) {
    mkdir($filesDir, 0755, true);
}

// ========== NOMBRES DE ARCHIVOS ==========
$pdfFilename = $uploadId . '.pdf';
$rawFilename = $uploadId . '_raw.dat';

$pdfPath = $filesDir . $pdfFilename;
$rawPath = $filesDir . $rawFilename;

// ========== MOVER ARCHIVOS ==========
if (!move_uploaded_file($_FILES['pdf']['tmp_name'], $pdfPath)) {
    http_response_code(500);
    echo json_encode(['error' => 'Error al guardar el archivo PDF']);
    exit;
}

if ($hasRaw) {
    move_uploaded_file($_FILES['raw']['tmp_name'], $rawPath);
}

// ========== HELPER URL BASE ==========
function urlBase(): string {
    $proto = (!empty($_SERVER['HTTPS']) && $_SERVER['HTTPS'] !== 'off') ? 'https' : 'http';
    return $proto . '://' . $_SERVER['HTTP_HOST'] . dirname($_SERVER['REQUEST_URI']);
}

// ========== CONSTRUIR METADATOS ==========
$metadata = [
    'upload_id' => $uploadId,
    'actividad_id' => $actividadId,
    'rut' => $reserva['rut'],
    'tipo' => $reserva['tipo'],
    'owner' => trim($_POST['owner'] ?? 'Estudiante'),
    'uploaded' => date('c'),
    'pdf' => [
        'filename' => $pdfFilename,
        'url' => urlBase() . '/data/uploads/' . $actividadId . '/files/' . $pdfFilename,
        'size' => filesize($pdfPath)
    ],
    'raw' => $hasRaw ? [
        'filename' => $rawFilename,
        'url' => urlBase() . '/data/uploads/' . $actividadId . '/files/' . $rawFilename,
        'size' => filesize($rawPath)
    ] : null
];

// ========== GUARDAR METADATA ==========
$metadataFile = $actividadDir . 'metadata_' . $uploadId . '.json';
file_put_contents($metadataFile, json_encode($metadata, JSON_PRETTY_PRINT));

// ========== ELIMINAR RESERVA USADA ==========
unset($reservas[$uploadId]);
file_put_contents($reservasFile, json_encode($reservas, JSON_PRETTY_PRINT));

// ========== RESPONDER ==========
http_response_code(200);
echo json_encode([
    'success' => true,
    'upload_id' => $uploadId,
    'actividad_id' => $actividadId,
    'pdf_url' => $metadata['pdf']['url'],
    'raw_url' => $metadata['raw']['url'] ?? null,
    'message' => 'Archivo subido exitosamente'
]);