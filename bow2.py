# --- bow_test_5_reviews.py ---

from dotenv import load_dotenv
import os
import json
import re
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer

# 1️⃣ Charger les variables d'environnement
load_dotenv()
input_reviews = os.getenv("INPUT_REVIEWS")

# 2️⃣ Charger seulement les 5 premières reviews du fichier JSONL
reviews = []
with open(input_reviews, "r", encoding="utf-8") as f:
    for i, line in enumerate(f):
        if i >= 5:
            break
        reviews.append(json.loads(line))

df = pd.DataFrame(reviews)
print(f"✅ {len(df)} reviews chargées")

# 3️⃣ Nettoyage du texte
def clean_text(s):
    s = s.lower()
    s = re.sub(r"http\S+", " ", s)
    s = re.sub(r"[^a-z\s]", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s

df["clean_text"] = df["text"].apply(clean_text)

# 4️⃣ Création du Bag-of-Words
vectorizer = CountVectorizer(stop_words="english")
X_bow = vectorizer.fit_transform(df["clean_text"])

# 5️⃣ Affichage sous forme de DataFrame pour visualiser
bow_df = pd.DataFrame(X_bow.toarray(), columns=vectorizer.get_feature_names_out())
bow_df.index = [f"review_{i+1}" for i in range(len(df))]

print("\n📊 Matrice Bag-of-Words (5 reviews) :")
print(bow_df)

# 6️⃣ (Optionnel) Aperçu des mots les plus fréquents
word_freq = X_bow.sum(axis=0).A1
vocab = vectorizer.get_feature_names_out()
freq_df = pd.DataFrame({"word": vocab, "freq": word_freq})
print("\n🔝 Mots les plus fréquents :")
print(freq_df.sort_values("freq", ascending=False).head(15))
