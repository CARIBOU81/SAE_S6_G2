import json
import sys
import os

fichier_entree = "C:/Users/flocon/Documents/sae6/yelp_academic_dataset_user4students.jsonl"

# On sépare le dossier et le nom du fichier
dossier = os.path.dirname(fichier_entree)
nom_du_fichier = os.path.basename(fichier_entree)

# On fabrique le bon chemin de sortie : C:/Users/.../sae6/nettoye_yelp_academic...
fichier_sortie = os.path.join(dossier, "nettoye_" + nom_du_fichier)

print(f"🔥 C'est parti pour l'extermination des amis !")
print(f"📁 Fichier d'entrée : {fichier_entree}")
print(f"📁 Fichier de sortie : {fichier_sortie}")

# On ouvre le fichier d'origine en lecture et le nouveau en écriture
try:
    with open(fichier_entree, 'r', encoding='utf-8') as f_in, \
         open(fichier_sortie, 'w', encoding='utf-8') as f_out:

        lignes_traitees = 0

        for ligne in f_in:
            if not ligne.strip():
                continue

            donnees = json.loads(ligne)

            # On supprime la liste d'amis
            donnees.pop("friends", None)

            # On écrit la ligne nettoyée
            f_out.write(json.dumps(donnees) + '\n')

            # On affiche la progression toutes les 50 000 lignes
            lignes_traitees += 1
            if lignes_traitees % 50000 == 0:
                print(f"⏳ {lignes_traitees} utilisateurs nettoyés...")

    print(f"✅ Terminé ! Le nouveau fichier est prêt : {fichier_sortie}")

except FileNotFoundError:
    print("🚨 Erreur : Je ne trouve pas le fichier d'entrée. Vérifie bien le chemin !")
except Exception as e:
    print(f"🚨 Une erreur inattendue est survenue : {e}")
