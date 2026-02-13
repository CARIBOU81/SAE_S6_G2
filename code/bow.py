# --- yelp_bow.py ---

from dotenv import load_dotenv
import os
import json
import re
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer

# 1️⃣ Charger les variables d'environnement du fichier .env
load_dotenv()

# 2️⃣ Récupérer les chemins depuis le .env
input_reviews = os.getenv("INPUT_REVIEWS")
input_business = os.getenv("INPUT_BUSINESS")
output_file = os.getenv("OUTPUT_FILE")

print("📂 Reviews file:", input_reviews)
print("🏢 Business file:", input_business)
print("💾 Output file:", output_file)

# 3️⃣ Charger les avis Yelp
data = []
with open(input_reviews, "r", encoding="utf-8") as f:
    for line in f:
        data.append(json.loads(line))

df = pd.DataFrame(data)
print(f"✅ {len(df)} avis chargés")

# 4️⃣ Nettoyer le texte
def clean_text(s):
    s = s.lower()
    s = re.sub(r"http\S+", " ", s)       # supprimer URLs
    s = re.sub(r"[^a-z\s]", " ", s)      # garder lettres et espaces
    s = re.sub(r"\s+", " ", s).strip()
    return s

df["clean_text"] = df["text"].apply(clean_text)

# 5️⃣ Créer le modèle Bag-of-Words
vectorizer = CountVectorizer(stop_words="english", ngram_range=(1,2), min_df=5)
X_bow = vectorizer.fit_transform(df["clean_text"])
print(f"🧮 Matrice BoW : {X_bow.shape}")

# 6️⃣ (Optionnel) Créer la matrice TF-IDF
tfidf = TfidfTransformer()
X_tfidf = tfidf.fit_transform(X_bow)
print("📊 TF-IDF calculé.")

# 7️⃣ (Optionnel) Sauvegarder les résultats
if output_file and output_file != "Mettre le chemin du fichier de sortie":
    df.to_csv(output_file, index=False)
    print(f"💾 Résultats sauvegardés dans : {output_file}")

# 8️⃣ Exemple : afficher les mots les plus fréquents
word_freq = X_bow.sum(axis=0).A1
vocab = vectorizer.get_feature_names_out()
freq_df = pd.DataFrame({"word": vocab, "freq": word_freq})
print("\n🔝 Mots les plus fréquents :")
print(freq_df.sort_values("freq", ascending=False).head(15))
