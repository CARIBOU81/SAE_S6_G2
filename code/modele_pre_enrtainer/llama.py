import json
import os
from dotenv import load_dotenv
import ollama

load_dotenv()

FICHIER_AVIS = os.getenv("INPUT_REVIEWS")

# --- 1. FONCTION DE LA MÉTHODE 1 ---
def extraire_aspects(revue):
    prompt_system = """
    Tu es un expert en analyse de données. Ton objectif est d'extraire les aspects mentionnés dans une revue client et de déterminer le sentiment associé à chacun (positif ou négatif).
    Tu dois répondre UNIQUEMENT au format JSON valide, sous forme d'une liste d'objets contenant les clés 'aspect' et 'sentiment'.
    """

    # Appel à LLaMA 3 via Ollama en forçant le format JSON
    response = ollama.chat(model='llama3', messages=[
        {'role': 'system', 'content': prompt_system},
        {'role': 'user', 'content': revue},
    ], format='json')

    # Petit conseil : parfois l'IA se trompe de format, c'est bien de prévoir une sécurité
    try:
        return json.loads(response['message']['content'])
    except json.JSONDecodeError:
        return {"erreur": "JSON invalide retourné par LLaMA", "brut": response['message']['content']}

# --- 2. LECTURE DU FICHIER JSONL ET EXÉCUTION ---
chemin_fichier = FICHIER_AVIS

print(f"📂 Ouverture du fichier : {chemin_fichier}\n")

# On ouvre le fichier une seule fois
with open(chemin_fichier, 'r', encoding='utf-8') as f:

    # On crée une boucle qui va tourner 5 fois (de 0 à 4)
    for i in range(5):
        ligne = f.readline()

        # Sécurité : si le fichier a moins de 5 lignes, on arrête la boucle
        if not ligne:
            break

        # On convertit cette ligne en dictionnaire Python
        donnees_json = json.loads(ligne)

        # On extrait le texte de la review
        texte_de_la_revue = donnees_json.get("text", "")

        print("-" * 50)
        print(f"📝 --- AVIS N°{i + 1} ---")

        # J'ai ajouté une petite coupure pour ne pas inonder ton terminal si le texte est très long
        extrait_texte = texte_de_la_revue[:150] + "..." if len(texte_de_la_revue) > 150 else texte_de_la_revue
        print(f"💬 Texte : \"{extrait_texte}\"")

        # --- 3. EXÉCUTION DE L'IA ---
        if texte_de_la_revue:
            print("🤖 LLaMA 3 analyse le texte...")
            resultats_absa = extraire_aspects(texte_de_la_revue)

            print("✅ Résultat structuré obtenu :")
            print(json.dumps(resultats_absa, indent=4, ensure_ascii=False))
        else:
            print("❌ Erreur : La clé 'text' n'a pas été trouvée ou est vide.")

        print("\n") # Petit espace avant de passer à l'avis suivant