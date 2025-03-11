import requests
import csv
import os
import time
import random
import json
from fake_useragent import UserAgent

# Définir l'emplacement du fichier CSV et du dossier de sauvegarde
csv_file = "unique_urls.csv"  # Remplace par ton chemin vers le fichier CSV
output_folder = "saved_pages"  # Dossier principal
json_file = os.path.join(output_folder, "correspondances.json")  # Fichier JSON

# Dictionnaire pour stocker les correspondances URL → fichier
if os.path.exists(json_file):
    with open(json_file, "r", encoding="utf-8") as f:
        correspondances = json.load(f)
    print(f"📄 JSON chargé ({len(correspondances)} pages déjà enregistrées)")
else:
    correspondances = {}

# Générer un User-Agent aléatoire
ua = UserAgent()

# Création des sous-dossiers (article, edition, panorama, definitions)
categories = ["article", "edition", "panorama", "definitions"]
for category in categories:
    os.makedirs(os.path.join(output_folder, category), exist_ok=True)

# Ouvrir le fichier CSV et lire les URLs
with open(csv_file, mode='r', encoding='utf-8') as file:
    reader = csv.DictReader(file)  # Supposons que le CSV a une colonne 'url'

    session = requests.Session()
    compteur = len(correspondances)  # Commencer à partir des pages déjà téléchargées

    for row in reader:
        url = row['url']

        # Vérifier si l'URL a déjà été téléchargée
        if url in correspondances:
            print(f"⏭️ Déjà téléchargée : {url}")
            continue  # Passer à l'URL suivante

        print(f"📥 Récupération de : {url}")

        # Générer un User-Agent aléatoire
        headers = {
            "User-Agent": ua.random,
        }

        for attempt in range(3):  # Essayer 3 fois en cas d’échec
            try:
                response = session.get(url, headers=headers, timeout=10)

                if response.status_code == 200:
                    # Extraire le type de contenu (article, edition, panorama, definitions)
                    parts = url.split("/")
                    if len(parts) > 4:
                        category = parts[3]  # Ex: "article", "edition", etc.
                    else:
                        category = "autres"  # Si non catégorisable

                    # Créer le bon dossier si ce n'est pas un des 4 connus
                    category_folder = os.path.join(output_folder, category)
                    os.makedirs(category_folder, exist_ok=True)

                    # Construire le nom du fichier
                    file_name = parts[-1] + ".html"
                    file_path = os.path.join(category_folder, file_name)

                    # Sauvegarder la page HTML
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write(response.text)

                    # Sauvegarder la correspondance URL → fichier
                    correspondances[url] = file_path

                    # Mettre à jour le JSON immédiatement après chaque sauvegarde
                    with open(json_file, "w", encoding="utf-8") as f:
                        json.dump(correspondances, f, indent=4, ensure_ascii=False)

                    compteur += 1  # Incrémenter le compteur
                    print(f"✅ Page sauvegardée sous {file_path} ({compteur})")
                    break  # Sortir de la boucle retry si succès

                elif response.status_code == 403:
                    print(f"⚠️ Accès interdit à {url} (403). Possible blocage.")
                    break

                elif response.status_code == 429:
                    print(f"⚠️ Trop de requêtes (429). Attente de 30 secondes...")
                    time.sleep(30)  # Attente plus longue avant retry
                else:
                    print(f"❌ Erreur HTTP {response.status_code} pour {url}")

            except requests.exceptions.RequestException as e:
                print(f"⚠️ Erreur de connexion : {e}")

            # Attente aléatoire entre 1 et 5 secondes pour éviter d’être bloqué
            time.sleep(random.uniform(1, 5))

print(f"\n🎯 {compteur} pages ont été téléchargées et classées.")
print(f"📂 Les correspondances sont sauvegardées dans {json_file}.")
