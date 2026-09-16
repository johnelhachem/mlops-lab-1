import argparse
import os

import mlflow
import mlflow.pytorch
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from torchvision import datasets, models, transforms


def get_dataset_root(dataset_name):
    if dataset_name == "mini":
        return "data/food11_processed_mini"

    if dataset_name == "processed":
        return "data/food11_processed"

    raise ValueError(
        "Dataset must be 'mini' or 'processed'"
    )


def evaluate(model, loader, criterion, device):
    model.eval()

    total_loss = 0.0
    correct = 0
    total = 0

    with torch.no_grad():
        for images, labels in loader:
            images = images.to(device)
            labels = labels.to(device)

            outputs = model(images)
            loss = criterion(outputs, labels)

            total_loss += loss.item() * images.size(0)

            predictions = outputs.argmax(dim=1)
            correct += (predictions == labels).sum().item()
            total += labels.size(0)

    average_loss = total_loss / len(loader.dataset)
    accuracy = correct / total

    return average_loss, accuracy


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--dataset",
        choices=["mini", "processed"],
        required=True,
    )

    parser.add_argument(
        "--epochs",
        type=int,
        required=True,
    )

    parser.add_argument(
        "--lr",
        type=float,
        required=True,
    )

    parser.add_argument(
        "--batch-size",
        type=int,
        required=True,
    )

    args = parser.parse_args()

    dataset_root = get_dataset_root(args.dataset)

    training_path = os.path.join(
        dataset_root,
        "training",
    )

    validation_path = os.path.join(
        dataset_root,
        "validation",
    )

    evaluation_path = os.path.join(
        dataset_root,
        "evaluation",
    )

    device = torch.device(
        "cuda" if torch.cuda.is_available() else "cpu"
    )

    print(f"Using device: {device}")
    print(f"Dataset: {dataset_root}")

    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
    ])

    training_dataset = datasets.ImageFolder(
        training_path,
        transform=transform,
    )

    validation_dataset = datasets.ImageFolder(
        validation_path,
        transform=transform,
    )

    evaluation_dataset = datasets.ImageFolder(
        evaluation_path,
        transform=transform,
    )

    num_classes = len(training_dataset.classes)

    print(f"Classes: {num_classes}")
    print(f"Training samples: {len(training_dataset)}")
    print(f"Validation samples: {len(validation_dataset)}")
    print(f"Evaluation samples: {len(evaluation_dataset)}")

    training_loader = DataLoader(
        training_dataset,
        batch_size=args.batch_size,
        shuffle=True,
    )

    validation_loader = DataLoader(
        validation_dataset,
        batch_size=args.batch_size,
        shuffle=False,
    )

    evaluation_loader = DataLoader(
        evaluation_dataset,
        batch_size=args.batch_size,
        shuffle=False,
    )

    model = models.resnet18(
        weights=models.ResNet18_Weights.DEFAULT
    )

    model.fc = nn.Linear(
        model.fc.in_features,
        num_classes,
    )

    model = model.to(device)

    criterion = nn.CrossEntropyLoss()

    optimizer = optim.Adam(
        model.parameters(),
        lr=args.lr,
    )

    mlflow.set_tracking_uri(
        "http://127.0.0.1:5000"
    )

    mlflow.set_experiment("food11")

    with mlflow.start_run():

        mlflow.log_params({
            "dataset": args.dataset,
            "epochs": args.epochs,
            "lr": args.lr,
            "batch_size": args.batch_size,
            "model": "resnet18",
            "num_classes": num_classes,
        })

        for epoch in range(args.epochs):

            model.train()

            running_loss = 0.0

            for images, labels in training_loader:

                images = images.to(device)
                labels = labels.to(device)

                optimizer.zero_grad()

                outputs = model(images)

                loss = criterion(
                    outputs,
                    labels,
                )

                loss.backward()
                optimizer.step()

                running_loss += (
                    loss.item() * images.size(0)
                )

            train_loss = (
                running_loss
                / len(training_loader.dataset)
            )

            val_loss, val_accuracy = evaluate(
                model,
                validation_loader,
                criterion,
                device,
            )

            print(
                f"Epoch {epoch + 1}/{args.epochs} | "
                f"train_loss={train_loss:.4f} | "
                f"val_loss={val_loss:.4f} | "
                f"val_accuracy={val_accuracy:.4f}"
            )

            mlflow.log_metric(
                "train_loss",
                train_loss,
                step=epoch,
            )

            mlflow.log_metric(
                "val_loss",
                val_loss,
                step=epoch,
            )

            mlflow.log_metric(
                "val_accuracy",
                val_accuracy,
                step=epoch,
            )

        test_loss, test_accuracy = evaluate(
            model,
            evaluation_loader,
            criterion,
            device,
        )

        mlflow.log_metric(
            "test_loss",
            test_loss,
        )

        mlflow.log_metric(
            "test_accuracy",
            test_accuracy,
        )

        mlflow.pytorch.log_model(
            model,
            "model",
            serialization_format="pickle",
        )

        print(f"Final test loss: {test_loss:.4f}")
        print(f"Final test accuracy: {test_accuracy:.4f}")


if __name__ == "__main__":
    main()