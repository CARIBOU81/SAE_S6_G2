import json
import re
import pandas as pd
from sklearn import svm
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report
import os
from dotenv import load_dotenv
from pathlib import Path

# =========================
# CONFIG
# =========================

load_dotenv()

FICHIER_AVIS = os.getenv("INPUT_REVIEWS")
FICHIER_BUSINESS = os.getenv("INPUT_BUSINESS")
FICHIER_SORTIE = os.getenv("OUTPUT_FILE")

# 1. Définit le chemin du dossier (via variable d'env ou chemin en dur)
dossier_data = os.getenv("OUTPUT_FILE3")
path = Path(dossier_data)

FILES = {}

# 2. Vérifie que le dossier existe
if path.exists():
    # 3. Récupère tous les fichiers .json
    for file_path in path.glob("*.jsonl"):
        # file_path.stem = nom du fichier sans .json (ex: "Hotels.json" -> "Hotels")
        # str(file_path) = le chemin complet
        FILES[file_path.stem] = str(file_path)

print("Fichiers utilisés :", FILES)


# =========================
# FONCTIONS UTILES
# =========================

def clean_text(text):
    text = text.lower()
    text = re.sub(r"http\S+", "", text)
    text = re.sub(r"[^a-zàâçéèêëîïôûùüÿñæœ\s]", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def load_dataset(path):
    data = []

    # Vérification simple si le fichier existe
    if not path or not os.path.exists(path):
        print(f"⚠️ Fichier introuvable : {path}")
        return pd.DataFrame(columns=["text", "stars"])

    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            try:
                # La magie opère ici : json.loads comprend automatiquement le format
                review = json.loads(line)

                # On extrait proprement
                data.append({
                    "text": review.get("text", ""), # .get évite le crash si la clé manque
                    "stars": review.get("stars", 0)
                })
            except json.JSONDecodeError:
                continue # On saute juste la ligne si elle est illisible

    return pd.DataFrame(data)


# =========================
# BOUCLE PRINCIPALE
# =========================

for etablissement, filepath in FILES.items():

    print(f"\n=============================")
    print(f" MODELE POUR : {etablissement.upper()}")
    print(f"=============================")

    # 1. Chargement
    df = load_dataset(filepath)
    print("Nb lignes :", len(df))
    print(df["stars"].value_counts())

    # 2. Nettoyage
    df["clean_text"] = df["text"].apply(clean_text)

    # (optionnel) réduire pour aller plus vite
    df = df.sample(200000, random_state=42)

    # 3. Split
    X_train, X_test, y_train, y_test = train_test_split(
        df["clean_text"],
        df["stars"],
        test_size=0.2,
        random_state=42,
        stratify=df["stars"]
    )

    # 4. TF-IDF (UN par type)
    vectorizer = TfidfVectorizer(
        max_features=200000,
        ngram_range=(1, 2),
        stop_words="english"
    )

    X_train_vec = vectorizer.fit_transform(X_train)
    X_test_vec = vectorizer.transform(X_test)

    # 5. Modèle
    model = svm.SVC(kernel='linear')

    model.fit(X_train_vec, y_train)

    # 6. Évaluation
    y_pred = model.predict(X_test_vec)

    print("\n--- RESULTATS ---")
    print(classification_report(y_test, y_pred))

    accuracy = (y_test == y_pred).mean()
    print(f"Accuracy : {accuracy:.4f}")

    # 7. Sauvegarde prédictions
    df_pred = pd.DataFrame({
        "true_stars": y_test.values,
        "predicted_stars": y_pred
    })

    output_file = f"predictions_{etablissement}.csv"
    df_pred.to_csv(output_file, index=False)

    print(f"Fichier sauvegardé : {output_file}")
