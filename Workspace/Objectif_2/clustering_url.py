import json
import pandas as pd
import csv

# Charger le fichier JSON
with open('extrait_articles.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Créer un DataFrame avec deux colonnes : 'url' et 'texte'
df = pd.DataFrame(list(data.items()), columns=['url', 'texte'])

# Sauvegarder en CSV en définissant un caractère d'échappement
df.to_csv("extrait_articles.csv", index=False, encoding='utf-8', escapechar='\\', quoting=csv.QUOTE_MINIMAL)

print("Conversion terminée : extrait_articles.csv créé.")
