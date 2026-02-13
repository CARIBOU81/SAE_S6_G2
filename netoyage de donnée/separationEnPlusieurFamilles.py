import json
import os
from collections import defaultdict
from dotenv import load_dotenv

load_dotenv()

# Fichiers d'entrée et sortie depuis les variables d'environnement
FICHIER_ENTREE = os.getenv("OUTPUT_FILE2")   # ex: donneesTraiter.jsonl
DOSSIER_SORTIE = os.getenv("OUTPUT_FILE3")   # ex: dossier donneesClasser/

if not FICHIER_ENTREE or not DOSSIER_SORTIE:
    raise ValueError("Les variables d'environnement OUTPUT_FILE2 et OUTPUT_FILE3 doivent être définies.")

# Création du dossier de sortie s'il n'existe pas
os.makedirs(DOSSIER_SORTIE, exist_ok=True)

# Le fichier toutesLesCateg.txt est dans le même dossier que le script
DOSSIER_SCRIPT = os.path.dirname(os.path.abspath(__file__))
FICHIER_CATEGORIES = os.path.join(DOSSIER_SCRIPT, "../Analyse de données/toutesLesCateg.txt")

# Familles à conserver
# J'ai garder les 10 familles les plus présentes
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

# Lecture des catégories + familles depuis le txt
categorie_famille = {}
with open(FICHIER_CATEGORIES, "r", encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if not line or "," not in line:
            continue
        cat, fam = line.split(",", 1)
        if fam in familles_a_garder:  # on ne garde que ces familles
            categorie_famille[cat.lower()] = fam

# Dictionnaire pour regrouper les objets JSON par famille
famille_jsons = defaultdict(list)

# Lecture du JSONL et regroupement par famille
with open(FICHIER_ENTREE, "r", encoding="utf-8") as f:
    for line in f:
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

        familles_ajoutees = set()
        for cat in categories.split(","):
            cat_clean = cat.strip().lower()
            fam = categorie_famille.get(cat_clean)
            if fam and fam not in familles_ajoutees:
                famille_jsons[fam].append(obj)
                familles_ajoutees.add(fam)

# Écriture des JSONL par famille
for fam, objets in famille_jsons.items():
    nom_fichier = f"{fam.replace(' ', '_').replace('&', 'et')}.jsonl"
    chemin_sortie = os.path.join(DOSSIER_SORTIE, nom_fichier)
    with open(chemin_sortie, "w", encoding="utf-8") as f:
        for obj in objets:
            f.write(json.dumps(obj, ensure_ascii=False) + "\n")

print(f"Fichiers JSONL pour les familles sélectionnées créés dans : {DOSSIER_SORTIE}")
