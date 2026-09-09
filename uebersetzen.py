#!/usr/bin/env python3
"""
Erzeugt die englische und franzoesische Fassung der Seite.

Gepflegt werden ausschliesslich die deutschen Dateien im Wurzelverzeichnis.
Dieses Skript liest sie, ersetzt die Texte anhand der Tabellen in
uebersetzung-en.json und uebersetzung-fr.json und schreibt das Ergebnis
nach en/ und fr/.

    python3 uebersetzen.py

Was nicht in der Tabelle steht, bleibt deutsch stehen - und wird am Ende
aufgelistet. So kann nichts unbemerkt untergehen.

Werktitel sind Absicht: "Mein Herz blutet" heisst auch auf der englischen
Seite so. Sie gehoeren deshalb nicht in die Tabelle.
"""

import html
import json
import os
import re
import sys
from html.parser import HTMLParser

BASIS = "https://www.dertdler.de"
ALLE = ("de", "en", "fr", "pl")      # Reihenfolge der Sprachwahl
SPRACHEN = ("en", "fr", "pl")        # was erzeugt wird
NAMEN = {"de": "DE", "en": "EN", "fr": "FR", "pl": "PL"}

# In diesen Elementen ist Text kein Text, sondern Programm bzw. Gestaltung.
STUMM = {"script", "style"}
# Attribute, deren Inhalt gelesen wird und deshalb uebersetzt gehoert.
ATTRIBUTE = {"alt", "title", "aria-label", "placeholder"}
LEER = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link",
        "meta", "param", "source", "track", "wbr"}
# Innerhalb dieser Klassen steht Werktitel - der bleibt deutsch.
BEHALTEN = {"titel", "logo", "handschrift"}

MONATE = {
    "en": ["January", "February", "March", "April", "May", "June", "July",
           "August", "September", "October", "November", "December"],
    "fr": ["janvier", "février", "mars", "avril", "mai", "juin", "juillet",
           "août", "septembre", "octobre", "novembre", "décembre"],
    # Polnisch nennt den Monat im Genitiv: "6 września 2026".
    "pl": ["stycznia", "lutego", "marca", "kwietnia", "maja", "czerwca", "lipca",
           "sierpnia", "września", "października", "listopada", "grudnia"],
}
TITEL_WORT = {"en": "tracks", "fr": "titres"}


def utwor(anzahl):
    """Polnische Mehrzahl von "utwór": 4 utwory, aber 6 und 18 utworow."""
    if anzahl % 10 in (2, 3, 4) and anzahl % 100 not in (12, 13, 14):
        return "utwory"
    return "utworów"

# Rechtstexte werden uebersetzt, aber massgeblich bleibt die deutsche Fassung.
RECHTSSEITEN = {"impressum.html", "datenschutz.html", "datenschutz-app.html"}
VORBEHALT = {
    "en": "This is a courtesy translation. In case of doubt, the German version is "
          "authoritative.",
    "fr": "Ceci est une traduction de courtoisie. En cas de doute, la version allemande "
          "fait foi.",
    "pl": "To tłumaczenie ma charakter informacyjny. W razie wątpliwości wiążąca jest "
          "wersja niemiecka.",
}
COVER = {"en": ("Cover of \u201c{}\u201d", "Album cover \u201c{}\u201d."),
         "fr": ("Pochette de \u00ab\u202f{}\u202f\u00bb", "Pochette de l\u2019album \u00ab\u202f{}\u202f\u00bb."),
         "pl": ("Ok\u0142adka \u201e{}\u201d", "Ok\u0142adka albumu \u201e{}\u201d.")}


def datum(text, sprache):
    """06.09.2026 wird zu 6 September 2026 bzw. 6 septembre 2026."""
    def ersetze(m):
        tag, monat, jahr = int(m.group(1)), int(m.group(2)), m.group(3)
        return f"{tag} {MONATE[sprache][monat - 1]} {jahr}"
    return re.sub(r"\b(\d{2})\.(\d{2})\.(\d{4})\b", ersetze, text)


def regeln(text, sprache):
    """Muster, die sich lohnen: Datumsangaben, Titelzahlen, Coverbeschreibungen."""
    kern = text.strip()
    m = re.fullmatch(r"Cover \u201e(.+)\u201c", kern)
    if m:
        return text.replace(kern, COVER[sprache][0].format(m.group(1)), 1)
    m = re.fullmatch(r"Albumcover \u201e(.+)\u201c\.", kern)
    if m:
        return text.replace(kern, COVER[sprache][1].format(m.group(1)), 1)
    if re.search(r"\d{2}\.\d{2}\.\d{4}", kern) or re.search(r"\d+ Titel", kern):
        neu = datum(kern, sprache)
        if sprache == "pl":
            neu = re.sub(r"(\d+) Titel", lambda m: f"{m.group(1)} {utwor(int(m.group(1)))}", neu)
        else:
            neu = re.sub(r"(\d+) Titel", lambda m: f"{m.group(1)} {TITEL_WORT[sprache]}", neu)
        if neu != kern:
            return text.replace(kern, neu, 1)
    return None


