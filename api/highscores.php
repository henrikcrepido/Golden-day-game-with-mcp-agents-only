<?php
/**
 * Highscores API handler for IIS + PHP deployments.
 *
 * Mirrors the REST API provided by server.py so the HTML games work
 * without any Python installation.
 *
 * Routes (configured via web.config URL Rewrite):
 *   GET  /api/highscores/{key}  → return stored scores as JSON array
 *   POST /api/highscores/{key}  → persist a JSON array of scores to disk
 *
 * The {key} value is passed as the query-string parameter "key" by the
 * rewrite rule in web.config.
 *
 * Data is stored in the data/ folder next to this file's parent directory:
 *   <site-root>/data/{key}.json
 *
 * IIS application-pool identity must have write access to the data/ folder.
 */

header('Content-Type: application/json; charset=utf-8');
header('Cache-Control: no-cache, no-store, must-revalidate');

// ── Validate key ──────────────────────────────────────────────────────────────
$key = isset($_GET['key']) ? $_GET['key'] : '';
if (!preg_match('/^[a-zA-Z0-9_-]{1,64}$/', $key)) {
    http_response_code(400);
    echo '{"error":"Invalid key"}';
    exit;
}

// ── Resolve data directory ────────────────────────────────────────────────────
// __DIR__ is <site-root>/api  →  parent is <site-root>
$dataDir = dirname(__DIR__) . DIRECTORY_SEPARATOR . 'data';
if (!is_dir($dataDir)) {
    if (!mkdir($dataDir, 0755, true)) {
        http_response_code(500);
        echo '{"error":"Cannot create data directory"}';
        exit;
    }
}

$filepath = $dataDir . DIRECTORY_SEPARATOR . $key . '.json';
$method   = $_SERVER['REQUEST_METHOD'];

// ── GET ───────────────────────────────────────────────────────────────────────
if ($method === 'GET') {
    if (file_exists($filepath)) {
        $data = file_get_contents($filepath);
        if ($data === false) {
            http_response_code(500);
            echo '{"error":"Failed to read file"}';
            exit;
        }
        echo $data;
    } else {
        echo '[]';
    }
    exit;
}

// ── POST ──────────────────────────────────────────────────────────────────────
if ($method === 'POST') {
    $body = file_get_contents('php://input');
    if ($body === false || $body === '') {
        http_response_code(400);
        echo '{"error":"Empty request body"}';
        exit;
    }

    $scores = json_decode($body, true);
    if (!is_array($scores)) {
        http_response_code(400);
        echo '{"error":"Payload must be a JSON array"}';
        exit;
    }

    // Write atomically: temp file then rename to avoid partial reads.
    $tmpPath = $filepath . '.tmp';
    $json    = json_encode($scores, JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE);
    if (file_put_contents($tmpPath, $json, LOCK_EX) === false) {
        http_response_code(500);
        echo '{"error":"Failed to write file"}';
        exit;
    }
    if (!rename($tmpPath, $filepath)) {
        @unlink($tmpPath);
        http_response_code(500);
        echo '{"error":"Failed to save file"}';
        exit;
    }

    echo '{"ok":true}';
    exit;
}

// ── Other methods ─────────────────────────────────────────────────────────────
http_response_code(405);
header('Allow: GET, POST');
echo '{"error":"Method Not Allowed"}';
