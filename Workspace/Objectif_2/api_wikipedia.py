from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)
WIKIPEDIA_API_URL = "https://fr.wikipedia.org/w/api.php"

def sanitize_filename(name):
    # Remplace les caractères non alphanumériques par un underscore pour créer un nom de fichier valide
    return "".join(c if c.isalnum() else "_" for c in name)

@app.route('/get_article', methods=['GET'])
def get_article():
    # Récupération du titre de l'article passé en paramètre
    title = request.args.get('title', '')
    if not title:
        return jsonify({"error": "Le paramètre 'title' est requis."}), 400

    # Définition des paramètres pour l'appel à l'API Wikipedia
    params = {
        "action": "query",
        "format": "json",
        "prop": "extracts",
        "explaintext": True,
        "titles": title
    }
    
    # Appel à l'API Wikipedia
    response = requests.get(WIKIPEDIA_API_URL, params=params)
    if response.status_code != 200:
        return jsonify({"error": "Erreur lors de l'appel à l'API Wikipedia"}), 500

    data = response.json()
    pages = data.get("query", {}).get("pages", {})

    # Extraction du texte de l'article (l'identifiant de page est dynamique)
    article_text = ""
    for page_id, page in pages.items():
        article_text = page.get("extract", "")
    
    # Création d'un nom de fichier sécurisé en fonction du titre
    safe_title = sanitize_filename(title)
    filename = f"article_{safe_title}.txt"
    
    # Sauvegarde de l'article dans un fichier texte
    with open(filename, "w", encoding="utf-8") as f:
        f.write(article_text)

    return jsonify({"title": title, "file": filename, "text": article_text})

if __name__ == "__main__":
    app.run(debug=True)
