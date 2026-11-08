import argparse
import hashlib
import sys
from pathlib import Path

from PIL import Image

from data import CLASSES

SPLITS = ("training", "validation", "evaluation")
EXTENSIONS = {".jpg", ".jpeg", ".png"}


def validate_dataset(root: Path, min_per_class: int, tau: float) -> bool:
    checks = {
        "Class folders": True,
        "Image format and dimensions": True,
        "Minimum images per class": True,
        "No duplicates across splits": True,
        "Training/validation balance": True,
    }

    counts = {}
    seen_hashes = {}

    for split in SPLITS:
        split_dir = root / split
        counts[split] = {}

        if not split_dir.is_dir():
            checks["Class folders"] = False
            checks["Minimum images per class"] = False
            continue

        folders = {p.name for p in split_dir.iterdir() if p.is_dir()}

        if folders != set(CLASSES):
            checks["Class folders"] = False

        for category in CLASSES:
            category_dir = split_dir / category

            if not category_dir.is_dir():
                counts[split][category] = 0
                checks["Minimum images per class"] = False
                continue

            images = sorted(
                p for p in category_dir.iterdir()
                if p.is_file() and p.suffix.lower() in EXTENSIONS
            )

            counts[split][category] = len(images)

            if len(images) < min_per_class:
                checks["Minimum images per class"] = False

            for path in images:
                try:
                    with Image.open(path) as image:
                        image.load()
                        if image.mode != "RGB" or image.size != (128, 128):
                            checks["Image format and dimensions"] = False

                    digest = hashlib.md5(path.read_bytes()).hexdigest()
                    previous_splits = seen_hashes.setdefault(digest, set())

                    if previous_splits and split not in previous_splits:
                        checks["No duplicates across splits"] = False

                    previous_splits.add(split)

                except (OSError, ValueError):
                    checks["Image format and dimensions"] = False

    train = counts["training"]
    validation = counts["validation"]

    train_total = sum(train.values())
    validation_total = sum(validation.values())

    if train_total == 0 or validation_total == 0:
        checks["Training/validation balance"] = False
    else:
        for category in CLASSES:
            train_share = train.get(category, 0) / train_total
            validation_share = validation.get(category, 0) / validation_total

            if abs(train_share - validation_share) > tau:
                checks["Training/validation balance"] = False

    for name, passed in checks.items():
        status = "PASS" if passed else "FAIL"
        print(f"{status} - {name}")

    print(f"Minimum images per class: {min_per_class}")
    print(f"Class balance tolerance: {tau}")

    return all(checks.values())


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("dataset", type=Path)
    parser.add_argument("--min-per-class", type=int, default=50)
    parser.add_argument("--tau", type=float, default=0.05)

    args = parser.parse_args()

    if not validate_dataset(args.dataset, args.min_per_class, args.tau):
        sys.exit(1)


if __name__ == "__main__":
    main()
