import pandas as pd
from pycaret.clustering import setup, create_model, plot_model

# Chargement des données
data = pd.read_csv("articles_clustered.csv")

# Configuration de l'environnement de clustering en indiquant la variable textuelle
clustering_setup = setup(data, text_features=['clean_content'], session_id=123)

# Création d'un modèle de clustering k-means avec k=4
km_model = create_model('kmeans', num_clusters=4, random_state=123)

# Affichage du graphique des clusters
plot_model(km_model, plot='cluster')
