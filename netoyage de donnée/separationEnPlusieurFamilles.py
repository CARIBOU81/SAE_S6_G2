import json
import os
from collections import defaultdict
from dotenv import load_dotenv
from tqdm import tqdm  # <--- IMPORT AJOUTÉ

load_dotenv()

# ----------------------------
# CONFIG
# ----------------------------
# Fichiers d'entrée et sortie depuis les variables d'environnement
FICHIER_ENTREE = os.getenv("OUTPUT_FILE2")   # ex: donneesTraiter.jsonl
DOSSIER_SORTIE = os.getenv("OUTPUT_FILE3")   # ex: dossier donneesClasser/

if not FICHIER_ENTREE or not DOSSIER_SORTIE:
    raise ValueError("❌ Les variables d'environnement OUTPUT_FILE2 et OUTPUT_FILE3 doivent être définies.")

# Création du dossier de sortie s'il n'existe pas
os.makedirs(DOSSIER_SORTIE, exist_ok=True)

# Le fichier toutesLesCateg.txt est dans le même dossier que le script
DOSSIER_SCRIPT = os.path.dirname(os.path.abspath(__file__))
# Attention: vérifie bien que ce chemin relatif est correct par rapport à l'endroit où est ton script
FICHIER_CATEGORIES = os.path.join(DOSSIER_SCRIPT, "../Analyse de données/toutesLesCateg.txt")

# Familles à conserver
familles_a_garder = {
    "Restauration",
    "Bars & Vie nocturne",
    "Commerce",
    "Beauté & Bien-être",
    "Services",
    "Loisirs & Culture",
    "Services événementiels",
    "Automobile",
    "Santé",
    "Hôtellerie & Voyage"
}

# ----------------------------
# PRÉPARATION
# ----------------------------
print("⚙️  Chargement des catégories...")

# Lecture des catégories + familles depuis le txt
categorie_famille = {}
try:
    with open(FICHIER_CATEGORIES, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or "," not in line:
                continue
            cat, fam = line.split(",", 1)
            # Nettoyage basique pour matcher plus facilement
            if fam in familles_a_garder:
                categorie_famille[cat.lower()] = fam
except FileNotFoundError:
    raise FileNotFoundError(f"❌ Impossible de trouver le fichier de catégories : {FICHIER_CATEGORIES}")

# Dictionnaire pour regrouper les objets JSON par famille
famille_jsons = defaultdict(list)

# ----------------------------
# 1. CLASSEMENT (LECTURE)
# ----------------------------

# On compte les lignes pour la première barre de chargement
print("📊 Calcul du volume à traiter...")
try:
    with open(FICHIER_ENTREE, "r", encoding="utf-8") as f:
        total_lines = sum(1 for _ in f)
except FileNotFoundError:
    raise FileNotFoundError(f"❌ Impossible de trouver le fichier d'entrée : {FICHIER_ENTREE}")

print(f"🔄 Classement de {total_lines} entrées en cours...")

with open(FICHIER_ENTREE, "r", encoding="utf-8") as f:
    # Barre de chargement 1 : Lecture et tri
    for line in tqdm(f, total=total_lines, desc="Tri des données", unit="li"):
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            continue

        categories = obj.get("categories")
        if not categories:
            continue

        # On évite d'ajouter le même objet plusieurs fois dans la MÊME famille
        # (mais un objet peut appartenir à plusieurs familles différentes)
        familles_ajoutees_pour_cet_objet = set()

        for cat in categories.split(","):
            cat_clean = cat.strip().lower()
            fam = categorie_famille.get(cat_clean)

            if fam and fam not in familles_ajoutees_pour_cet_objet:
                famille_jsons[fam].append(obj)
                familles_ajoutees_pour_cet_objet.add(fam)

# ----------------------------
# 2. SAUVEGARDE (ÉCRITURE)
# ----------------------------
print(f"\n💾 Sauvegarde dans {len(famille_jsons)} fichiers familles...")

# Barre de chargement 2 : Écriture des fichiers
for fam, objets in tqdm(famille_jsons.items(), desc="Écriture fichiers", unit="fam"):
    nom_fichier = f"{fam.replace(' ', '_').replace('&', 'et')}.jsonl"
    chemin_sortie = os.path.join(DOSSIER_SORTIE, nom_fichier)

    with open(chemin_sortie, "w", encoding="utf-8") as f:
        for obj in objets:
            f.write(json.dumps(obj, ensure_ascii=False) + "\n")

print("-" * 40)
print(f"✅ Terminé ! Les fichiers sont dans : {DOSSIER_SORTIE}")