# ======================================================
# IMPORTS
# ======================================================

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from dotenv import load_dotenv
from sklearn.feature_extraction.text import TfidfVectorizer

sns.set(style="whitegrid")

# ======================================================
# LOAD ENV VARIABLES
# ======================================================

load_dotenv()

REVIEWS_PATH = os.getenv("INPUT_REVIEWS")
BUSINESS_PATH = os.getenv("INPUT_BUSINESS")
USER_PATH = os.getenv("INPUT_USER")

print("Chargement des données...")

# ======================================================
# LOAD DATA
# ======================================================

reviews = pd.read_json(REVIEWS_PATH, lines=True)
business = pd.read_json(BUSINESS_PATH, lines=True)
users = pd.read_json(USER_PATH, lines=True)

print("Reviews shape:", reviews.shape)
print("Business shape:", business.shape)
print("Users shape:", users.shape)

# ======================================================
# BASIC FEATURE ENGINEERING
# ======================================================

# Longueur des avis
reviews["length"] = reviews["text"].apply(len)

# Polarité
def polarity(stars):
    if stars > 3:
        return "positif"
    elif stars < 3:
        return "negatif"
    else:
        return "neutre"

reviews["polarity"] = reviews["stars"].apply(polarity)

# ======================================================
# 1️⃣ RÉPARTITION DES NOTES
# ======================================================

plt.figure()
reviews["stars"].value_counts().sort_index().plot(kind="bar")
plt.title("Répartition des notes")
plt.xlabel("Nombre d'étoiles")
plt.ylabel("Nombre d'avis")
plt.show()

# ======================================================
# 2️⃣ LONGUEUR DES AVIS
# ======================================================

plt.figure()
reviews.groupby("stars")["length"].mean().plot(kind="bar")
plt.title("Longueur moyenne des avis par note")
plt.ylabel("Longueur moyenne (caractere)")
plt.show()

print("\nLongueur moyenne par polarité :")
print(reviews.groupby("polarity")["length"].mean())

# ======================================================
# 3️⃣ MERGE AVEC BUSINESS
# ======================================================

df = reviews.merge(
    business,
    on="business_id",
    suffixes=("_review", "_business")
)

print("\nColonnes après merge business :")
print(df.columns)

# Analyse popularité business vs note moyenne
business_stats = df.groupby("business_id").agg(
    nb_reviews=("stars_review", "count"),
    avg_rating=("stars_review", "mean")
)

plt.figure()
plt.scatter(business_stats["nb_reviews"],
            business_stats["avg_rating"])
plt.title("Popularité du business vs Note moyenne")
plt.xlabel("Nombre d'avis")
plt.ylabel("Note moyenne")
plt.show()

# ======================================================
# 4️⃣ MERGE AVEC USERS
# ======================================================

df = df.merge(users, on="user_id")

print("\nColonnes après merge users :")
print(df.columns)

# Les gros reviewers sont-ils plus sévères ?
user_stats = df.groupby("user_id").agg(
    nb_reviews_written=("stars_review", "count"),
    avg_given_rating=("stars_review", "mean")
)

plt.figure()
plt.scatter(user_stats["nb_reviews_written"],
            user_stats["avg_given_rating"])
plt.title("Nombre d'avis écrits vs Note moyenne donnée")
plt.xlabel("Nombre d'avis écrits")
plt.ylabel("Note moyenne donnée")
plt.show()

# ======================================================
# 5️⃣ ANALYSE VOCABULAIRE TF-IDF
# ======================================================

positive_reviews = reviews[reviews["polarity"] == "positif"]["text"]
negative_reviews = reviews[reviews["polarity"] == "negatif"]["text"]

vectorizer = TfidfVectorizer(
    stop_words="english",
    max_features=1000
)

X_pos = vectorizer.fit_transform(positive_reviews)
X_neg = vectorizer.fit_transform(negative_reviews)

words = vectorizer.get_feature_names_out()

top_pos = np.argsort(X_pos.mean(axis=0)).A1[-10:]
top_neg = np.argsort(X_neg.mean(axis=0)).A1[-10:]

print("\nTop 10 mots positifs :")
print([words[i] for i in top_pos])

print("\nTop 10 mots négatifs :")
print([words[i] for i in top_neg])

print("\nAnalyse terminée.")
