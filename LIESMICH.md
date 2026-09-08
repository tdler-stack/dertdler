# dertdler.de

Homepage für Thorsten Diehl / TDler. Gestaltung nach der Visitenkarte:
warmes Schwarz, Bronze-Gold, gesperrte Versalien, Schreibschrift für die
Motto-Zeilen.

## Dateien

    index.html        Startseite
    impressum.html
    datenschutz.html
    stil.css          Gestaltung
    schrift.css       Oswald, Barlow und Caveat als eingebettete Schriften
    bilder/           Cover und App-Symbol

Alle sechs Dateien plus den Ordner `bilder/` zu 1blu hochladen, in das
Wurzelverzeichnis der Domain.

## Warum die Schriften eingebettet sind

Sie liegen bewusst nicht bei Google. Beim Nachladen von Google Fonts geht die
IP-Adresse jedes Besuchers an Google — das Landgericht München hat 2022 einen
Websitebetreiber deswegen verurteilt. So bleibt die Aussage in der
Datenschutzerklärung wahr, dass nichts von fremden Servern nachgeladen wird.
Wer Schriften ändert, muss das mitbedenken.

## Offen (Stand 06.09.2026)

- Streaming-Adressen: Spotify, Apple Music, YouTube, Instagram.
  Im Markup stehen `<span class="dienst" data-offen>`; daraus wird ein
  `<a href="...">` und das `data-offen` entfällt.
- Verkaufsadressen: Amazon, eBay, Kleinanzeigen. Verkäuferprofil verlinken,
  nicht einzelne Angebote — die laufen aus.
- Vier Bildplätze im Abschnitt "Bilder".
- Biografie: der Text unter "Zur Person" ist ein Entwurf und als solcher
  markiert.
- Foto von Thorsten an den Tasten. Existiert noch nicht; muss aufgenommen
  werden. Die vorhandenen Studiofotos sind zu unaufgeräumt, und Zuschneiden
  hilft nicht, weil das Chaos in der Bildmitte liegt.

## SSL

`https://dertdler.de` liefert derzeit ein Zertifikat für `*.1blu.de` und
damit eine Browserwarnung. Im 1blu-Kundenbereich das kostenlose Zertifikat
für die Domain aktivieren.

## Bearbeitete Fotos

Die abgestimmten Porträts liegen im Sitzungsordner, nicht hier. Beim
Bearbeiten von iPhone-Fotos immer `ImageOps.exif_transpose` benutzen, sonst
liegen Hochformate quer.

## Wo die Seite auf dem Webspace liegt

Das ist nicht offensichtlich und hat einmal eine Stunde gekostet.

**Das Wurzelverzeichnis der Domain ist `/www/dertdler.de/wordpress/`** — nicht
`/www/dertdler.de/`. Der Name stammt von der frueheren WordPress-Installation;
1blu hat die Domain damals auf diesen Unterordner gelegt. Dateien eine Ebene
hoeher werden nicht ausgeliefert, auch wenn sie sichtbar dort liegen.

Alle sieben Dateien plus `bilder/` gehoeren also in:

    /www/dertdler.de/wordpress/

Die frueheren Inhalte liegen unter `/alt/wordpress` — ausserhalb von `/www`
und damit aus dem Netz nicht erreichbar.

## Zugang

    WebFTP:  ueber den Link im 1blu-Kundenbereich (Monsta FTP, laeuft im Browser)
    Server:  webhosting30.1blu.de
    Zugang:  ftp256965-2717528   (Pfad /, sieht alles)

Monsta FTP blendet Dateien mit einem Punkt am Anfang standardmaessig aus. Die
`.htaccess` laesst sich deshalb schlecht hochladen; einfacher ist es, sie dort
als neue Datei anzulegen und den Inhalt einzufuegen.

Im Finder werden versteckte Dateien mit Befehl + Umschalt + Punkt eingeblendet.

## Offene Punkte

- Das Wurzelverzeichnis liesse sich im Kundenbereich unter Domain vermutlich
  auf `/www/dertdler.de/` umstellen. Dann koennte der irrefuehrende Ordnername
  `wordpress` verschwinden.
- `/alt` kann geloescht werden, sobald sicher ist, dass nichts fehlt.
