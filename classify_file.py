from huggingface_hub import InferenceClient
from getparams import load_api_credentials
import argparse
import json

# Testvariablen
TEST_TEXT = """Hallo, ich habe kürzlich ein Gerät von Ihrem Unternehmen gekauft, aber es funktioniert nicht wie angepriesen und ich möchte eine Rückerstattung!
Sie sind ein Stück Scheiße."""

# Vorgegebene Labels
LABELS = [
    "Vertrag", 
    "Rechtsauskunft",
    "Versicherungsauskunft"
    ]

def klassifiziere_text(text, api_token):
    client = InferenceClient(token=api_token)
    
    inputs = text
    params = {"candidate_labels": LABELS}
    
    response = client.post(
        json={"inputs": inputs, "parameters": params},
        model="typeform/distilbert-base-uncased-mnli"
    )
    
    # Bytes-Antwort in JSON umwandeln
    return json.loads(response.decode('utf-8'))

def lese_datei(dateipfad, max_zeichen):
    with open(dateipfad, 'r', encoding='utf-8') as datei:
        return datei.read(max_zeichen)

def main():
    parser = argparse.ArgumentParser(description="Klassifiziere Text mithilfe von Zero-Shot-Klassifikation.")
    parser.add_argument("text", nargs="?", help="Der zu klassifizierende Text")
    parser.add_argument("-t", "--test", action="store_true", help="Im Testmodus mit vordefinierten Eingaben ausführen")
    parser.add_argument("-f", "--file", help="Pfad zur Textdatei, die analysiert werden soll")
    parser.add_argument("-m", "--max", type=int, default=1000, help="Maximale Anzahl der zu lesenden Zeichen aus der Datei")
    args = parser.parse_args()

    if args.test:
        text = TEST_TEXT
        print("Wird im Testmodus mit vordefinierten Eingaben ausgeführt.")
    elif args.file:
        text = lese_datei(args.file, args.max)
    else:
        if not args.text:
            parser.error("Text zur Klassifizierung ist erforderlich, es sei denn, der Testmodus ist aktiviert oder eine Datei wird angegeben.")
        text = args.text

    api_token = load_api_credentials('huggingface')
    
    try:
        ergebnis = klassifiziere_text(text, api_token)
        
        print("\nEingegebener Text:")
        print(text)
        print("\nKlassifizierungsergebnisse:")
        for label, score in zip(ergebnis['labels'], ergebnis['scores']):
            print(f"{label}: {score:.4f}")
    except Exception as e:
        print(f"Ein Fehler ist aufgetreten: {e}")

if __name__ == "__main__":
    main()