import pandas as pd
import os
from dotenv import load_dotenv

# 1. Configuration
load_dotenv()

# Le fichier d'entrée (Le gros fichier JSON avec toutes les entreprises)
FICHIER_ENTREE = os.getenv("INPUT_REVIEWS")

# Le dossier où on va créer les 4 fichiers
DOSSIER_SORTIE = "donnees_triees"
os.makedirs(DOSSIER_SORTIE, exist_ok=True)

# LISTE DES 4 TYPES À EXTRAIRE
# Tu peux modifier cette liste pour changer les types de fichiers générés
TYPES_A_EXTRAIRE = [
    "Restaurants",
    "Shopping",
    "Health & Medical",
    "Hotels"
]

def generer_fichiers_separés():
    print(f"--- 1. Chargement du fichier maître : {FICHIER_ENTREE} ---")

    try:
        # On charge le gros fichier en mémoire
        df = pd.read_json(FICHIER_ENTREE, lines=True)

        # Nettoyage : On enlève les lignes qui n'ont pas de catégories (pour éviter les erreurs)
        df = df.dropna(subset=['categories'])

        print(f"Total entreprises chargées : {len(df)}")
        print("--- 2. Création des fichiers séparés ---")

        # BOUCLE : On parcourt nos 4 types
        for type_cible in TYPES_A_EXTRAIRE:

            # A. FILTRAGE
            # On cherche si le mot (ex: "Restaurants") est dans la liste des catégories
            # case=False permet de trouver "restaurants" ou "Restaurants"
            df_filtre = df[df['categories'].str.contains(type_cible, case=False, na=False)]

            if len(df_filtre) > 0:
                # B. CRÉATION DU NOM DE FICHIER PROPRE
                # On remplace les espaces et caractères spéciaux pour le nom du fichier
                # Exemple : "Health & Medical" devient "Health_Medical"
                nom_clean = type_cible.replace(" & ", "_").replace(" ", "_").replace("/", "_")
                nom_fichier_sortie = f"yelp_{nom_clean}.json"
                chemin_complet = os.path.join(DOSSIER_SORTIE, nom_fichier_sortie)

                # C. SAUVEGARDE
                # On écrit le fichier (orient='records', lines=True garde le format compatible Yelp)
                df_filtre.to_json(chemin_complet, orient='records', lines=True)

                print(f"✅ [CRÉÉ] {nom_fichier_sortie} : Contient {len(df_filtre)} établissements.")
            else:
                print(f"⚠️ [VIDE] Aucun établissement trouvé pour '{type_cible}'.")

        print("-" * 30)
        print(f"Opération terminée. Tes 4 fichiers sont dans le dossier '{DOSSIER_SORTIE}'.")

    except FileNotFoundError:
        print(f"ERREUR : Le fichier d'entrée '{FICHIER_ENTREE}' est introuvable.")
    except Exception as e:
        print(f"Une erreur est survenue : {e}")

# Lancer le programme
if __name__ == "__main__":
    generer_fichiers_separés()