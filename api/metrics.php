<?php
// File: metrics.php
// Path: /home/herb/Desktop/OurLibrary/api/metrics.php
// Standard: AIDEV-PascalCase-2.3
// Created: 2025-01-23
// Last Modified: 2025-01-23 02:50PM

/**
 * OurLibrary Metrics Collection API
 * Handles anonymous usage metrics from the library application
 * Forwards metrics to Google Drive for analysis
 */

header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: POST, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type');

// Handle preflight OPTIONS request
if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    http_response_code(200);
    exit();
}

// Only accept POST requests
if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    http_response_code(405);
    echo json_encode(['error' => 'Method not allowed']);
    exit();
}

try {
    // Get JSON input
    $input = file_get_contents('php://input');
    $data = json_decode($input, true);
    
    if (!$data || !isset($data['metrics'])) {
        throw new Exception('Invalid input data');
    }
    
    $metrics = $data['metrics'];
    $timestamp = $data['timestamp'] ?? time() * 1000;
    
    // Validate and sanitize metrics
    $sanitizedMetrics = [];
    foreach ($metrics as $metric) {
        $sanitizedMetric = [
            'timestamp' => (int)($metric['timestamp'] ?? $timestamp),
            'action' => sanitizeString($metric['action'] ?? 'unknown'),
            'bookId' => (int)($metric['bookId'] ?? 0),
            'metadata' => sanitizeMetadata($metric['metadata'] ?? []),
            'userAgent' => sanitizeString(substr($metric['userAgent'] ?? '', 0, 50)),
            'sessionId' => sanitizeString($metric['sessionId'] ?? 'unknown')
        ];
        $sanitizedMetrics[] = $sanitizedMetric;
    }
    
    // Prepare data for Google Drive storage
    $metricsData = [
        'batch_timestamp' => $timestamp,
        'batch_size' => count($sanitizedMetrics),
        'metrics' => $sanitizedMetrics,
        'server_timestamp' => time() * 1000,
        'source' => 'ourlibrary_web'
    ];
    
    // Save to local log file (backup)
    $logFile = '../data/metrics_' . date('Y-m-d') . '.log';
    $logEntry = date('Y-m-d H:i:s') . ' ' . json_encode($metricsData) . "\n";
    file_put_contents($logFile, $logEntry, FILE_APPEND | LOCK_EX);
    
    // Forward to Google Drive (via Google Apps Script or Drive API)
    $gdriveSuccess = forwardToGoogleDrive($metricsData);
    
    // Return success response
    echo json_encode([
        'success' => true,
        'processed' => count($sanitizedMetrics),
        'gdrive_synced' => $gdriveSuccess,
        'timestamp' => $timestamp
    ]);
    
} catch (Exception $e) {
    http_response_code(400);
    echo json_encode([
        'error' => 'Failed to process metrics',
        'message' => $e->getMessage()
    ]);
}

/**
 * Sanitize string input
 */
function sanitizeString($str) {
    if (!is_string($str)) return '';
    return htmlspecialchars(strip_tags(trim($str)), ENT_QUOTES, 'UTF-8');
}

/**
 * Sanitize metadata array
 */
function sanitizeMetadata($metadata) {
    if (!is_array($metadata)) return [];
    
    $sanitized = [];
    foreach ($metadata as $key => $value) {
        if (is_string($key) && (is_string($value) || is_numeric($value))) {
            $sanitized[sanitizeString($key)] = is_string($value) ? 
                sanitizeString($value) : $value;
        }
    }
    return $sanitized;
}

/**
 * Forward metrics to Google Drive
 * This would integrate with your Google Drive service account
 */
function forwardToGoogleDrive($metricsData) {
    try {
        // In production, this would use Google Drive API
        // with your anderson-library-service@anderson-library.iam.gserviceaccount.com
        
        // For now, save to local file that can be manually uploaded
        $gdriveFile = '../data/gdrive_metrics_' . date('Y-m-d_H-i-s') . '.json';
        $result = file_put_contents($gdriveFile, json_encode($metricsData, JSON_PRETTY_PRINT));
        
        return $result !== false;
        
    } catch (Exception $e) {
        error_log('Google Drive sync failed: ' . $e->getMessage());
        return false;
    }
}
?>