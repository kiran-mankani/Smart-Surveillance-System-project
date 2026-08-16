import os
import json
import random
import numpy as np
import torch


# ============================================================
# Create folder if it does not exist
# ============================================================

def create_directory(path):
    os.makedirs(path, exist_ok=True)


# ============================================================
# Set Random Seed
# ============================================================

def set_seed(seed=42):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)


# ============================================================
# Calculate Accuracy
# ============================================================

def calculate_accuracy(outputs, labels):
    _, predictions = torch.max(outputs, dim=1)
    correct = (predictions == labels).sum().item()
    return correct / labels.size(0)


# ============================================================
# Save Best Model
# ============================================================

def save_best_model(model, path):

    folder = os.path.dirname(path)
    if folder != "":
        os.makedirs(folder, exist_ok=True)

    torch.save(model.state_dict(), path)

    print(f"\nBest model saved:\n{path}")


# ============================================================
# Save Checkpoint
# ============================================================

def save_checkpoint(
    model,
    optimizer,
    epoch,
    best_accuracy,
    path
):

    folder = os.path.dirname(path)
    if folder != "":
        os.makedirs(folder, exist_ok=True)

    checkpoint = {
        "epoch": epoch,
        "model_state_dict": model.state_dict(),
        "optimizer_state_dict": optimizer.state_dict(),
        "best_accuracy": best_accuracy
    }

    print("\nSaving checkpoint...")

    torch.save(checkpoint, path)

    print(f"\nCheckpoint saved:\n{path}")


# ============================================================
# Load Checkpoint
# ============================================================

def load_checkpoint(path, model, optimizer=None):

    checkpoint = torch.load(path)

    model.load_state_dict(checkpoint["model_state_dict"])

    if optimizer is not None:
        optimizer.load_state_dict(checkpoint["optimizer_state_dict"])

    print("\nCheckpoint Loaded Successfully")

    return checkpoint


# ============================================================
# Save Class Names
# ============================================================

def save_class_names(class_names, path):

    folder = os.path.dirname(path)
    if folder != "":
        os.makedirs(folder, exist_ok=True)

    with open(path, "w") as file:
        json.dump(class_names, file, indent=4)

    print("\nClass names saved.")


# ============================================================
# Device
# ============================================================

def get_device():

    if torch.cuda.is_available():
        device = torch.device("cuda")
    else:
        device = torch.device("cpu")

    print(f"\nUsing Device : {device}")

    return device