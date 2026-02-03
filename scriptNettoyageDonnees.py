import json
import os
import re
import unicodedata

# ----------------------------
# CONFIG
# ----------------------------
INPUT_REVIEWS = "yelp_academic_reviews4students.jsonl"
INPUT_BUSINESS = "yelp_academic_dataset_business.json"
OUTPUT_DIR = "donneesTraiter"

OUTPUT_REVIEWS = os.path.join(OUTPUT_DIR, "reviews_clean.jsonl")
OUTPUT_BUSINESS = os.path.join(OUTPUT_DIR, "business_clean.json")

os.makedirs(OUTPUT_DIR, exist_ok=True)

# ----------------------------
# UTILS
# ----------------------------
def clean_text(text):
    if not text:
        return ""

    # Normalisation unicode (accents)
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", "ignore").decode("ascii")

    # Suppression des emojis et caractères spéciaux
    text = re.sub(r"[^a-zA-Z0-9\s.,!?']", " ", text)

    # Suppression espaces multiples
    text = re.sub(r"\s+", " ", text).strip()

    return text.lower()


# ----------------------------
# CLEAN REVIEWS
# ----------------------------
def clean_reviews():
    seen_texts = set()
    kept = 0
    removed = 0

    with open(INPUT_REVIEWS, "r", encoding="utf-8") as fin, \
         open(OUTPUT_REVIEWS, "w", encoding="utf-8") as fout:

        for line in fin:
            review = json.loads(line)

            raw_text = review.get("text", "")
            cleaned_text = clean_text(raw_text)

            # Supprimer avis vides
            if cleaned_text == "":
                removed += 1
                continue

            # Supprimer doublons
            if cleaned_text in seen_texts:
                removed += 1
                continue

            seen_texts.add(cleaned_text)
            review["text"] = cleaned_text

            fout.write(json.dumps(review, ensure_ascii=False) + "\n")
            kept += 1

    print(f"✔ Avis conservés : {kept}")
    print(f"✘ Avis supprimés : {removed}")


# ----------------------------
# CLEAN BUSINESS
# ----------------------------
def clean_business():
    kept = 0

    with open(INPUT_BUSINESS, "r", encoding="utf-8") as fin, \
         open(OUTPUT_BUSINESS, "w", encoding="utf-8") as fout:

        for line in fin:
            business = json.loads(line)

            business["name"] = clean_text(business.get("name", ""))
            business["city"] = clean_text(business.get("city", ""))
            business["categories"] = clean_text(business.get("categories", ""))

            fout.write(json.dumps(business, ensure_ascii=False) + "\n")
            kept += 1

    print(f"✔ Entreprises nettoyées : {kept}")


# ----------------------------
# MAIN
# ----------------------------
if __name__ == "__main__":
    print("Nettoyage des avis...")
    clean_reviews()

    print("\nNettoyage des entreprises...")
    clean_business()

    print("\n✅ Données nettoyées dans le dossier 'donneesTraiter'")
