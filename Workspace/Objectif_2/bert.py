import json
import csv
import torch
from transformers import AutoTokenizer, AutoModel

def clean_text(text):
    """
    Nettoie le texte en remplaçant les retours à la ligne par des espaces et en supprimant les espaces superflus.
    """
    return text.replace("\n", " ").strip()

def get_pooled_embedding(text, tokenizer, model, pooling="max"):
    """
    Tokenise le texte et extrait l'embedding pour chaque token à partir de BERT,
    puis applique une opération de pooling (max ou moyenne) pour obtenir un vecteur fixe.
    
    La sortie brute de BERT est un tenseur de forme (1, sequence_length, hidden_size).
    """
    inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
    with torch.no_grad():
        outputs = model(**inputs)
    
    # On récupère la sortie brute : embeddings pour chaque token.
    # La forme est (1, sequence_length, hidden_size) que l'on réduit en (sequence_length, hidden_size)
    token_embeddings = outputs.last_hidden_state.squeeze(0)
    
    if pooling == "max":
        # Appliquer le max pooling sur la dimension des tokens
        pooled_embedding = torch.max(token_embeddings, dim=0)[0]
    elif pooling == "mean":
        # Appliquer le mean pooling sur la dimension des tokens
        pooled_embedding = torch.mean(token_embeddings, dim=0)
    else:
        raise ValueError("Le paramètre pooling doit être 'max' ou 'mean'")
    
    return pooled_embedding.numpy()

def main():
    # Charger le fichier JSON contenant les URLs et les textes associés
    with open("extrait_articles_cleaned.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    
    # Choix du modèle : ici CamemBERT pour le français
    model_name = "camembert-base"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModel.from_pretrained(model_name)
    
    # Choix du type de pooling : 'max' ou 'mean'
    pooling_type = "max"  # vous pouvez passer à "mean" si vous préférez
    
    # Ouvrir le fichier CSV en écriture pour stocker l'URL et l'embedding associé
    with open("articles_embeddings.csv", "w", encoding="utf-8", newline="") as csvfile:
        fieldnames = ["url", "embedding"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for url, text in data.items():
            # Nettoyage du texte
            text_clean = clean_text(text)
            # Extraction de l'embedding avec pooling
            embedding = get_pooled_embedding(text_clean, tokenizer, model, pooling=pooling_type)
            # Conversion du vecteur en chaîne de caractères (séparé par des espaces)
            embedding_str = " ".join(map(str, embedding.tolist()))
            writer.writerow({"url": url, "embedding": embedding_str})

if __name__ == "__main__":
    main()
