<?php
/*
 * zaehler.php - zaehlt Seitenaufrufe fuer www.dertdler.de
 *
 * Wird von einem kleinen Skript am Ende jeder Seite aufgerufen und
 * schreibt reine Summen in daten/besuche-JJJJ-MM.json.
 *
 * Was NICHT gespeichert wird: IP-Adressen, Cookies, Kennungen,
 * irgendetwas, womit sich ein einzelner Besucher wiedererkennen liesse.
 * Gezaehlt werden nur: Tag, Seite, Herkunftsseite, Sprachfassung.
 *
 * Auswertung: statistik.php
 */

// Antwort ist immer ein 1x1-Pixel, egal was passiert.
function pixel() {
    header('Content-Type: image/gif');
    header('Cache-Control: no-store, no-cache, must-revalidate');
    header('Pragma: no-cache');
    echo base64_decode('R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7');
    exit;
}

$kennung = isset($_SERVER['HTTP_USER_AGENT']) ? strtolower($_SERVER['HTTP_USER_AGENT']) : '';
foreach (array('bot','crawl','spider','slurp','headless','curl','wget','python','monitor','preview','fetch') as $wort) {
    if (strpos($kennung, $wort) !== false) { pixel(); }
}

$seite = isset($_GET['s']) ? $_GET['s'] : '/';
$seite = preg_replace('/[?#].*$/', '', $seite);
if (strlen($seite) > 120 || !preg_match('#^/[A-Za-z0-9._/-]*$#', $seite)) { pixel(); }

$sprache = 'de';
if (preg_match('#^/(en|fr|pl)(/|$)#', $seite, $t)) {
    $sprache = $t[1];
    $seite = substr($seite, 3);
}
if ($seite === '' || substr($seite, -1) === '/') { $seite .= 'index.html'; }

$herkunft = '(direkt)';
if (!empty($_GET['h'])) {
    $wirt = parse_url($_GET['h'], PHP_URL_HOST);
    if ($wirt) {
        $wirt = strtolower(preg_replace('/^www\./', '', $wirt));
        if (strpos($wirt, 'dertdler.de') === false && preg_match('/^[a-z0-9.-]{3,60}$/', $wirt)) {
            $herkunft = $wirt;
        } else {
            pixel();   // Klick innerhalb der eigenen Seite zaehlt als Seitenaufruf, nicht als Herkunft
        }
    }
}

$ordner = __DIR__ . '/daten';
if (!is_dir($ordner)) {
    @mkdir($ordner, 0755);
    @file_put_contents($ordner . '/.htaccess',
        "<IfModule mod_authz_core.c>\nRequire all denied\n</IfModule>\n" .
        "<IfModule !mod_authz_core.c>\nDeny from all\n</IfModule>\n");
    @file_put_contents($ordner . '/index.html', "<!doctype html><title>.</title>");
}

$datei = $ordner . '/besuche-' . date('Y-m') . '.json';
$griff = @fopen($datei, 'c+');
if (!$griff) { pixel(); }

if (flock($griff, LOCK_EX)) {
    $inhalt = stream_get_contents($griff);
    $d = $inhalt ? json_decode($inhalt, true) : null;
    if (!is_array($d)) { $d = array('tage' => array(), 'seiten' => array(), 'herkunft' => array(), 'sprachen' => array()); }

    $heute = date('Y-m-d');
    $d['tage'][$heute]        = (isset($d['tage'][$heute]) ? $d['tage'][$heute] : 0) + 1;
    $d['seiten'][$seite]      = (isset($d['seiten'][$seite]) ? $d['seiten'][$seite] : 0) + 1;
    $d['sprachen'][$sprache]  = (isset($d['sprachen'][$sprache]) ? $d['sprachen'][$sprache] : 0) + 1;
    $d['herkunft'][$herkunft] = (isset($d['herkunft'][$herkunft]) ? $d['herkunft'][$herkunft] : 0) + 1;

    ftruncate($griff, 0);
    rewind($griff);
    fwrite($griff, json_encode($d));
    fflush($griff);
    flock($griff, LOCK_UN);
}
fclose($griff);
pixel();
