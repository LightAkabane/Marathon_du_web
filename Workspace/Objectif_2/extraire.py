import json
import requests

# Définir à partir de quelle occurrence démarrer (1 pour démarrer au début)
start_occurrence = 1

# Charger le fichier texte contenant les IDs
with open('ids.txt', 'r', encoding='utf-8') as f:
    # Lire chaque ligne et ne conserver que les lignes non vides constituées uniquement de chiffres
    ids_unique = [line.strip() for line in f if line.strip().isdigit()]

# Dictionnaire pour stocker pour chaque id le corpus (intro + outro)
resultats = {}

total_ids = len(ids_unique)
processed_count = 0

# Pour chaque id, appeler l'API en testant deux endpoints
for index, id_val in enumerate(ids_unique, start=1):
    # Si l'indice est inférieur à l'occurrence de départ, on passe
    if index < start_occurrence:
        continue

    processed_count += 1
    print(f"Traitement de l'ID {id_val} ({index}/{total_ids})")

    # Premier endpoint: /issues/{id_val}/
    api_url = f"https://www.brief.me/api/issues/{id_val}/?format=json"
    response = requests.get(api_url)

    # Si le premier endpoint ne retourne pas 200, essayer /news/{id_val}/
    if response.status_code != 200:
        api_url = f"https://www.brief.me/api/news/{id_val}/?format=json"
        response = requests.get(api_url)

    if response.status_code == 200:
        data = response.json()
        intro = data.get("intro", "")
        outro = data.get("outro", "")
        # Concaténer intro et outro dans un corpus
        corpus = (intro + " " + outro).strip()
        resultats[id_val] = corpus
    else:
        print(f"Erreur lors de la requête pour l'id {id_val} (code {response.status_code})")

    # Sauvegarde intermédiaire tous les 100 enregistrements traités
    if processed_count % 100 == 0:
        backup_filename = f"ids_corpus_backup_{processed_count}.json"
        with open(backup_filename, 'w', encoding='utf-8') as f:
            json.dump(resultats, f, ensure_ascii=False, indent=2)
        print(f"Sauvegarde intermédiaire effectuée dans '{backup_filename}' après {processed_count} enregistrements.")

# Sauvegarde finale du dictionnaire complet
with open('ids_corpus.json', 'w', encoding='utf-8') as f:
    json.dump(resultats, f, ensure_ascii=False, indent=2)

print(f"{len(resultats)} IDs traités et enregistrés dans 'ids_corpus.json'.")
