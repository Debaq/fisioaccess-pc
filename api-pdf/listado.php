<?php
header('Content-Type: application/json');

$metaDir = __DIR__ . '/data/';
$list    = [];

if (is_dir($metaDir)) {
    foreach (glob($metaDir . '*.json') as $file) {
        $list[] = json_decode(file_get_contents($file), true);
    }
}

echo json_encode($list);