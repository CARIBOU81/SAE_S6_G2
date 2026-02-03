import re
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report


# =========================
# 1. CHARGEMENT DU DATASET
# =========================

texts = []
stars = []
buffer = ""

with open("../data/yelp_academic_reviews4students.jsonl", "r", encoding="utf-8", errors="ignore") as f:
    for line in f:
        buffer += line.strip()

        # Une entrée complète se termine par }
        if buffer.endswith("}"):
            try:
                star_match = re.search(r"stars:(\d)", buffer)
                text_match = re.search(r'"text:""(.*?)"""', buffer)

                if star_match and text_match:
                    stars.append(int(star_match.group(1)))
                    texts.append(text_match.group(1))

            except:
                pass

            buffer = ""

df = pd.DataFrame({
    "text": texts,
    "stars": stars
})

print(df.head())
print("Nb lignes:", len(df))
print(df["stars"].value_counts())


# =========================
# 2. NETTOYAGE DU TEXTE
# =========================

def clean_text(text):
    text = text.lower()
    text = re.sub(r"http\S+", "", text)
    text = re.sub(r"[^a-zàâçéèêëîïôûùüÿñæœ\s]", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()

print("Nettoyage du texte...")
df["clean_text"] = df["text"].apply(clean_text)


# =========================
# 3. REDUCTION (OPTIONNEL)
# =========================
# Accélère énormément l'entraînement tout en gardant de très bons résultats

#df = df.sample(200000, random_state=42)

print("Dataset réduit:", len(df))


# =========================
# 4. TRAIN / TEST SPLIT
# =========================

X_train, X_test, y_train, y_test = train_test_split(
    df["clean_text"],
    df["stars"],
    test_size=0.2,
    random_state=42,
    stratify=df["stars"]
)


# =========================
# 5. TF-IDF
# =========================

vectorizer = TfidfVectorizer(
    max_features=1000000,
    ngram_range=(1, 2),
    stop_words="english"
)

print("Vectorisation TF-IDF...")
X_train_vec = vectorizer.fit_transform(X_train)
X_test_vec = vectorizer.transform(X_test)


# =========================
# 6. MODELE
# =========================

model = LogisticRegression(
    max_iter=1000,
    class_weight="balanced",
    n_jobs=-1
)

print("Entraînement du modèle...")
model.fit(X_train_vec, y_train)


# =========================
# 7. EVALUATION
# =========================

y_pred = model.predict(X_test_vec)

print("\n--- RESULTATS ---")
print(classification_report(y_test, y_pred))


# =========================
# 8. PREDICTION FINALE
# =========================

def predict_note(text):
    text = clean_text(text)
    vec = vectorizer.transform([text])
    return model.predict(vec)[0]


print("\n--- TEST PREDICTION ---")
print("Note prédite :", predict_note(
    "the food was excellent and the staff were super friendly"
))


df_pred = pd.DataFrame(y_pred, columns=['stars'])
df_pred.to_csv('predictions_stars.csv', index=False)
print("\nRésultats sauvegardés dans 'predictions_stars.csv'")
print("\nPremières 10 prédictions :")
print(df_pred.head(10))

accuracy = (y_test == y_pred).mean()
print(f"\nExactitude globale du modèle: {accuracy:.4f}")