class Uebersetzer(HTMLParser):
    def __init__(self, tabelle, sprache, datei, fehlend):
        super().__init__(convert_charrefs=False)
        self.tabelle, self.sprache, self.datei, self.fehlend = tabelle, sprache, datei, fehlend
        self.aus = []
        self.tiefe_stumm = 0
        self.tiefe_behalten = 0
        self.stapel = []

    # --- Hilfen -------------------------------------------------------
    def uebersetze(self, text):
        kern = text.strip()
        if not kern or not re.search(r"[A-Za-zÄÖÜäöüß]", kern):
            return text
        if "@@" in kern or self.tiefe_behalten:
            return text
        geregelt = regeln(text, self.sprache)
        if geregelt is not None:
            return geregelt
        # Seitenbezogene Ausnahme zuerst: dasselbe deutsche Wort kann in der
        # Navigation und mitten im Satz verschieden uebersetzt gehoeren.
        for schluessel in (f"{self.datei}:{kern}", kern):
            if schluessel in self.tabelle:
                return self.einsetzen(text, kern, self.tabelle[schluessel])
        self.fehlend.setdefault(kern, set()).add(self.datei)
        return text

    @staticmethod
    def einsetzen(text, kern, ersatz):
        """
        Setzt die Uebersetzung ein und behaelt die Leerzeichen ringsum.

        Ausnahme: Beginnt die Uebersetzung mit einem Satzzeichen, faellt das
        Leerzeichen davor weg. Sonst entstuende "Erwacht , a pozniej" - die
        deutsche Vorlage hatte an der Stelle keins, weil dort ein Wort stand.
        """
        vorn = text[:len(text) - len(text.lstrip())]
        hinten = text[len(text.rstrip()):]
        if ersatz[:1] in ",.;:!?)»":
            vorn = ""
        return vorn + ersatz + hinten

    def pfad(self, wert):
        """Bilder und Stylesheets liegen eine Ebene hoeher als en/ und fr/."""
        if not wert or re.match(r"^(https?:|mailto:|tel:|#|//|\.\./)", wert):
            return wert
        if wert.endswith(".html") or wert.startswith("?"):
            return wert            # Seiten liegen im selben Ordner
        return "../" + wert

    def attribute(self, tag, attrs):
        neu = []
        for name, wert in attrs:
            if wert is None:
                neu.append((name, wert)); continue
            if name in ("href", "src") and tag != "a":
                wert = self.pfad(wert)
            elif name in ("href", "src"):
                wert = self.pfad(wert)
            elif name in ATTRIBUTE:
                geregelt = regeln(wert, self.sprache)
                wert = geregelt if geregelt is not None else self.uebersetze(wert)
            elif tag == "meta" and name == "content" and \
                    any(n == "name" and v in ("description", "keywords") for n, v in attrs):
                wert = self.uebersetze(wert)
            elif tag == "html" and name == "lang":
                wert = self.sprache
            neu.append((name, wert))
        return neu

    def schreibe_tag(self, tag, attrs, schluss=""):
        teile = [tag]
        for name, wert in attrs:
            teile.append(name if wert is None else f'{name}="{html.escape(wert, quote=True)}"')
        self.aus.append(f"<{' '.join(teile)}{schluss}>")

    # --- Ereignisse ---------------------------------------------------
    def handle_starttag(self, tag, attrs):
        if tag in STUMM:
            self.tiefe_stumm += 1
        klassen = {k for n, v in attrs if n == "class" and v for k in v.split()}
        if klassen & BEHALTEN:
            self.tiefe_behalten += 1
        self.stapel.append(bool(klassen & BEHALTEN))
        self.schreibe_tag(tag, self.attribute(tag, attrs))

    def handle_startendtag(self, tag, attrs):
        self.schreibe_tag(tag, self.attribute(tag, attrs), schluss=" /")

    def handle_endtag(self, tag):
        if tag in STUMM and self.tiefe_stumm:
            self.tiefe_stumm -= 1
        if self.stapel and self.stapel.pop() and self.tiefe_behalten:
            self.tiefe_behalten -= 1
        if tag not in LEER:
            self.aus.append(f"</{tag}>")

    def handle_data(self, daten):
        self.aus.append(daten if self.tiefe_stumm else self.uebersetze(daten))

    def handle_comment(self, daten):
        self.aus.append(f"<!--{daten}-->")

    def handle_decl(self, daten):
        self.aus.append(f"<!{daten}>")

    def handle_entityref(self, name):
        self.aus.append(f"&{name};")

    def handle_charref(self, name):
        self.aus.append(f"&#{name};")

    def ergebnis(self):
        return "".join(self.aus)


