<?php
/*
 * statistik.php - Auswertung der Zaehlerdaten aus daten/
 *
 * Aufruf:  https://www.dertdler.de/statistik.php
 *
 * Das Kennwort steht in der naechsten Zeile. Aendere es in etwas,
 * das nur du kennst, und lade die Datei danach neu hoch.
 */
$KENNWORT = 'Anja020875##7';

session_start();
if (isset($_GET['ende'])) { session_destroy(); header('Location: statistik.php'); exit; }
if (isset($_POST['kennwort'])) {
    if (hash_equals($KENNWORT, (string)$_POST['kennwort'])) { $_SESSION['offen'] = true; }
    else { $fehler = 'Das war nicht das richtige Kennwort.'; }
}
$offen = !empty($_SESSION['offen']);

$ordner = __DIR__ . '/daten';
$monate = array();
foreach (glob($ordner . '/besuche-*.json') as $pfad) {
    if (preg_match('/besuche-(\d{4}-\d{2})\.json$/', $pfad, $t)) { $monate[$t[1]] = $pfad; }
}
krsort($monate);
$monat = isset($_GET['m']) && isset($monate[$_GET['m']]) ? $_GET['m'] : key($monate);
$d = array('tage' => array(), 'seiten' => array(), 'herkunft' => array(), 'sprachen' => array());
if ($monat && isset($monate[$monat])) {
    $roh = json_decode(@file_get_contents($monate[$monat]), true);
    if (is_array($roh)) { $d = array_merge($d, $roh); }
}
$gesamt = array_sum($d['tage']);
$MONATSNAME = array(1=>'Januar','Februar','M&auml;rz','April','Mai','Juni','Juli','August','September','Oktober','November','Dezember');
function h($s) { return htmlspecialchars((string)$s, ENT_QUOTES, 'UTF-8'); }
function oben($feld, $anzahl) { arsort($feld); return array_slice($feld, 0, $anzahl, true); }
?>
<!doctype html>
<html lang="de">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow">
<title>Besuche &middot; dertdler.de</title>
<style>
  :root{ --schwarz:#0B0A08; --russ:#131110; --erhoben:#191614;
         --gold:#C79C5E; --gold-hell:#E6CB99; --bein:#F3EEE4;
         --asche:#9C9289; --linie:#2A2521; }
  *{ box-sizing:border-box; }
  body{ margin:0; padding:32px 20px 64px; background:var(--schwarz); color:var(--bein);
        font:16px/1.6 -apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif; }
  .mitte{ max-width:820px; margin:0 auto; }
  h1{ font-size:1.6rem; font-weight:600; margin:0 0 4px; }
  h2{ font-size:1rem; font-weight:600; letter-spacing:.08em; text-transform:uppercase;
      color:var(--gold); margin:40px 0 12px; }
  .leise{ color:var(--asche); margin:0 0 28px; }
  .karte{ background:var(--russ); border:1px solid var(--linie); border-radius:10px; padding:20px; }
  .zahl{ font-size:2.6rem; font-weight:600; color:var(--gold-hell); line-height:1.1; }
  .balken{ display:flex; align-items:flex-end; gap:3px; height:130px; margin-top:10px; }
  .balken div{ flex:1; background:var(--gold); border-radius:2px 2px 0 0; min-height:2px; opacity:.85; }
  .balken div:hover{ opacity:1; }
  .achse{ display:flex; justify-content:space-between; color:var(--asche); font-size:.78rem; margin-top:6px; }
  table{ width:100%; border-collapse:collapse; }
  td{ padding:7px 0; border-bottom:1px solid var(--linie); }
  td:last-child{ text-align:right; color:var(--gold-hell); font-variant-numeric:tabular-nums; }
  tr:last-child td{ border-bottom:0; }
  a{ color:var(--gold); }
  form{ background:var(--russ); border:1px solid var(--linie); border-radius:10px; padding:24px; max-width:360px; }
  input{ width:100%; padding:11px 12px; margin:10px 0; border-radius:7px;
         border:1px solid var(--linie); background:var(--erhoben); color:var(--bein); font-size:1rem; }
  button{ width:100%; padding:11px; border:0; border-radius:7px; background:var(--gold);
          color:var(--schwarz); font-weight:600; font-size:1rem; cursor:pointer; }
  .monate{ margin:0 0 24px; }
  .monate a{ margin-right:14px; text-decoration:none; }
  .monate .jetzt{ color:var(--bein); font-weight:600; }
  .fehler{ color:#E08A7A; }
</style>
</head>
<body><div class="mitte">

<?php if (!$offen): ?>
  <h1>Besuche</h1>
  <p class="leise">dertdler.de</p>
  <form method="post">
    <label for="k">Kennwort</label>
    <input id="k" type="password" name="kennwort" autofocus>
    <button type="submit">Ansehen</button>
    <?php if (!empty($fehler)): ?><p class="fehler"><?= h($fehler) ?></p><?php endif; ?>
  </form>
<?php else: ?>

  <h1>Besuche</h1>
  <p class="leise">dertdler.de &middot; <a href="?ende=1">abmelden</a></p>

  <?php if (!$monate): ?>
    <div class="karte">
      <p>Noch keine Daten. Der Z&auml;hler legt die erste Datei an, sobald jemand die Seite besucht.</p>
    </div>
  <?php else: ?>

    <p class="monate">
      <?php foreach ($monate as $m => $p):
        list($j, $mo) = explode('-', $m); ?>
        <a href="?m=<?= h($m) ?>" class="<?= $m === $monat ? 'jetzt' : '' ?>"><?= $MONATSNAME[(int)$mo] ?> <?= h($j) ?></a>
      <?php endforeach; ?>
    </p>

    <div class="karte">
      <div class="zahl"><?= number_format($gesamt, 0, ',', '.') ?></div>
      <p class="leise" style="margin:0">Seitenaufrufe in diesem Monat</p>
      <?php
        list($j, $mo) = explode('-', $monat);
        $tage_im_monat = (int)date('t', mktime(0,0,0,(int)$mo,1,(int)$j));
        $hoechst = $d['tage'] ? max($d['tage']) : 1;
      ?>
      <div class="balken">
        <?php for ($i = 1; $i <= $tage_im_monat; $i++):
          $tag = sprintf('%s-%02d', $monat, $i);
          $wert = isset($d['tage'][$tag]) ? $d['tage'][$tag] : 0;
          $hoehe = $hoechst ? round($wert / $hoechst * 100) : 0; ?>
          <div style="height:<?= max($hoehe, 1) ?>%" title="<?= $i ?>. &ndash; <?= $wert ?>"></div>
        <?php endfor; ?>
      </div>
      <div class="achse"><span>1.</span><span><?= $tage_im_monat ?>.</span></div>
    </div>

    <h2>Meistbesuchte Seiten</h2>
    <div class="karte"><table>
      <?php foreach (oben($d['seiten'], 12) as $seite => $n): ?>
        <tr><td><?= h($seite) ?></td><td><?= number_format($n, 0, ',', '.') ?></td></tr>
      <?php endforeach; ?>
      <?php if (!$d['seiten']): ?><tr><td>&ndash;</td><td>0</td></tr><?php endif; ?>
    </table></div>

    <h2>Woher die Besucher kommen</h2>
    <div class="karte"><table>
      <?php foreach (oben($d['herkunft'], 12) as $wirt => $n): ?>
        <tr><td><?= h($wirt) ?></td><td><?= number_format($n, 0, ',', '.') ?></td></tr>
      <?php endforeach; ?>
      <?php if (!$d['herkunft']): ?><tr><td>&ndash;</td><td>0</td></tr><?php endif; ?>
    </table></div>

    <h2>Sprachfassungen</h2>
    <div class="karte"><table>
      <?php
        $namen = array('de' => 'Deutsch', 'en' => 'Englisch', 'fr' => 'Franz&ouml;sisch', 'pl' => 'Polnisch');
        foreach (oben($d['sprachen'], 6) as $s => $n): ?>
        <tr><td><?= isset($namen[$s]) ? $namen[$s] : h($s) ?></td><td><?= number_format($n, 0, ',', '.') ?></td></tr>
      <?php endforeach; ?>
      <?php if (!$d['sprachen']): ?><tr><td>&ndash;</td><td>0</td></tr><?php endif; ?>
    </table></div>

  <?php endif; ?>
<?php endif; ?>

</div></body>
</html>
