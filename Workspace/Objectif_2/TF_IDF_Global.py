import json
import os
import math
import re
from collections import Counter
from bs4 import BeautifulSoup
import nltk
from nltk.corpus import stopwords

# Télécharger les stopwords en français (si ce n'est pas déjà fait)
nltk.download('stopwords')
stop_words = set(stopwords.words('french'))

# Ajouter ici vos stopwords personnalisés
stop_words_personnalises = {"a", "30", "|", "7", "déjà", "Briefme", "Brief me", "Brief.me", "brief me", "briefme", "dy", "ni", "plus", "sans", "gratuitessayez", "gratuitme", "sansengagement", "publactualitéexpliquéebriefme", "gratuitabonnezvousmon", "essai", "gratuitement"}
stop_words = stop_words.union(stop_words_personnalises)

# Fonction de nettoyage du texte
def nettoyage_texte(texte):
    # Supprimer les URLs
    texte = re.sub(r'http\S+|www\S+|https\S+', '', texte)
    # Supprimer les artefacts HTML et mentions Twitter
    texte = re.sub(r'&amp;|&|@', '', texte)
    # Supprimer les caractères spéciaux et les artefacts comme "û" ou "_"
    texte = re.sub(r'[^\w\s]|û|_', '', texte)
    # Convertir en minuscules
    texte = texte.lower()
    # Supprimer les espaces inutiles
    texte = texte.strip()
    return texte

# 1. Charger le fichier JSON avec les correspondances URL -> chemin vers le fichier HTML
with open('saved_pages/correspondances.json', 'r', encoding='utf-8') as f:
    correspondances = json.load(f)

# 2. Fonction pour extraire le texte brut d'un fichier HTML
def extraire_texte(filepath):
    with open(filepath, 'r', encoding='utf-8') as file:
        contenu = file.read()
    soup = BeautifulSoup(contenu, 'html.parser')
    return soup.get_text()

# Récupérer le texte de chaque article et appliquer le prétraitement
# On crée un dictionnaire qui associe chaque URL au texte nettoyé de l'article
articles_textes = {}
for url, filepath in correspondances.items():
    texte = extraire_texte(filepath)
    texte_nettoye = nettoyage_texte(texte)
    articles_textes[url] = texte_nettoye

# Concaténer tous les textes pour obtenir une vision globale
texte_global = " ".join(articles_textes.values())

# 3. Calcul du TF global en filtrant les stopwords
def calculer_tf(texte, stop_words):
    mots = texte.split()  # le texte est déjà en minuscules
    mots = [mot for mot in mots if mot not in stop_words]
    total = len(mots)
    freq = Counter(mots)
    tf = {mot: count / total for mot, count in freq.items()}
    return tf

tf_global = calculer_tf(texte_global, stop_words)

# 4. Charger le corpus de Wikipedia_data pour calculer l'IDF
dossier_wiki = 'Wikipedia_data'
documents = []
for nom in os.listdir(dossier_wiki):
    if nom.endswith('.txt'):
        chemin = os.path.join(dossier_wiki, nom)
        with open(chemin, 'r', encoding='utf-8') as f:
            documents.append(f.read().lower())

# Calcul de l'IDF sur le corpus Wikipedia
def calculer_idf(corpus):
    N = len(corpus)
    docs_mots = [set(doc.split()) for doc in corpus]
    idf = {}
    tous_mots = set().union(*docs_mots)
    for mot in tous_mots:
        n_t = sum(1 for doc in docs_mots if mot in doc)
        # Formule d'IDF avec lissage
        idf[mot] = math.log((N + 1) / (n_t + 1)) + 1
    return idf

idf_wiki = calculer_idf(documents)

# 5. Calculer le TF-IDF global : TF de l'ensemble des articles * IDF calculé sur Wikipedia
tfidf_global = {mot: tf_val * idf_wiki.get(mot, 1) for mot, tf_val in tf_global.items()}

# 6. Pour chaque mot, déterminer la liste des articles contenant ce mot
# On parcourt chaque article et on stocke les mots présents dans un set pour une recherche rapide
articles_mots = {url: set(texte.split()) for url, texte in articles_textes.items()}

mot_articles = {}
for mot in tfidf_global:
    mot_articles[mot] = [url for url, mots in articles_mots.items() if mot in mots]

# 7. Créer un dictionnaire final associant à chaque mot son score TF-IDF et la liste des articles
resultats = {mot: {"score": tfidf_global[mot], "articles": mot_articles[mot]} for mot in tfidf_global}

# 8. Enregistrer le dictionnaire dans un fichier JSON
with open('tfidf_scores.json', 'w', encoding='utf-8') as f:
    json.dump(resultats, f, ensure_ascii=False, indent=4)

print("Les scores TF-IDF et la liste des articles contenant chaque mot ont été enregistrés dans le fichier 'tfidf_scores.json'.")
