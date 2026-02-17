# BoW.py
# Vectorisation Bag-of-Words

from dotenv import load_dotenv
import os
import json
import re
import pandas as pd
import joblib
from sklearn.feature_extraction.text import CountVectorizer

# Chargement des variables d'environnement
load_dotenv()

INPUT_REVIEWS = os.getenv("INPUT_REVIEWS")
OUTPUT_DIR = os.getenv("OUTPUT_DIR", "bow_output")

os.makedirs(OUTPUT_DIR, exist_ok=True)

print("Fichier reviews :", INPUT_REVIEWS)
print("Dossier de sortie :", OUTPUT_DIR)

# Paramètre : nombre maximal d'avis
MAX_SAMPLES = 250_000

# Chargement des données (limité à MAX_SAMPLES)
data = []
with open(INPUT_REVIEWS, "r", encoding="utf-8") as f:
    for i, line in enumerate(f):
        if i >= MAX_SAMPLES:
            break
        data.append(json.loads(line))

df = pd.DataFrame(data)
print(f"{len(df)} avis chargés (lecture limitée à {MAX_SAMPLES})")

# Nettoyage du texte
def clean_text(text):
    text = text.lower()
    text = re.sub(r"http\S+", " ", text)        # supprimer URLs
    text = re.sub(r"[^a-z\s]", " ", text)      # garder lettres et espaces
    text = re.sub(r"\s+", " ", text).strip()
    return text

df["clean_text"] = df["text"].apply(clean_text)

# Création des labels de polarité
def create_label(stars):
    if stars > 3:
        return "positive"
    elif stars < 3:
        return "negative"
    else:
        return "neutral"

df["sentiment"] = df["stars"].apply(create_label)

# Vectorisation Bag-of-Words
"""
Paramètres choisis :

- stop_words="english" → suppression mots vides
- ngram_range=(1,2) → unigrammes + bigrammes
- max_features=30 000 → contrôle taille vocabulaire
- min_df=20 → suppression mots trop rares
"""

vectorizer = CountVectorizer(
    stop_words="english",
    ngram_range=(1, 2),
    max_features=30_000,
    min_df=20
)

X_bow = vectorizer.fit_transform(df["clean_text"])
y = df["sentiment"]

print("Matrice Bag-of-Words :", X_bow.shape)

# -------------------------------
# Sauvegarde du vectorizer et des labels
# -------------------------------

joblib.dump(vectorizer, os.path.join(OUTPUT_DIR, "bow_vectorizer.pkl"))

df[["sentiment"]].to_csv(
    os.path.join(OUTPUT_DIR, "labels.csv"),
    index=False
)

print("Vectorizer et labels sauvegardés.")

# -------------------------------
# Analyse exploratoire : mots les plus fréquents
# -------------------------------

word_freq = X_bow.sum(axis=0).A1
vocab = vectorizer.get_feature_names_out()

freq_df = pd.DataFrame({
    "word": vocab,
    "frequency": word_freq
}).sort_values("frequency", ascending=False)

freq_df.to_csv(
    os.path.join(OUTPUT_DIR, "word_frequencies.csv"),
    index=False
)

print("\nTop 15 mots les plus fréquents :")
print(freq_df.head(15))
