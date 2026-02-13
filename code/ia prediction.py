import re
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report


# =========================
# CONFIG
# =========================

FILES = {
    "tout": "C:/Users/louan/OneDrive/Documents/but-info/S6/SAE/SAE_S6_G2/data/yelp_academic_reviews4students.jsonl",
    
}


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
    data = pd.read_json(path, lines=True, encoding="utf-8", encoding_errors="ignore")

    df = pd.DataFrame({
        "texte": data["text"],
        "stars": data["stars"]
    })

    print(f"✓ Données chargées : {len(df)} lignes")
    print(df["stars"].value_counts().sort_index())

    return df


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
    df["clean_text"] = df["texte"].apply(clean_text)

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
    model = LogisticRegression(
        max_iter=1000,
        class_weight="balanced",
        n_jobs=-1
    )

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
