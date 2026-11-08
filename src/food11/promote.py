import argparse
import math

from mlflow.tracking import MlflowClient

TRACKING_URI = "http://127.0.0.1:5000"
MODEL_NAME = "food11"


def get_evaluation(client, version):
    if not version.run_id:
        raise ValueError(f"Model version {version.version} has no source run.")

    run = client.get_run(version.run_id)
    accuracy = run.data.metrics.get("test_accuracy")
    dataset = run.data.tags.get("evaluation_dataset")
    n = run.data.tags.get("evaluation_n")

    if accuracy is None:
        raise ValueError(
            f"Model version {version.version} has no test_accuracy."
        )
    if dataset is None or n is None:
        raise ValueError(
            f"Model version {version.version} is missing evaluation metadata."
        )

    accuracy = float(accuracy)
    n = int(n)

    if not 0 <= accuracy <= 1 or n <= 0:
        raise ValueError("Invalid evaluation accuracy or sample size.")

    return accuracy, dataset, n


def main():
    parser = argparse.ArgumentParser(description="Promote a Food-11 model.")
    parser.add_argument("--version", type=int, required=True)
    args = parser.parse_args()

    client = MlflowClient(tracking_uri=TRACKING_URI)

    champion = client.get_model_version_by_alias(MODEL_NAME, "champion")
    candidate = client.get_model_version(MODEL_NAME, str(args.version))

    if candidate.version == champion.version:
        raise ValueError("Candidate is already the champion.")

    champion_accuracy, champion_dataset, n = get_evaluation(
        client, champion
    )
    candidate_accuracy, candidate_dataset, candidate_n = get_evaluation(
        client, candidate
    )

    if candidate_dataset != champion_dataset or candidate_n != n:
        raise ValueError(
            "Candidate and champion must use the same evaluation dataset "
            "and sample size."
        )

    se = math.sqrt(champion_accuracy * (1 - champion_accuracy) / n)
    threshold = champion_accuracy + 2 * se
    promote = candidate_accuracy >= threshold

    decision = "champion" if promote else "challenger"

    client.set_registered_model_alias(
        MODEL_NAME, decision, candidate.version
    )

    for key, value in {
        "decision": decision,
        "candidate_accuracy": candidate_accuracy,
        "champion_accuracy": champion_accuracy,
        "promotion_threshold": threshold,
        "standard_error": se,
        "evaluation_n": n,
    }.items():
        client.set_model_version_tag(
            MODEL_NAME, candidate.version, key, str(value)
        )

    print(f"Previous champion: version {champion.version}")
    print(f"Candidate: version {candidate.version}")
    print(f"Champion accuracy: {champion_accuracy:.4f}")
    print(f"Candidate accuracy: {candidate_accuracy:.4f}")
    print(f"Standard error: {se:.4f}")
    print(f"Required accuracy: {threshold:.4f}")
    print(f"Decision: {decision}")


if __name__ == "__main__":
    main()
