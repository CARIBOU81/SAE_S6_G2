import pandas as pd
import os
from collections import Counter
from dotenv import load_dotenv

# --- 1. CONFIGURATION ---
load_dotenv()
FICHIER_ENTREE = os.getenv("INPUT_REVIEWS")
DOSSIER_SORTIE = "donnees_triees_auto"
os.makedirs(DOSSIER_SORTIE, exist_ok=True)

# C'est ici ta "LIMITE VARIABLE"
# Si tu mets 10, il créera 10 fichiers pour les 10 types d'établissements les plus fréquents.
# Si tu mets 50, il en fera 50.
NOMBRE_DE_CATEGORIES_A_EXTRAIRE = 10

def extraire_categories_dynamiques():
    print(f"--- 1. Chargement et Analyse de : {FICHIER_ENTREE} ---")

    try:
        # On charge les données
        df = pd.read_json(FICHIER_ENTREE, lines=True)
        df = df.dropna(subset=['categories']) # On nettoie

        # --- ANALYSE INTELLIGENTE ---
        print("Analyse des catégories en cours...")

        # On prend toutes les chaines de caractères "Restaurants, Pizza, Bar"
        # On les sépare par la virgule pour avoir une liste géante de tous les mots clés
        toutes_categories = []
        for liste_cat in df['categories']:
            # On sépare par ", " et on ajoute à la liste globale
            mots = [mot.strip() for mot in liste_cat.split(',')]
            toutes_categories.extend(mots)

        # On compte les répétitions (ex: "Restaurants" apparaît 5000 fois)
        compteur = Counter(toutes_categories)

        # On récupère seulement le TOP X défini plus haut
        top_categories = compteur.most_common(NOMBRE_DE_CATEGORIES_A_EXTRAIRE)

        print(f"\nTop {NOMBRE_DE_CATEGORIES_A_EXTRAIRE} catégories détectées :")
        for cat, count in top_categories:
            print(f"- {cat} ({count} établissements)")

        print("-" * 30)

        # --- GÉNÉRATION DES FICHIERS ---
        for cat_nom, count in top_categories:

            # On filtre le DataFrame original
            df_filtre = df[df['categories'].str.contains(cat_nom, case=False, na=False)]

            # Nom de fichier propre
            nom_clean = cat_nom.replace(" & ", "_").replace(" ", "_").replace("/", "_")
            nom_fichier = f"yelp_{nom_clean}.json"
            chemin_complet = os.path.join(DOSSIER_SORTIE, nom_fichier)

            # Sauvegarde
            df_filtre.to_json(chemin_complet, orient='records', lines=True)
            print(f"✅ Fichier créé : {nom_fichier} ({len(df_filtre)} lignes)")

        print("-" * 30)
        print("Terminé !")

    except Exception as e:
        print(f"Erreur : {e}")

if __name__ == "__main__":
    extraire_categories_dynamiques()