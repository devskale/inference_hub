# KI-Agent Prompt: Kriterien-IDs und Beispiele (v3.2)

## BESCHREIBUNG

Dieser Prompt extrahiert alle Kriterien (Formal-, Eignungs- und Zuschlagskriterien) aus Ausschreibungsunterlagen und strukturiert sie mit eindeutigen IDs. Die Kriterien werden in einem JSON-Format ausgegeben, das für die Integration in bestehende Datenstrukturen optimiert ist.

## KRITERIEN SCHEMA

```json
{
  "schema_version": "3.2-ai-optimized",
  "kriterien": [
    {
      "id": "string",
      "typ": "Formal|Eignung|Zuschlag",
      "kategorie": "string",
      "name": "string",
      "anforderung": "string|null",
      "schwellenwert": "string|null",
      "gewichtung_punkte": "number|null",
      "dokumente": ["string"],
      "geltung_lose": ["string"],
      "pruefung": {
        "status": "null",
        "bemerkung": "null",
        "pruefer": "null",
        "datum": "null"
      },
      "quelle": "string|null"
    }
  ]
}
```

## AUFGABE

Extrahiere alle Kriterien aus dem Dokument und strukturiere sie gemäß dem Schema mit folgenden Feldern:

- **id**: Eindeutige ID nach der definierten Systematik
- **typ**: Kriterientyp (Formal/Eignung/Zuschlag)
- **kategorie**: Fachliche Kategorisierung
- **name**: Kurze, prägnante Bezeichnung
- **anforderung**: Detaillierte Beschreibung der Anforderung
- **schwellenwert**: Konkrete Grenzwerte (falls vorhanden)
- **gewichtung_punkte**: Punktzahl für Zuschlagskriterien
- **dokumente**: Liste erforderlicher Dokumente
- **geltung_lose**: Geltungsbereich (Lose)
- **pruefung**: Prüfungsstatus (initial null)
- **quelle**: Referenz im Dokument

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

## ID-SYSTEMATIK

### Präfixe nach Kriterientyp:

- **F_xxx**: Formalkriterien (führen zu Ausschluss bei Nichterfüllung)
- **E_xxx**: Eignungskriterien (führen zu Ausschluss bei Nichterfüllung)
- **Z_xxx**: Zuschlagskriterien (führen zu Punktabzug bei Nichterfüllung)

### Kategorien-Kürzel:

- **BIEGE**: Bietergemeinschaft
- **TECH**: Technische Leistungsfähigkeit
- **WIRT**: Wirtschaftliche Leistungsfähigkeit
- **BERUFL**: Berufliche Zuverlässigkeit
- **PREIS**: Preis
- **QUAL**: Qualität
- **TERM**: Termine
- **DOK**: Dokumentation
- **FORM**: Formale Anforderungen
- **NACH**: Nachweise
- **FRIST**: Fristen

### Nummerierung:

- Fortlaufend innerhalb jeder Kategorie: 001, 002, 003, ...
- Bei über 999 Kriterien: 1001, 1002, ...

### Beispiel-IDs:

- F_DOK_001: Erstes Dokumentenkriterium (Formal)
- E_TECH_005: Fünftes technisches Eignungskriterium
- Z_PREIS_001: Erstes Preiskriterium (Zuschlag)
- F_FRIST_002: Zweites Fristenkriterium (Formal)

## VOLLSTÄNDIGES BEISPIEL

```json
{
  "schema_version": "3.2-ai-optimized",
  "kriterien": [
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
    },
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
  ]
}
```

## AUSGABE

- Nur JSON Kriterien-Objekt mit "kriterien" Array (keine anderen Inhalte)
- Keine Markdown-Wrapper
- Alle im Dokument identifizierten Kriterien vollständig erfassen
- IDs nach der definierten Systematik vergeben
- Prüfungsfelder initial auf null setzen