def sprachwahl(datei, sprache):
    """Die Sprachwahl wird je Fassung neu gesetzt - Pfade und Markierung."""
    zeilen = ['  <div class="sprachen">']
    for code in ALLE:
        if code == sprache:
            ziel = datei
        elif code == "de":
            ziel = f"../{datei}"
        else:
            ziel = f"../{code}/{datei}"
        aktuell = ' aria-current="page"' if code == sprache else ""
        marke = "" if code == sprache else f' hreflang="{code}"'
        zeilen.append(f'    <a{aktuell} href="{ziel}" lang="{code}"{marke}>{NAMEN[code]}</a>')
    zeilen.append("  </div>")
    return "\n".join(zeilen) + "\n"


def hreflang(datei, sprache):
    zeilen = []
    for code in ALLE:
        ziel = datei if code == "de" else f"{code}/{datei}"
        zeilen.append(f'<link rel="alternate" hreflang="{code}" href="{BASIS}/{ziel}">')
    zeilen.append(f'<link rel="alternate" hreflang="x-default" href="{BASIS}/{datei}">')
    return "\n".join(zeilen)


def main():
    hier = os.path.dirname(os.path.abspath(__file__))
    os.chdir(hier)
    seiten = sorted(f for f in os.listdir(".") if f.endswith(".html"))
    if not seiten:
        sys.exit("Keine deutschen Seiten gefunden.")

    gesamt_fehlend = {}
    for sprache in SPRACHEN:
        pfad_tabelle = f"uebersetzung-{sprache}.json"
        if not os.path.exists(pfad_tabelle):
            print(f"[{sprache}] {pfad_tabelle} fehlt - uebersprungen.")
            continue
        tabelle = json.load(open(pfad_tabelle, encoding="utf-8"))
        os.makedirs(sprache, exist_ok=True)
        fehlend = {}

        for datei in seiten:
            quelle = open(datei, encoding="utf-8").read()

            # Sprachwahl und hreflang werden nicht uebersetzt, sondern ersetzt.
            quelle = re.sub(r'  <div class="sprachen">.*?  </div>\n',
                            "@@SPRACHWAHL@@\n", quelle, flags=re.S)
            quelle = re.sub(r'<link rel="alternate" hreflang="[^"]*" href="[^"]*">\n?',
                            "", quelle)
            quelle = quelle.replace("</head>", "@@HREFLANG@@\n</head>", 1)

            p = Uebersetzer(tabelle, sprache, datei, fehlend)
            p.feed(quelle)
            ergebnis = p.ergebnis()
            ergebnis = ergebnis.replace("@@SPRACHWAHL@@", sprachwahl(datei, sprache))
            ergebnis = ergebnis.replace("@@HREFLANG@@", hreflang(datei, sprache))
            if datei in RECHTSSEITEN:
                ergebnis = re.sub(
                    r'(<h1 class="seitentitel">.*?</h1>)',
                    r'\1\n    <p class="vorbehalt">' + VORBEHALT[sprache] + "</p>",
                    ergebnis, count=1, flags=re.S)
            open(os.path.join(sprache, datei), "w", encoding="utf-8").write(ergebnis)

        print(f"[{sprache}] {len(seiten)} Seiten geschrieben nach {sprache}/")
        if fehlend:
            gesamt_fehlend[sprache] = fehlend
            print(f"[{sprache}] {len(fehlend)} Texte ohne Uebersetzung:")
            for kern in sorted(fehlend)[:40]:
                orte = ", ".join(sorted(fehlend[kern]))
                kurz = kern if len(kern) <= 70 else kern[:67] + "..."
                print(f'    "{kurz}"   ({orte})')
            if len(fehlend) > 40:
                print(f"    ... und {len(fehlend) - 40} weitere")

    if gesamt_fehlend:
        print("\nDiese Texte stehen noch deutsch in der fremdsprachigen Fassung.")
        print("Ergaenze sie in der jeweiligen uebersetzung-<sprache>.json.")
    else:
        print("\nAlles uebersetzt.")


if __name__ == "__main__":
    main()
