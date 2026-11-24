import csv
from pathlib import Path

from app.services.classifier import classify_ticket


BASE_DIR = Path(__file__).resolve().parent

DATASET_PATH = BASE_DIR / "datasets" / "reply_quality.csv"
RESULTS_PATH = BASE_DIR / "reply_quality_results.csv"


def evaluate_replies():
    results = []

    with DATASET_PATH.open(
        "r", encoding="utf-8-sig", newline=""
    ) as file:
        dataset = list(csv.DictReader(file))

    if not dataset:
        raise ValueError("Reply evaluation dataset is empty")

    for index, row in enumerate(dataset, start=1):
        message = row["message"]

        print(f"Evaluating {index}/{len(dataset)}: {message}")

        try:
            prediction = classify_ticket(message)

            category = prediction.category.value
            priority = prediction.priority.value
            article_ids = prediction.knowledge_article_ids
            reply = prediction.draft_reply
            error = ""

        except Exception as exc:
            category = ""
            priority = ""
            article_ids = []
            reply = ""
            error = f"{type(exc).__name__}: {exc}"

        results.append({
            "id": row["id"],
            "message": message,
            "expected_article_id": row["expected_article_id"],
            "expected_language": row["expected_language"],
            "predicted_category": category,
            "predicted_priority": priority,
            "retrieved_article_ids": ",".join(map(str, article_ids)),
            "generated_reply": reply,
            "groundedness": "",
            "language": "",
            "safety": "",
            "relevance": "",
            "error": error,
        })

    with RESULTS_PATH.open(
        "w", encoding="utf-8-sig", newline=""
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=list(results[0].keys()),
        )

        writer.writeheader()
        writer.writerows(results)

    successful = sum(not item["error"] for item in results)

    print("\n=== REPLY QUALITY EVALUATION ===")
    print(f"Total: {len(results)}")
    print(f"Processed: {successful}")
    print(f"Errors: {len(results) - successful}")
    print(f"Results saved to: {RESULTS_PATH}")
    print("Manual scoring is required.")


if __name__ == "__main__":
    evaluate_replies()
