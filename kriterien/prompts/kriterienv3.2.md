# KI-Agent Prompt: Kriterien-Extraktion (Optimiert v3.2)

## Aufgabe

Extrahiere ALLE prüfbaren Kriterien aus der Ausschreibung für automatisierte Compliance-Prüfung.

## 3-Schritt-Methode

### SCHRITT 1: SCANNEN nach Trigger-Wörtern

- **K/O-Kriterien**: "muss", "hat zu", "verpflichtet", "unzulässig", "ausgeschlossen"
- **Bewertung**: "Punkte", "Gewichtung", "bewertet", "Zuschlagskriterium"
- **Dokumente**: "Beilage", "Nachweis", "vorzulegen", "beizufügen"
- **Quantifizierbar**: Zahlen, "mindestens", "bis spätestens", "EUR", "%"

### SCHRITT 2: KATEGORISIEREN nach Auswirkung

- **Formal** = Fehler führt zu Ausschluss (Dokumente, Fristen, Unterschriften)
- **Eignung** = Fehler führt zu Ausschluss (Befugnis, Zuverlässigkeit, Kapazität)
- **Zuschlag** = Fehler reduziert Punktzahl (Preis, Qualität, Termine)

### SCHRITT 3: STRUKTURIEREN für KI-Prüfung

## VEREINFACHTES SCHEMA

```json
{
  "schema_version": "3.2-ai-optimized",
  "meta": {
    "auftraggeber": "string",
    "aktenzeichen": "string|null",
    "lose": ["string"]
  },
  "kriterien": [
    {
      "id": "string",
      "typ": "Formal|Eignung|Zuschlag",
      "kategorie": "string",
      "name": "string",
      "anforderung": "string",
      "schwellenwert": "string|null",
      "gewichtung_punkte": "number|null",
      "dokumente": ["string"],
      "geltung_lose": ["string"],
      "pruefung": {
        "status": "erfuellt|nicht_erfuellt|teilweise_erfuellt|ungeprueft|null",
        "bemerkung": "string|null",
        "pruefer": "string|null",
        "datum": "YYYY-MM-DD|null"
      },
      "quelle": "string"
    }
  ]
}
```

## BEISPIELE für KI-Training

### Beispiel 1: Formalkriterium

```
TEXT: "Bietergemeinschaften haben in Beilage 01 die Mitglieder aufzulisten."

EXTRAKTION:
{
  "id": "F_BIEGE_001",
  "typ": "Formal",
  "kategorie": "Bietergemeinschaft",
  "name": "Mitglieder-Auflistung",
  "anforderung": "Bietergemeinschaften müssen Mitglieder in Beilage 01 auflisten",
  "schwellenwert": null,
  "gewichtung_punkte": null,
  "dokumente": ["Beilage 01"],
  "geltung_lose": ["alle"],
  "pruefung": {
    "status": null,
    "bemerkung": null,
    "pruefer": null,
    "datum": null
  },
  "quelle": "Punkt 4.1.(2)"
}
```

### Beispiel 2: Eignungskriterium

```
TEXT: "Der Bieter muss mindestens 10 Vollzeitäquivalente beschäftigen."

EXTRAKTION:
{
  "id": "E_TECH_001",
  "typ": "Eignung",
  "kategorie": "Technische Leistungsfähigkeit",
  "name": "Mindest-Mitarbeiterzahl",
  "anforderung": "Mindestens 10 Vollzeitäquivalente in 2021-2023",
  "schwellenwert": "10 Vollzeitäquivalente",
  "gewichtung_punkte": null,
  "dokumente": [],
  "geltung_lose": ["alle"],
  "pruefung": {
    "status": null,
    "bemerkung": null,
    "pruefer": null,
    "datum": null
  },
  "quelle": "Punkt 5.4.1"
}
```

### Beispiel 3: Zuschlagskriterium

```
TEXT: "Zuschlagskriterium Preis: 700 Punkte. Günstigstes Angebot erhält Maximalpunktzahl."

EXTRAKTION:
{
  "id": "Z_PREIS_001",
  "typ": "Zuschlag",
  "kategorie": "Preis",
  "name": "Gesamtpreis",
  "anforderung": null,
  "schwellenwert": null,
  "gewichtung_punkte": 700,
  "dokumente": [],
  "geltung_lose": ["alle"],
  "pruefung": {
    "status": null,
    "bemerkung": null,
    "pruefer": null,
    "datum": null
  },
  "quelle": "Punkt 7.2"
}
```

## PRÜFREGELN für KI-Agent

### ✅ VOLLSTÄNDIGKEIT:

- Alle "muss", "verpflichtet", "unzulässig" erfasst?
- Alle Beilagen/Nachweise identifiziert?
- Alle Punktevergaben bei Zuschlag erfasst?

### ✅ PRÄZISION:

- Schwellenwerte quantifiziert (Zahlen, Daten)?
- Geltungsbereich spezifiziert (welche Lose)?
- Prüfungsfelder initial leer gelassen?

## AUSGABE

- Nur JSON (keine Markdown-Wrapper)
- Keine Kommentare oder Erklärungen
- Bei Unsicherheit: `null` verwenden
- Systematische IDs: F_xxx, E_xxx, Z_xxx

## FOKUS für KI-Prüfung

Jedes extrahierte Kriterium bildet die Basis für spätere Prüfung durch KI-Agenten oder Anwälte. Daher:

- Klare, messbare Anforderungen formulieren
- Dokumentenbezüge eindeutig benennen
- Schwellenwerte präzise erfassen
- Prüfungsfelder initial leer lassen für spätere Ausfüllung
