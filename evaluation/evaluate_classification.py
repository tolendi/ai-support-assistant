
import csv
from pathlib import Path
from collections import Counter
from app.services.classifier import classify_ticket


BASE_DIR = Path(__file__).resolve().parent

DATASET_PATH = BASE_DIR / "datasets" / "classification.csv"
RESULTS_PATH = BASE_DIR / "classification_results.csv"


def calculate_classification_metrics(results):
    categories = sorted({
        result["expected_category"]
        for result in results
    } | {
        result["predicted_category"]
        for result in results
        if result["predicted_category"]
    })

    metrics = []

    for category in categories:
        tp = sum(
            r["expected_category"] == category
            and r["predicted_category"] == category
            for r in results
        )

        fp = sum(
            r["expected_category"] != category
            and r["predicted_category"] == category
            for r in results
        )

        fn = sum(
            r["expected_category"] == category
            and r["predicted_category"] != category
            for r in results
        )

        precision = tp / (tp + fp) if tp + fp else 0.0
        recall = tp / (tp + fn) if tp + fn else 0.0

        f1 = (
            2 * precision * recall / (precision + recall)
            if precision + recall
            else 0.0
        )

        support = tp + fn

        metrics.append({
            "category": category,
            "precision": precision,
            "recall": recall,
            "f1": f1,
            "support": support,
        })

    return metrics


def evaluate_classification():
    results = []
    correct = 0

    with DATASET_PATH.open("r", encoding="utf-8-sig", newline="") as file:
        dataset = list(csv.DictReader(file))

    if not dataset:
        raise ValueError("Evaluation dataset is empty")

    for row in dataset:
        message = row["message"]
        expected = row["expected_category"]
        expected_priority = row["expected_priority"]

        print(f"Evaluating {row['id']}/{len(dataset)}: {message}")

        try:
            prediction = classify_ticket(message)
            predicted = prediction.category.value
            predicted_priority = prediction.priority.value
            priority_correct = predicted_priority == expected_priority
            is_correct = predicted == expected
            error = ""

            if is_correct:
                correct += 1

        except Exception as exc:
            predicted = ""
            is_correct = False
            error = f"{type(exc).__name__}: {exc}"
            predicted_priority = ""
            priority_correct = False

        results.append({
            "id": row["id"],
            "message": message,
            "expected_category": expected,
            "predicted_category": predicted,
            "correct": is_correct,
            "error": error,
            "expected_priority": expected_priority,
            "predicted_priority": predicted_priority,
            "priority_correct": priority_correct,
        })

    total = len(dataset)
    accuracy = correct / total * 100

    with RESULTS_PATH.open(
        "w", encoding="utf-8-sig", newline=""
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "id",
                "message",
                "expected_category",
                "predicted_category",
                "correct",
                "error",
                "expected_priority",
                "predicted_priority",
                "priority_correct",
            ],
        )
        writer.writeheader()
        writer.writerows(results)

    priority_correct_count = sum(
    result["priority_correct"] for result in results
    )

    priority_accuracy = priority_correct_count / total * 100

    print(f"Priority Accuracy: {priority_accuracy:.2f}%")

    print("\n=== CLASSIFICATION EVALUATION ===")
    print(f"Total: {total}")
    print(f"Correct: {correct}")
    print(f"Incorrect: {total - correct}")
    print(f"Accuracy: {accuracy:.2f}%")
    print(f"Results saved to: {RESULTS_PATH}")


    metrics = calculate_classification_metrics(results)

    print("\n=== CATEGORY METRICS ===")
    print(
        f"{'Category':<20}"
        f"{'Precision':>12}"
        f"{'Recall':>10}"
        f"{'F1':>10}"
        f"{'Support':>10}"
    )

    for item in metrics:
        print(
            f"{item['category']:<20}"
            f"{item['precision']:>12.2f}"
            f"{item['recall']:>10.2f}"
            f"{item['f1']:>10.2f}"
            f"{item['support']:>10}"
        )

    macro_precision = sum(
        item["precision"] for item in metrics
    ) / len(metrics)

    macro_recall = sum(
        item["recall"] for item in metrics
    ) / len(metrics)

    macro_f1 = sum(
        item["f1"] for item in metrics
    ) / len(metrics)

    print("\n=== MACRO AVERAGE ===")
    print(f"Macro Precision: {macro_precision:.4f}")
    print(f"Macro Recall:    {macro_recall:.4f}")
    print(f"Macro F1-score:  {macro_f1:.4f}")


    print("\n=== INCORRECT PREDICTIONS ===")
    for result in results:
        if not result["correct"]:
            print(
                f"ID {result['id']}: "
                f"expected={result['expected_category']}, "
                f"predicted={result['predicted_category']}"
            )
            if result["error"]:
                print(f"  Error: {result['error']}")


if __name__ == "__main__":
    evaluate_classification()
