# KI-Agent Prompt: Bieterdokumente-Extraktion (v3.2)

## BESCHREIBUNG

Dieser Prompt extrahiert die erforderlichen Bieterdokumente aus Ausschreibungsunterlagen. Die Informationen werden typischerweise im Kapitel "INHALT UND FORM DES ANGEBOTES" oder ähnlichen Abschnitten aufgelistet und bilden die Grundlage für die Vollständigkeitsprüfung von Bieterangeboten.

## BIETERDOKUMENTE SCHEMA

```json
{
  "schema_version": "3.2-ai-optimized",
  "bieterdokumente": [
    {
      "kategorie": "Pflichtdokument|Bedarfsfall|Nachweis|Zusatzdokument",
      "bezeichnung": "string",
      "beilage_nummer": "string|null",
      "beschreibung": "string",
      "unterzeichnung_erforderlich": "boolean",
      "fachliche_pruefung": "boolean"
    }
  ]
}
```

## AUFGABE

Extrahiere alle erforderlichen Bieterdokumente aus dem Abschnitt "INHALT UND FORM DES ANGEBOTES" oder ähnlichen Kapiteln mit folgenden Feldern:

### Dokumentenstruktur:
- **kategorie**: 
  - "Pflichtdokument" = Immer erforderlich
  - "Bedarfsfall" = Nur bei bestimmten Umständen erforderlich
  - "Nachweis" = Eignungsnachweis oder Qualifikationsbeleg
  - "Zusatzdokument" = Ergänzende Unterlagen

- **bezeichnung**: Vollständige Bezeichnung des Dokuments
- **beilage_nummer**: Referenznummer (z.B. "Beilage 01", "Beilage 04")
- **beschreibung**: Detaillierte Beschreibung des Dokuments und seiner Funktion
- **unterzeichnung_erforderlich**: Ob das Dokument signiert werden muss
- **fachliche_pruefung**: Ob fachliche Prüfung durch Steuerberater/Wirtschaftsprüfer erforderlich

## TYPISCHE BIETERDOKUMENTE

### Standarddokumente:
- Angebotshauptteil der Vergabeplattform
- Leistungsverzeichnis und Preisblatt
- Firmenbuchauszug
- Erklärung SanktionenVO

### Bedarfsfälle:
- Erklärung für Bieter- und Arbeitsgemeinschaften
- Subunternehmerliste
- Verpflichtungserklärung Subunternehmer

### Eignungsnachweise:
- Leistungsfähigkeit Dienstnehmer und Umsätze
- Leistungsfähigkeit Referenzen
- Nachweise der Eignung gemäß Punkt 5

### Zuschlagskriterien:
- ISO-Zertifizierungen
- Lieferfrist-Verkürzung

### Produktbezogene Dokumente:
- Datenblätter zu angebotenen Produkten
- Sicherheitsdatenblätter
- Zertifikate

## BEISPIEL

```json
{
  "schema_version": "3.2-ai-optimized",
  "bieterdokumente": [
    {
      "kategorie": "Pflichtdokument",
      "bezeichnung": "Angebotshauptteil der Vergabeplattform",
      "beilage_nummer": null,
      "beschreibung": "Ausgefüllter und signierter Hauptteil des Angebots über die elektronische Vergabeplattform",
      "unterzeichnung_erforderlich": true,
      "fachliche_pruefung": false
    },
    {
      "kategorie": "Bedarfsfall",
      "bezeichnung": "Erklärung für Bieter- und Arbeitsgemeinschaften",
      "beilage_nummer": "Beilage 01",
      "beschreibung": "Erforderlich bei Bieter- oder Arbeitsgemeinschaften zur Darstellung der Zusammenarbeit",
      "unterzeichnung_erforderlich": true,
      "fachliche_pruefung": false
    },
    {
      "kategorie": "Pflichtdokument",
      "bezeichnung": "Leistungsverzeichnis und Preisblatt",
      "beilage_nummer": "Beilage 04",
      "beschreibung": "Ausgefülltes Formblatt mit Preisangaben für alle ausgeschriebenen Leistungen",
      "unterzeichnung_erforderlich": false,
      "fachliche_pruefung": false
    },
    {
      "kategorie": "Nachweis",
      "bezeichnung": "Leistungsfähigkeit Dienstnehmer und Umsätze",
      "beilage_nummer": "Beilage 05",
      "beschreibung": "Von Steuerberater oder Wirtschaftsprüfer bestätigtes Formblatt zur finanziellen Leistungsfähigkeit",
      "unterzeichnung_erforderlich": true,
      "fachliche_pruefung": true
    }
  ]
}
```

## AUSGABE

- Nur JSON Bieterdokumente-Tag (keine anderen Inhalte)
- Keine Markdown-Wrapper
- Alle im Dokument genannten Bieterdokumente vollständig erfassen
- Bei fehlender Beilage-Nummer: `null` verwenden
- Kategorisierung nach tatsächlicher Verwendung im Dokument