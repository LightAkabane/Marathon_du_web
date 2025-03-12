import re
import json
import os
from bs4 import BeautifulSoup

# Fonction pour nettoyer le HTML et extraire le texte brut
def clean_html(html_text):
    soup = BeautifulSoup(html_text, "html.parser")
    return soup.get_text(separator="\n").strip()

# Fonction pour tenter de corriger le format JSON si nécessaire
def fix_json_format(data_str):
    fixed = re.sub(r'([{,]\s*)([a-zA-Z_]\w*)(\s*):', r'\1"\2"\3:', data_str)
    return fixed

# Exemple d'adaptation du traitement pour un fichier donné
def process_file(filepath):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        print(f"Erreur lors de la lecture du fichier {filepath}: {e}")
        return None

    # D'abord, on essaie d'extraire un bloc JSON si présent (cas classique)
    json_pattern = r'data:\s*(\{.*?\})\s*,template:'
    match = re.search(json_pattern, content, re.DOTALL)
    if match:
        data_str = match.group(1)
        try:
            data_json = json.loads(data_str)
        except json.JSONDecodeError as e:
            # Tenter de corriger le format
            fixed_data_str = fix_json_format(data_str)
            try:
                data_json = json.loads(fixed_data_str)
            except json.JSONDecodeError as e2:
                print(f"Erreur JSON persistante dans {filepath} : {e2}")
                data_json = None

        if data_json and "text" in data_json:
            # Extraction du contenu de la clé "text"
            text_content = data_json["text"]
            if isinstance(text_content, list):
                text_content = text_content[0] if text_content else ""
            return clean_html(text_content)

    # Sinon, si le bloc JSON n'est pas trouvé, on tente d'extraire le contenu HTML d'intérêt.
    # Ici, on peut par exemple chercher la zone de l'article dans une balise <div> spécifique.
    # Pour l'exemple, on recherche le premier paragraphe dans le corps de l'article.
    soup = BeautifulSoup(content, "html.parser")
    # Exemple : chercher la première balise <p> dans un conteneur de type "NewsRewind__item__content"
    container = soup.find("div", class_=re.compile("NewsRewind__item__content"))
    if container:
        p = container.find("p")
        if p:
            return clean_html(str(p))
    # Sinon, on extrait le texte brut de la page
    return clean_html(content)


# Exemple d'utilisation pour traiter plusieurs fichiers à partir d'un fichier de correspondance
def process_multiple_files(correspondances_file, output_file):
    with open(correspondances_file, "r", encoding="utf-8") as f:
        correspondances = json.load(f)

    results = {}
    for article_id, filepath in correspondances.items():
        print(f"Traitement de {filepath} (ID {article_id})")
        text = process_file(filepath)
        if text:
            results[article_id] = text
        else:
            print(f"Pas de texte extrait pour {filepath}")

    with open(output_file, "w", encoding="utf-8") as out:
        json.dump(results, out, ensure_ascii=False, indent=2)
    print(f"Extraction terminée, résultats enregistrés dans {output_file}")

# Exemple d'appel
if __name__ == "__main__":
    correspondances_file = "saved_pages/correspondances.json"  # fichier JSON : { "article_id": "chemin/vers/fichier.html", ... }
    output_file = "extrait_articles.json"
    process_multiple_files(correspondances_file, output_file)
