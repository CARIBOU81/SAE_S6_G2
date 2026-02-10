import os
import pandas as pd
import matplotlib.pyplot as plt
from dotenv import load_dotenv

load_dotenv()

# Dossier où se trouvent tes 10 fichiers JSONL
DOSSIER_FAMILLES = os.getenv("OUTPUT_FILE3")

if not DOSSIER_FAMILLES:
    raise ValueError("La variable d'environnement OUTPUT_FILE3 doit être définie.")

# Dossier pour sauvegarder les graphiques
DOSSIER_GRAPHIQUES = os.path.join(DOSSIER_FAMILLES, "graphs_businessPopulairesNoter")
os.makedirs(DOSSIER_GRAPHIQUES, exist_ok=True)

resultats_familles = []
resultats_correlations = []

# Parcours de tous les fichiers JSONL du dossier
for nom_fichier in os.listdir(DOSSIER_FAMILLES):
    if not nom_fichier.endswith(".jsonl"):
        continue

    chemin = os.path.join(DOSSIER_FAMILLES, nom_fichier)
    print(f"Analyse de {nom_fichier} ...")

    # Chargement du JSONL
    df = pd.read_json(chemin, lines=True)

    if "business_id" not in df.columns or "stars" not in df.columns:
        print(f"⚠️ Colonnes manquantes dans {nom_fichier}, ignoré.")
        continue

    # Nom de la famille depuis le nom du fichier
    famille = nom_fichier.replace(".jsonl", "").replace("_", " ")

    # =========================
    # 📊 Stats globales famille
    # =========================

    nb_total_avis = len(df)
    nb_business = df["business_id"].nunique()
    note_moyenne = df["stars"].mean()

    resultats_familles.append({
        "famille": famille,
        "nb_business": nb_business,
        "nb_total_avis": nb_total_avis,
        "note_moyenne": note_moyenne
    })

    print(f"  {famille} -> business: {nb_business}, avis: {nb_total_avis}, note moyenne: {note_moyenne:.2f}")

    # =========================
    # 📈 Stats par business
    # =========================

    stats_business = (
        df.groupby("business_id")
          .agg(
              nb_reviews=("stars", "count"),
              mean_stars=("stars", "mean")
          )
          .reset_index()
    )

    # Corrélation popularité vs note (au niveau business)
    if len(stats_business) > 1:
        corr = stats_business["nb_reviews"].corr(stats_business["mean_stars"])
    else:
        corr = float("nan")

    resultats_correlations.append({
        "famille": famille,
        "correlation": corr,
        "nb_business": len(stats_business)
    })

    print(f"  Corrélation (par business) pour {famille} : {corr}")

    # Scatter plot par business pour la famille
    plt.figure()
    plt.scatter(stats_business["nb_reviews"], stats_business["mean_stars"])
    plt.xlabel("Nombre d'avis (par business)")
    plt.ylabel("Note moyenne (par business)")
    plt.title(f"Popularité vs Note moyenne - {famille}")

    nom_graph = f"{famille.replace(' ', '_')}_scatter_business.png"
    chemin_graph = os.path.join(DOSSIER_GRAPHIQUES, nom_graph)
    plt.tight_layout()
    plt.savefig(chemin_graph)
    plt.close()

# =========================
# 📁 DataFrames récap
# =========================

df_familles = pd.DataFrame(resultats_familles)
df_correlations = pd.DataFrame(resultats_correlations)

print("\n=== Résumé par famille ===")
print(df_familles)

print("\n=== Résumé des corrélations par famille ===")
print(df_correlations)

# Sauvegarde CSV
chemin_csv_familles = os.path.join(DOSSIER_FAMILLES, "resume_familles.csv")
df_familles.to_csv(chemin_csv_familles, index=False, encoding="utf-8")

chemin_csv_corr = os.path.join(DOSSIER_FAMILLES, "resume_correlations.csv")
df_correlations.to_csv(chemin_csv_corr, index=False, encoding="utf-8")

# =========================
# 📊 Graphiques globaux
# =========================

# 1) Nombre de business par famille
plt.figure()
plt.bar(df_familles["famille"], df_familles["nb_business"])
plt.xticks(rotation=45, ha="right")
plt.ylabel("Nombre de business")
plt.title("Nombre de business par famille")
plt.tight_layout()
plt.savefig(os.path.join(DOSSIER_GRAPHIQUES, "nb_business_par_famille.png"))
plt.close()

# 2) Note moyenne par famille
plt.figure()
plt.bar(df_familles["famille"], df_familles["note_moyenne"])
plt.xticks(rotation=45, ha="right")
plt.ylabel("Note moyenne")
plt.title("Note moyenne par famille")
plt.tight_layout()
plt.savefig(os.path.join(DOSSIER_GRAPHIQUES, "note_moyenne_par_famille.png"))
plt.close()

# 3) Popularité (nb total d'avis) vs note moyenne (par famille)
plt.figure()
plt.scatter(df_familles["nb_total_avis"], df_familles["note_moyenne"])
plt.xlabel("Nombre total d'avis (popularité famille)")
plt.ylabel("Note moyenne")
plt.title("Popularité vs Note moyenne (par famille)")

for _, row in df_familles.iterrows():
    plt.text(row["nb_total_avis"], row["note_moyenne"], row["famille"], fontsize=8)

plt.tight_layout()
plt.savefig(os.path.join(DOSSIER_GRAPHIQUES, "popularite_vs_note_moyenne_familles.png"))
plt.close()

print(f"\nCSV familles : {chemin_csv_familles}")
print(f"CSV corrélations : {chemin_csv_corr}")
print(f"Graphiques sauvegardés dans : {DOSSIER_GRAPHIQUES}")
