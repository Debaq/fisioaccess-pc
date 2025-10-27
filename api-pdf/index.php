<?php
/*  index.php – API completa para subir
 P DF  +  archivo crudo (opcional)                                              *
 Guarda ambos con el mismo serial y devuelve JSON con URLs y metadatos
 --------------------------------------------------------------*/
header('Content-Type: application/json');

/* ---------- 1. Método ---------- */
if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    http_response_code(405);
    echo json_encode(['error' => 'Método no permitido']);
    exit;
}

/* ---------- 2. PDF obligatorio ---------- */
if (!isset($_FILES['pdf']) || $_FILES['pdf']['error'] !== UPLOAD_ERR_OK) {
    http_response_code(400);
    echo json_encode(['error' => 'No se recibió el archivo PDF']);
    exit;
}

/* ---------- 3. RAW opcional ---------- */
$hasRaw = isset($_FILES['raw']) && $_FILES['raw']['error'] === UPLOAD_ERR_OK;

/* ---------- 4. Validar que el PDF sea PDF ---------- */
$finfo = finfo_open(FILEINFO_MIME_TYPE);
$mime  = finfo_file($finfo, $_FILES['pdf']['tmp_name']);
finfo_close($finfo);
if ($mime !== 'application/pdf') {
    http_response_code(400);
    echo json_encode(['error' => 'El archivo no es PDF']);
    exit;
}

/* ---------- 5. Campos obligatorios ---------- */
$required = ['owner', 'type', 'comments'];
foreach ($required as $f) {
    if (empty($_POST[$f])) {
        http_response_code(400);
        echo json_encode(['error' => "Falta el campo $f"]);
        exit;
    }
}

/* ---------- 6. Nombres únicos ---------- */
$baseName  = bin2hex(random_bytes(6)) . '_' . microtime(true);
$pdfName   = $baseName . '.pdf';
$rawName   = $baseName . '_raw.dat';
$uploadDir = __DIR__ . '/upload/';
$metaDir   = __DIR__ . '/data/';

if (!is_dir($uploadDir)) mkdir($uploadDir, 0755, true);
if (!is_dir($metaDir))   mkdir($metaDir,   0755, true);

$pdfPath = $uploadDir . $pdfName;
$rawPath = $uploadDir . $rawName;

/* ---------- 7. Mover archivos ---------- */
move_uploaded_file($_FILES['pdf']['tmp_name'], $pdfPath);
if ($hasRaw) {
    move_uploaded_file($_FILES['raw']['tmp_name'], $rawPath);
}

/* ---------- 8. Helper URL base ---------- */
function urlBase(): string
{
    $proto = (!empty($_SERVER['HTTPS']) && $_SERVER['HTTPS'] !== 'off') ? 'https' : 'http';
    return $proto . '://' . $_SERVER['HTTP_HOST'] . dirname($_SERVER['REQUEST_URI']);
}

/* ---------- 9. Construir metadatos ---------- */
$meta = [
    'filename'  => $pdfName,
'url'       => urlBase() . '/upload/' . $pdfName,
'size'      => filesize($pdfPath),
'uploaded'  => date('c'),
'owner'     => trim($_POST['owner']),
'type'      => trim($_POST['type']),
'comments'  => trim($_POST['comments']),
'raw'       => $hasRaw ? [
    'filename' => $rawName,
'url'      => urlBase() . '/upload/' . $rawName,
'size'     => filesize($rawPath)
] : null
];

/* ---------- 10. Guardar meta ---------- */
file_put_contents($metaDir . $baseName . '.json', json_encode($meta, JSON_PRETTY_PRINT));

/* ---------- 11. Responder ---------- */
echo json_encode(['url' => $meta['url'], 'raw' => $meta['raw'], 'meta' => $meta]);
