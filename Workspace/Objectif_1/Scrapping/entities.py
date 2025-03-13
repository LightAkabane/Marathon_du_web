# Installation des dépendances si nécessaire
# pip install spacy pqdm
# python -m spacy download fr_core_news_md

import spacy
import pandas as pd
import json
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from pqdm.processes import pqdm  # Parallelisation + Progress Bar

# Charger le modèle de langue français de spaCy
nlp = spacy.load("fr_core_news_md")

# Charger les stopwords depuis un fichier texte
def load_stopwords(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        return [ligne.strip() for ligne in f]


# Fonction d'extraction des entités pour un seul texte
def extract_entities_from_text(params):
    """
    Extrait les entités nommées d'un texte donné en utilisant spaCy,
    en supprimant les stopwords et en fusionnant les entités composées.
    """
    article_id, text, stopwords = params  # Déballer les paramètres
    try:
        if not text:
            return (article_id, [])  # Retourner un ID + liste vide

        doc = nlp(text)
        unique_entities = {}

        articles = {"le", "la", "les", "l'", "du", "de", "des", "un", "une"}

        for ent in doc.ents:
            entity_text = ent.text.strip().lower()  # Normaliser en minuscules

            # Vérifier si l'entité contient uniquement des stopwords
            if all(word in stopwords for word in entity_text.split()):
                continue  # Ignorer cette entité

            # Supprimer les articles en début/fin d'entité
            words = entity_text.split()
            if words[0] in articles:
                words = words[1:]
            if words and words[-1] in articles:
                words = words[:-1]
            entity_text = " ".join(words)

            # Vérifier si l'entité inversée existe déjà (ex: "Macron Emmanuel" et "Emmanuel Macron")
            sorted_entity = " ".join(sorted(entity_text.split()))
            entity_type = ent.label_

            # Supprimer les termes parasites
            if entity_text in {"de", "la", "l'", "du"}:
                continue

            # Éviter les doublons
            if sorted_entity in unique_entities:
                continue

            unique_entities[sorted_entity] = entity_type

        return (article_id, [(entity_type, entity) for entity, entity_type in unique_entities.items()])

    except Exception as e:
        print(f" Erreur sur l'article {article_id}: {e}")
        return (article_id, [])  # Retourner un ID avec une liste vide en cas d'erreur

# Fonction principale pour extraire les entités depuis un fichier JSON avec `pqdm`
def extract_named_entities_from_json(json_path, stopwords_path, num_workers=4):
    """
    Charge un fichier JSON et extrait les entités nommées en parallèle avec `pqdm`,
    en conservant le numéro des articles.

    :param json_path: Chemin du fichier JSON contenant les textes.
    :param stopwords_path: Chemin du fichier contenant les stopwords.
    :param num_workers: Nombre de processus parallèles.
    :return: Un DataFrame contenant les entités extraites.
    """
    # Charger les stopwords
    stopwords = load_stopwords(stopwords_path)

    # Charger les données JSON
    with open(json_path, "r", encoding="utf-8") as file:
        data = json.load(file)

    # Vérifier la structure du JSON (conserver le numéro des articles)
    extracted_data = []

    # Préparer la liste des textes pour l'extraction parallèle
    articles = [(article_id, item["texte"], stopwords) for article_id, item in data.items() if "texte" in item]

    # Appliquer l'extraction des entités en parallèle avec `pqdm`
    results = pqdm(articles, extract_entities_from_text, n_jobs=num_workers)

    # Construction du DataFrame
    for article_id, entities in results:
        for entity_type, entity in entities:
            extracted_data.append({
                "article_id": article_id,  # Conserver le numéro d'article
                "entity_type": entity_type,
                "entity": entity
            })

    df = pd.DataFrame(extracted_data)
    return df


# Définition des chemins des fichiers
json_path = "clean_articles.json"  # Remplace par le bon fichier
stopwords_path = "stopwords-fr.txt"
stopwords = load_stopwords(stopwords_path)

# Extraction des entités depuis le JSON avec `pqdm`
df_entities = extract_named_entities_from_json(json_path, stopwords_path, num_workers=4)

# Exporter en CSV
csv_path = "entites_nommes.csv"
df_entities.to_csv(csv_path, index=False, encoding="utf-8")

print(f"✅ Extraction terminée. Fichier CSV généré : {csv_path}")

df_entities

def generate_wordclouds_by_category(df):
    """Génère un nuage de mots distinct pour chaque type d'entité (LOC, ORG, PER, MISC)."""
    categories = ["LOC", "ORG", "PER", "MISC"]
    for category in categories:
        words = " ".join(df[df["entity_type"] == category]["entity"])
        if words:  # Vérifier si la catégorie contient des entités
            wordcloud = WordCloud(width=800, height=400, background_color="white", stopwords=set(stopwords)).generate(words)
            
            plt.figure(figsize=(10, 5))
            plt.imshow(wordcloud, interpolation="bilinear")
            plt.axis("off")
            plt.title(f"Nuage de mots pour {category}")
            plt.show()


# Génération des nuages de mots par catégorie
generate_wordclouds_by_category(df_entities)

# Définir le chemin du fichier de sortie sur Kaggle
json_output_path = "entities.json"

# Transformer le DataFrame en JSON et l'enregistrer
df_entities.to_json(json_output_path, orient="records", force_ascii=False, indent=4)

print(f" Fichier JSON exporté avec succès : {json_output_path}")