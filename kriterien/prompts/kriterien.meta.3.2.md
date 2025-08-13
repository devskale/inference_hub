# KI-Agent Prompt: Meta-Tag Generation (v3.2)

## BESCHREIBUNG

Dieser Prompt extrahiert die grundlegenden Metadaten einer Ausschreibung, einschließlich Auftraggeber, Aktenzeichen und Lose mit deren Bewertungsprinzipien. Die Informationen bilden die Basis für die strukturierte Erfassung von Ausschreibungsdaten.

## META-TAG SCHEMA

```json
{
  "schema_version": "3.2-ai-optimized",
  "meta": {
    "auftraggeber": "string",
    "aktenzeichen": "string|null",
    "lose": [
      {
        "nummer": "string",
        "bezeichnung": "string",
        "beschreibung": "string",
        "bewertungsprinzip": "Bestbieter|Billigstbieter|Sonstige"
      }
    ]
  }
}
```

## AUFGABE

Generiere ausschließlich das Meta-Tag aus der Ausschreibung mit folgenden Feldern:

- **auftraggeber**: Name der ausschreibenden Organisation/Behörde
- **aktenzeichen**: Offizielle Referenznummer der Ausschreibung (falls vorhanden)
- **lose**: Array aller Lose/Teilaufträge mit detaillierten Informationen

### Lose-Struktur:
- **nummer**: Los-Nummer (z.B. "Los 1", "1", "A")
- **bezeichnung**: Kurze Bezeichnung des Loses
- **beschreibung**: Detaillierte Beschreibung der Leistung/Produkte
- **bewertungsprinzip**: 
  - "Bestbieter" = Wirtschaftlich und technisch günstigstes Angebot
  - "Billigstbieter" = Niedrigster Preis
  - "Sonstige" = Andere Bewertungsmethoden

## BEISPIEL

Für eine Ausschreibung mit 4 Losen:
```json
{
  "schema_version": "3.2-ai-optimized",
  "meta": {
    "auftraggeber": "Wiener Wohnen Hausbetreuung GmbH",
    "aktenzeichen": "2023_02002_AAB_EV",
    "lose": [
      {
        "nummer": "Los 1",
        "bezeichnung": "Aufsitzrasenmäher",
        "beschreibung": "Lieferung von Aufsitzrasenmähern",
        "bewertungsprinzip": "Bestbieter"
      },
      {
        "nummer": "Los 2",
        "bezeichnung": "Laubbläser und Rasenmäher",
        "beschreibung": "Lieferung von Laubbläsern und Rasenmähern",
        "bewertungsprinzip": "Billigstbieter"
      }
    ]
  }
}
```

## AUSGABE

- Nur JSON Meta-Tag (keine anderen Inhalte)
- Keine Markdown-Wrapper
- Bei fehlendem Aktenzeichen: `null` verwenden
- Alle Lose mit vollständigen Informationen erfassen