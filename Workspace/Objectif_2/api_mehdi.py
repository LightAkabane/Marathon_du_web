import requests
import json
import pandas as pd
import re
import os

# 🌍 URLs de l'API
NEWS_URL = "https://www.brief.me/api/news/"
ISSUES_URL = "https://www.brief.me/api/issues/"

# 📂 Fichiers de sortie
NEWS_JSON_FILE = "briefme_news.json"
ISSUES_JSON_FILE = "briefme_issues.json"
EVENTS_CSV_FILE = "output_events_combined.csv"

# 📌 Charger les événements des utilisateurs pour compter les vues
def load_event_data():
    if not os.path.exists(EVENTS_CSV_FILE):
        print("⚠️ Le fichier CSV des événements n'existe pas.")
        return {}, {}

    df = pd.read_csv(EVENTS_CSV_FILE, delimiter=";", dtype=str)

    # 📌 Filtrer les événements "pv" (page vue)
    df_views = df[df["Event Name"] == "pv"].copy()

    # 📌 Extraire `id_article` depuis l'URL
    def extract_article_id(url):
        if pd.isna(url):
            return None
        match = re.search(r"/article/(\d{4}-\d{2}-\d{2}-(\d+))", url)
        return match.group(2) if match else None

    df_views["id_article"] = df_views["url"].apply(extract_article_id)
    count_article_vue = df_views["id_article"].value_counts().to_dict()

    # 📌 Extraire `id_issue` depuis l'URL
    def extract_issue_id(url):
        if pd.isna(url):
            return None
        match = re.search(r"/issue/(\d+)", url)
        return match.group(1) if match else None

    df_views["id_issue"] = df_views["url"].apply(extract_issue_id)
    count_issue_vue = df_views["id_issue"].value_counts().to_dict()

    return count_article_vue, count_issue_vue

# 📝 Chargement des compteurs de vues
count_article_vue, count_issue_vue = load_event_data()

# 📌 Mise à jour progressive des fichiers JSON
def update_json_file(file_path, new_data):
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            try:
                existing_data = json.load(f)
            except json.JSONDecodeError:
                existing_data = []
    else:
        existing_data = []

    # Ajout des nouvelles entrées
    existing_data.extend(new_data)

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(existing_data, f, indent=4, ensure_ascii=False)

# 📌 Fonction pour récupérer toutes les pages d'une API avec écriture progressive
def fetch_data(api_url, output_file, data_type):
    page = 1
    while True:
        url = f"{api_url}?page={page}"
        print(f"📡 Récupération des {data_type} (page {page}) : {url}...")

        response = requests.get(url)
        if response.status_code != 200:
            print(f"❌ Erreur {response.status_code} lors de la récupération des {data_type}.")
            break

        data = response.json()
        if "results" not in data or not data["results"]:
            print(f"✅ Fin de la pagination des {data_type}.")
            break

        new_entries = []
        for entry in data["results"]:
            item_id = str(entry["id"])
            processed_entry = {
                "id": item_id,
                "slug": entry["slug"],
                "title": entry["title"],
                "published_at": entry.get("published_at", None),
                "authors": entry["issue"]["authors"] if entry.get("issue") else None,
                "section": entry["section"]["title"] if entry.get("section") else None,
                "category": entry["category"][0]["title"] if entry.get("category") else None,
                "count_views": count_article_vue.get(item_id, 0) if data_type == "articles" else count_issue_vue.get(item_id, 0)
            }
            new_entries.append(processed_entry)

        # Mise à jour immédiate du JSON
        update_json_file(output_file, new_entries)

        print(f"✅ Page {page} ajoutée avec {len(new_entries)} {data_type}.")
        page += 1

# 🏁 Exécution du script
print("\n🔄 Extraction des ARTICLES (news)...")
fetch_data(NEWS_URL, NEWS_JSON_FILE, "articles")

print("\n🔄 Extraction des ÉDITIONS (issues)...")
fetch_data(ISSUES_URL, ISSUES_JSON_FILE, "éditions")

print(f"\n✅ Extraction et mise à jour terminées ! Les résultats sont dans '{NEWS_JSON_FILE}' et '{ISSUES_JSON_FILE}'")
