#!/bin/bash
#
# Laedt die Seite zu 1blu hoch.
#
# Die Zugangsdaten stehen NICHT in dieser Datei, sondern in ~/.netrc.
# Dort gehoert eine Zeile hin:
#
#     machine webhosting30.1blu.de login ftp256965-2717528 password DEIN_PASSWORT
#
# und die Datei darf nur dir gehoeren:  chmod 600 ~/.netrc
#
# Aufruf:  ./hochladen.sh            alles hochladen
#          ./hochladen.sh --test     nur zeigen, was hochgeladen wuerde

set -uo pipefail
cd "$(dirname "$0")"

SERVER="webhosting30.1blu.de"
TESTLAUF=0
[ "${1:-}" = "--test" ] && TESTLAUF=1

if [ ! -f "$HOME/.netrc" ]; then
  echo "Es gibt keine ~/.netrc - ohne die kenne ich den Zugang nicht."
  echo "Siehe den Kommentar oben in dieser Datei."
  exit 1
fi

# Uebersetzungen frisch erzeugen, damit en/ fr/ pl/ zum deutschen Stand passen.
echo "Uebersetzungen erzeugen ..."
python3 uebersetzen.py || { echo "uebersetzen.py ist gescheitert - Abbruch."; exit 1; }
echo

fehler=0
anzahl=0

hochladen() {
  local lokal="$1"
  local ziel="${lokal#./}"
  anzahl=$((anzahl + 1))
  if [ "$TESTLAUF" = "1" ]; then
    echo "  wuerde laden: $ziel"
    return
  fi
  if curl -sS --ssl-reqd --netrc --ftp-create-dirs -T "$lokal" "ftp://$SERVER/$ziel"; then
    echo "  ok  $ziel"
  else
    echo "  FEHLER  $ziel"
    fehler=$((fehler + 1))
  fi
}

echo "Seiten und Gestaltung ..."
for f in *.html *.css .htaccess; do
  [ -f "$f" ] && hochladen "$f"
done

echo
echo "Bilder und Sprachfassungen ..."
for ordner in bilder en fr pl; do
  [ -d "$ordner" ] || continue
  while IFS= read -r datei; do
    hochladen "$datei"
  done < <(find "$ordner" -type f ! -name ".DS_Store" ! -name "._*" | sed 's|^|./|')
done

echo
if [ "$TESTLAUF" = "1" ]; then
  echo "Testlauf: $anzahl Dateien waeren hochgeladen worden. Nichts veraendert."
elif [ "$fehler" -eq 0 ]; then
  echo "Fertig. $anzahl Dateien hochgeladen, keine Fehler."
  echo "Sieh auf https://dertdler.de nach - bei Bildern hilft ein Neuladen mit Umschalt."
else
  echo "Fertig mit $fehler Fehlern bei $anzahl Dateien."
  echo "Meldet curl 0 Bytes oder findet er den Pfad nicht, steht in der LIESMICH,"
  echo "was es damit auf sich hat - der Upload-Pfad hat sich schon einmal geaendert."
fi
