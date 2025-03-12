import json
import os
import math
import re
from collections import Counter
from bs4 import BeautifulSoup
import nltk
from nltk.corpus import stopwords
from wordcloud import WordCloud
import matplotlib.pyplot as plt

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

# 3. Récupérer le texte de chaque article, le nettoyer et l'associer à son URL
articles_textes = {}
for url, filepath in correspondances.items():
    texte = extraire_texte(filepath)
    texte_nettoye = nettoyage_texte(texte)
    articles_textes[url] = texte_nettoye

# Concaténer tous les textes pour obtenir une vision globale
texte_global = " ".join(articles_textes.values())

# 4. Calcul du TF global en filtrant les stopwords
def calculer_tf(texte, stop_words):
    mots = texte.split()  # le texte est déjà en minuscules
    mots = [mot for mot in mots if mot not in stop_words]
    total = len(mots)
    freq = Counter(mots)
    tf = {mot: count / total for mot, count in freq.items()}
    return tf

tf_global = calculer_tf(texte_global, stop_words)

# 5. Charger le corpus de Wikipedia_data pour calculer l'IDF
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

# 6. Calculer le TF-IDF global : TF de l'ensemble des articles * IDF calculé sur Wikipedia
tfidf_global = {mot: tf_val * idf_wiki.get(mot, 1) for mot, tf_val in tf_global.items()}

# 7. Affichage d'un nuage de mots basé sur les scores TF-IDF
wordcloud = WordCloud(width=800, height=400, background_color="white", colormap="viridis")
wordcloud.generate_from_frequencies(tfidf_global)

plt.figure(figsize=(15, 7.5))
plt.imshow(wordcloud, interpolation='bilinear')
plt.axis("off")
plt.title("Nuage de mots basé sur TF-IDF", fontsize=20)
plt.show()
