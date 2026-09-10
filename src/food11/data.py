from pathlib import Path
from PIL import Image


CLASSES = [
    "Bread",
    "Dairy product",
    "Dessert",
    "Egg",
    "Fried food",
    "Meat",
    "Noodles-Pasta",
    "Rice",
    "Seafood",
    "Soup",
    "Vegetable-Fruit",
]

SPLITS = ["training", "evaluation", "validation"]

BASE_DIR = Path(__file__).resolve().parents[2]
RAW_DIR = BASE_DIR / "data" / "food11_raw"
PROCESSED_DIR = BASE_DIR / "data" / "food11_processed"
MINI_DIR = BASE_DIR / "data" / "food11_processed_mini"

MAX_MINI_IMAGES = 100


def get_class_from_filename(filename: str) -> str:
    """Extract the Food11 class from the filename."""
    class_index = int(filename.split("_")[0])
    return CLASSES[class_index]


def process_split(split: str) -> None:
    raw_split = RAW_DIR / split
    processed_split = PROCESSED_DIR / split
    mini_split = MINI_DIR / split

    class_counts = {class_name: 0 for class_name in CLASSES}

    for image_path in raw_split.iterdir():
        if not image_path.is_file():
            continue

        if image_path.suffix.lower() not in {".jpg", ".jpeg", ".png"}:
            continue

        class_name = get_class_from_filename(image_path.name)

        processed_class_dir = processed_split / class_name
        mini_class_dir = mini_split / class_name

        processed_class_dir.mkdir(parents=True, exist_ok=True)
        mini_class_dir.mkdir(parents=True, exist_ok=True)

        output_name = image_path.stem + ".jpg"

        # Create 128x128 processed image.
        output_path = processed_class_dir / output_name

        with Image.open(image_path) as image:
            image = image.convert("RGB")
            image = image.resize((128, 128))
            image.save(output_path, "JPEG", quality=95)

            # Copy at most 100 images per class to the mini dataset.
            if class_counts[class_name] < MAX_MINI_IMAGES:
                mini_output_path = mini_class_dir / output_name
                image.save(mini_output_path, "JPEG", quality=95)
                class_counts[class_name] += 1

    print(f"Processed {split}:")
    for class_name, count in class_counts.items():
        print(f"  {class_name}: {count} mini images")


def main() -> None:
    if not RAW_DIR.exists():
        raise FileNotFoundError(f"Raw dataset not found: {RAW_DIR}")

    for split in SPLITS:
        process_split(split)

    print("\nProcessing complete.")


if __name__ == "__main__":
    main()