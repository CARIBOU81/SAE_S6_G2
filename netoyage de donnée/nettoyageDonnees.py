import json
import os
import re
import unicodedata
from dotenv import load_dotenv
from tqdm import tqdm  # <--- IMPORT AJOUTÉ

# ----------------------------
# CONFIG
# ----------------------------
load_dotenv()

FICHIER_ENTREE = os.getenv("OUTPUT_FILE")    # donneesMerch.jsonl
FICHIER_SORTIE = os.getenv("OUTPUT_FILE2")   # donneesTraiter.jsonl

if not FICHIER_ENTREE or not FICHIER_SORTIE:
    raise ValueError("❌ OUTPUT_FILE ou OUTPUT_FILE2 manquant dans le .env")

# Créer le dossier de sortie si besoin
os.makedirs(os.path.dirname(FICHIER_SORTIE), exist_ok=True)

# ----------------------------
# UTILS
# ----------------------------
def clean_text(text):
    if not text:
        return ""

    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", "ignore").decode("ascii")
    text = re.sub(r"[^a-zA-Z0-9\s.,!?']", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text.lower()

# ----------------------------
# CLEAN MERGED DATA
# ----------------------------
def clean_merged_file():
    seen_texts = set()
    kept = 0
    removed = 0

    # 1. On compte d'abord le nombre total de lignes pour la barre de chargement
    print("📊 Calcul du nombre de lignes à traiter...")
    try:
        with open(FICHIER_ENTREE, "r", encoding="utf-8") as f:
            # Cette méthode est rapide pour compter les lignes sans charger le fichier
            total_lines = sum(1 for _ in f)
    except FileNotFoundError:
        print(f"❌ Erreur : Le fichier {FICHIER_ENTREE} est introuvable.")
        return

    print(f"🔄 Début du traitement de {total_lines} lignes...")

    # 2. Traitement avec barre de chargement
    with open(FICHIER_ENTREE, "r", encoding="utf-8") as fin, \
         open(FICHIER_SORTIE, "w", encoding="utf-8") as fout:

        # tqdm enveloppe 'fin' et affiche la progression
        for line in tqdm(fin, total=total_lines, unit="line", desc="Nettoyage"):

            if not line.strip():
                removed += 1
                continue

            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                removed += 1
                continue

            # Nettoyage des champs texte s'ils existent
            if "text" in obj:
                obj["text"] = clean_text(obj.get("text", ""))

            if "name" in obj:
                obj["name"] = clean_text(obj.get("name", ""))

            if "city" in obj:
                obj["city"] = clean_text(obj.get("city", ""))

            if "categories" in obj:
                obj["categories"] = clean_text(obj.get("categories", ""))

            # Si le texte est vide après nettoyage → on jette
            if "text" in obj and obj["text"] == "":
                removed += 1
                continue

            # Suppression des doublons sur le texte
            if "text" in obj:
                if obj["text"] in seen_texts:
                    removed += 1
                    continue
                seen_texts.add(obj["text"])

            fout.write(json.dumps(obj, ensure_ascii=False) + "\n")
            kept += 1

    print("-" * 40)
    print(f"✔ Lignes conservées : {kept}")
    print(f"✘ Lignes supprimées : {removed}")
    print(f"✅ Fichier nettoyé écrit dans : {FICHIER_SORTIE}")

# ----------------------------
# MAIN
# ----------------------------
if __name__ == "__main__":
    print("🧹 Nettoyage du fichier fusionné...")
    print(f"📥 Entrée : {FICHIER_ENTREE}")
    print(f"📤 Sortie : {FICHIER_SORTIE}")
    print("-" * 40)

    clean_merged_file()