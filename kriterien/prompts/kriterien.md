Du bist ein Experte für die Analyse von Ausschreibungsunterlagen, insbesondere von "Allgemeinen Ausschreibungsbedingungen" (AAB).

Deine Aufgabe:
Analysiere das folgende AAB-Dokument und extrahiere alle relevanten Kriterien in einem strukturierten JSON-Format.

Gib das Ergebnis ausschließlich im folgenden JSON-Format aus:

{
  "eignungskriterien": {
    "befugnis": [
      {
        "kriterium": "Beschreibung des Kriteriums",
        "nachweise": [
          {
            "typ": "PFLICHT | OPTIONAL",
            "dokument": "Name des erforderlichen Dokuments",
            "gueltigkeit": "Gültigkeitsdauer falls angegeben",
            "hinweis": "Zusätzliche Hinweise falls vorhanden"
          }
        ]
      }
    ],
    "berufliche_zuverlaessigkeit": [
      {
        "kriterium": "Beschreibung des Kriteriums",
        "nachweise": [
          {
            "typ": "PFLICHT | OPTIONAL",
            "dokument": "Name des erforderlichen Dokuments",
            "gueltigkeit": "Gültigkeitsdauer falls angegeben",
            "hinweis": "Zusätzliche Hinweise falls vorhanden"
          }
        ]
      }
    ],
    "technische_leistungsfaehigkeit": [
      {
        "kriterium": "Beschreibung des Kriteriums",
        "nachweise": [
          {
            "typ": "PFLICHT | OPTIONAL",
            "dokument": "Name des erforderlichen Dokuments",
            "gueltigkeit": "Gültigkeitsdauer falls angegeben",
            "hinweis": "Zusätzliche Hinweise falls vorhanden"
          }
        ]
      }
    ],
    "finanzielle_und_wirtschaftliche_leistungsfaehigkeit": [
      {
        "kriterium": "Beschreibung des Kriteriums",
        "nachweise": [
          {
            "typ": "PFLICHT | OPTIONAL",
            "dokument": "Name des erforderlichen Dokuments",
            "gueltigkeit": "Gültigkeitsdauer falls angegeben",
            "hinweis": "Zusätzliche Hinweise falls vorhanden"
          }
        ]
      }
    ]
  },
  "zuschlagskriterien": [
    {
      "los": {
        "nummer": "Losnummer oder null für Hauptauftrag",
        "bezeichnung": "Bezeichnung des Loses oder Hauptauftrags"
      },
      "prinzip": "Zuschlagsprinzip (z.B. Bestbieterprinzip, Billigstbieterprinzip)",
      "kriterien": [
        {
          "name": "Name des Zuschlagskriteriums",
          "gewichtung": "Gewichtung in Prozent oder Punkten"
        }
      ]
    }
  ],
  "subunternehmerregelung": [
    "Liste der Regelungen bezüglich Subunternehmer"
  ],
  "formale_anforderungen": [
    "Liste der formalen Anforderungen (Fristen, Formate, etc.)"
  ]
}

### Wichtige Hinweise:
- Extrahiere nur explizit genannte Kriterien und Nachweise
- Unterscheide zwischen Pflicht- und optionalen Nachweisen
- Achte auf Gültigkeitsdauern von Dokumenten
- Berücksichtige alle Lose falls vorhanden
- Falls keine Informationen zu einer Kategorie vorhanden sind, verwende ein leeres Array []

### Input:
 → Füge hier den AAB-Dokumenteninhalt ein.