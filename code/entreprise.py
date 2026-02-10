import pandas as pd
import os
import sys
from dotenv import load_dotenv

# 1. On charge les variables du .env
load_dotenv()

# 2. On récupère les noms de fichiers
FICHIER_AVIS = os.getenv("INPUT_REVIEWS")
FICHIER_BUSINESS = os.getenv("INPUT_BUSINESS")
FICHIER_SORTIE = os.getenv("OUTPUT_FILE")

# --- BLOC DE SÉCURITÉ (Très important) ---
# Si jamais le .env est mal rempli, on arrête tout de suite pour éviter des erreurs bizarres
if not FICHIER_AVIS or not FICHIER_BUSINESS:
    print("❌ ERREUR : Les noms de fichiers ne sont pas trouvés dans le .env")
    print("Vérifiez que vous avez bien défini INPUT_REVIEWS et INPUT_BUSINESS.")
    sys.exit(1) # Arrête le script proprement

print(f"📂 Configuration chargée :")
print(f"   - Avis : {FICHIER_AVIS}")
print(f"   - Business : {FICHIER_BUSINESS}")
print("-" * 30)

# --- LA SUITE DE VOTRE SCRIPT RESTE IDENTIQUE ---

print("1. Chargement du dictionnaire des entreprises...")
# On ne charge QUE les colonnes utiles pour économiser la mémoire (RAM)
cols_a_garder = ['business_id', 'name', 'categories', 'city', 'stars']

df_business = pd.read_json(FICHIER_BUSINESS, lines=True)
# On ne garde que les colonnes choisies
df_business = df_business[cols_a_garder]

# On renomme la note du business pour ne pas la confondre avec la note de l'avis
df_business = df_business.rename(columns={'stars': 'business_rating'})

print(f"   -> {len(df_business)} entreprises chargées en mémoire.")

print("2. Chargement et fusion des avis (Patience...)...")

# Astuce : Si votre fichier d'avis est GIGANTESQUE (plusieurs Go),
# on le charge par morceaux ("chunks") pour ne pas saturer l'ordi.
chunk_size = 100000
chunks = []

# Lecture du fichier d'avis par blocs
reader = pd.read_json(FICHIER_AVIS, lines=True, chunksize=chunk_size)

for i, chunk in enumerate(reader):
    print(f"   Traitement du bloc n°{i+1}...")

    # C'est ici que la magie opère : on colle les infos business sur les avis
    chunk_merged = pd.merge(chunk, df_business, on='business_id', how='left')

    # On remplit les vides si une entreprise n'est pas trouvée
    chunk_merged['categories'] = chunk_merged['categories'].fillna('Inconnu')

    # On ajoute ce bloc traité à la liste (ou on pourrait écrire direct dans le fichier)
    chunks.append(chunk_merged)

# On recolle tous les morceaux
print("3. Finalisation...")
df_final = pd.concat(chunks)

print("4. Sauvegarde dans le nouveau fichier...")
df_final.to_json(FICHIER_SORTIE, orient='records', lines=True)

print(f"✅ Terminé ! Vous avez un fichier '{FICHIER_SORTIE}' avec {len(df_final)} lignes.")
print("Exemple d'une ligne :")
print(df_final[['text', 'name', 'categories']].iloc[0])