import pandas as pd
import re

# Chargement du fichier CSV source
df = pd.read_csv("combined_events.csv", delimiter=';')

# 1. Filtrer sur l'Event Name "pv"
df = df[df["Event Name"] == "pv"]

# 2. Exclure certaines URL spécifiques
urls_a_exclure = [
    "https://app.brief.me/",
    "app://brief.me/index.html#/",
    "https://localhost/index.html#/"
]
df = df[~df["url"].isin(urls_a_exclure)]

# 3. Supprimer les colonnes inutiles
df = df.drop(columns=["backend", "pid"])

# 4. Remplacer les URL commençant par "app://brief.me/index.html#/" par "https://www.brief.me/"
df["url"] = df["url"].str.replace(
    r'^app://brief.me/index.html#/', 
    'https://www.brief.me/', 
    regex=True
)

# 5. Appliquer un filtre global pour exclure les URL en localhost
df = df[~df["url"].str.startswith("https://localhost/index.html#/")]

# 6. Détection des URL contenant une date (format AAAA-MM-JJ)
pattern = r'\d{4}-\d{2}-\d{2}'
df["contains_date"] = df["url"].str.contains(pattern, regex=True)

# 7. Séparation des URL avec et sans date
df_with_date = df[df["contains_date"]].copy()
df_without_date = df[~df["contains_date"]].copy()

# 8. Définition des patterns à exclure sur df_without_date (autres filtres)
patterns_exclus = (
    df_without_date["url"].str.startswith("https://app.brief.me/?login_token") |
    df_without_date["url"].str.startswith("https://app.brief.me/?redirect") |
    df_without_date["url"].str.startswith("https://app.brief.me/notifications") |
    df_without_date["url"].str.startswith("https://app.brief.me/?standalone=true") |
    df_without_date["url"].str.contains("token", case=False, na=False) |
    df_without_date["url"].str.startswith("https://www.brief.me/accounts/") |
    df_without_date["url"].str.startswith("file:") |
    df_without_date["url"].str.startswith("https://www.brief.me/abonnement/") |
    df_without_date["url"].str.startswith("https://www.brief.me/user/") |
    df_without_date["url"].str.startswith("https://app.brief.me/logout") |
    df_without_date["url"].str.startswith("https://www.brief.me/compte/") |
    df_without_date["url"].str.startswith("https://www.brief.me/recrutement") |
    df_without_date["url"].str.startswith("https://www.brief.me/contact/") |
    df_without_date["url"].str.startswith("https://www.brief.me/login-requested/") |
    df_without_date["url"].str.startswith("https://www.brief.me/offrir/") |
    df_without_date["url"].str.startswith("https://www.brief.me/upload/") |
    df_without_date["url"].str.startswith("https://www.brief.me/tutoriel-GAR/") |
    (df_without_date["url"] == "https://www.brief.me/") |
    (df_without_date["url"] == "app://brief.me/index.html#/notifications")
)

# Exclusion des URL indésirables dans df_without_date
df_without_date = df_without_date[~patterns_exclus]

# Affichage des statistiques
print("Total d'urls :", len(df))
print("Urls avec date :", len(df_with_date))
print("Urls sans date (après nettoyage) :", len(df_without_date))

# Sauvegarde des résultats
df_with_date.to_csv("pretreat_data/donnees_with_date.csv", index=False, sep=';')
# Sauvegarde des URL sans date
df_without_date.to_csv("pretreat_data/donnees_without_date.csv", index=False, sep=';')
# Fusion finale et sauvegarde
df_all = pd.concat([df_with_date, df_without_date])
df_all.to_csv("pretreat_data/donnees_all.csv", index=False, sep=';')
