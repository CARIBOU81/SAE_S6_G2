Présentation du projet

La SAE du sixième semestre est un projet visant à analyser des avis clients sur des entreprises à l'aide de techniques de traitement de données et d'intelligence artificielle (IA).

---

1. Installation des dépendances

Lancer PowerShell (`Win + R`, puis taper `powershell` et appuyer sur Entrée).

    Mise en place de Llama 3

Entrer la commande suivante pour installer Ollama :
`irm https://ollama.com/install.ps1 | iex`

Une fois installé, entrer la commande suivante pour télécharger et lancer le modèle :
`ollama run llama3`

   Installation des dépendances Python

Entrer la commande suivante pour installer les bibliothèques requises :
`pip install torch transformers pandas scikit-learn python-dotenv tqdm ollama`

---

2. Mise en place du fichier .env

* Créer un fichier nommé `.env` à la racine du projet.
* À l'aide du fichier modèle `demo.env`, remplir les informations nécessaires dans le fichier `.env`.

---

3. Exécution des programmes de tri

Exécuter les fichiers suivants (de préférence dans cet ordre) :
1. `entreprise.py`
2. `nettoyage_donnees.py`
3. `separation_familles.py`

---

4. Exécution des programmes d'IA

Une fois les étapes précédentes terminées, vous pouvez exécuter les programmes d'IA.