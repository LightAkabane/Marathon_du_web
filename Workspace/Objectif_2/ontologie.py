import requests
import json
import time

# Liste des catégories à utiliser
categories = [
    "Géographie",      # Remplace "Monde"
    "Politique",
    "Société",
    "Économie",
    "Environnement",
    "Science",         # Remplace "Sciences"
    "Technologie",
    "Culture",
    "Médias",
]

base_url = "https://fr.wikipedia.org/w/api.php"

def get_articles_for_category(category, limit=10):
    params = {
        "action": "query",
        "list": "categorymembers",
        "cmtitle": f"Catégorie:{category}",
        "cmlimit": limit,
        "format": "json"
    }
    response = requests.get(base_url, params=params)
    if response.status_code == 200:
        data = response.json()
        # Retourner la liste des articles
        return data.get("query", {}).get("categorymembers", [])
    else:
        print(f"Erreur pour la catégorie {category} : {response.status_code}")
        return []

def get_article_content(pageid):
    params = {
        "action": "query",
        "prop": "extracts",
        "pageids": pageid,
        "explaintext": True,
        "format": "json"
    }
    response = requests.get(base_url, params=params)
    if response.status_code == 200:
        data = response.json()
        pages = data.get("query", {}).get("pages", {})
        # Les clés de pages sont des chaînes de caractères
        page = pages.get(str(pageid))
        if page:
            return page.get("extract", "")
    else:
        print(f"Erreur lors de la récupération du contenu pour la page {pageid}")
    return ""

# Dictionnaire pour stocker les résultats par catégorie
articles_by_category = {}

for cat in categories:
    articles = get_articles_for_category(cat)
    # Pour chaque article, ajouter son contenu textuel
    for article in articles:
        pageid = article.get("pageid")
        # Pour éviter de trop solliciter l'API, une courte pause peut être utile
        time.sleep(0.5)
        content = get_article_content(pageid)
        article["content"] = content
    articles_by_category[cat] = articles
    print(f"Catégorie: {cat} - {len(articles)} articles récupérés")

# Enregistrer les résultats dans un fichier JSON
output_file = "articles_wikipedia.json"
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(articles_by_category, f, ensure_ascii=False, indent=4)

print(f"Les articles et leur contenu ont été enregistrés dans le fichier {output_file}")
