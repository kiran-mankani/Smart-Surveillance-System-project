# ============================================================
# File Name : evaluate.py
# Project   : Smart Surveillance Analytics System
# Model     : CNN + LSTM
# ============================================================

import os
import json
import torch
import numpy as np
import matplotlib.pyplot as plt

from tqdm import tqdm
from torch.utils.data import DataLoader, random_split
from torchvision import transforms
from sklearn.metrics import (
    confusion_matrix,
    classification_report,
    roc_curve,
    auc
)
from sklearn.preprocessing import label_binarize

from dataset import VideoDataset
from model import CNNLSTM
from utils import get_device, set_seed

# ============================================================
# CONFIGURATION
# ============================================================

FRAMES_PATH = "../dataset/extracted_frames"

MODEL_PATH = "../saved_models/best_cnn_lstm.pth"

CLASS_PATH = "../saved_models/class_names.json"

SAVE_PATH = "../saved_models"

BATCH_SIZE = 8

SEQUENCE_LENGTH = 20

TRAIN_RATIO = 0.8

SEED = 42

# ============================================================
# IMAGE TRANSFORM
# ============================================================

transform = transforms.Compose([
    transforms.Resize((224,224)),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485,0.456,0.406],
        std=[0.229,0.224,0.225]
    )
])

# ============================================================
# DEVICE
# ============================================================

set_seed(SEED)

device = get_device()

# ============================================================
# LOAD CLASS NAMES
# ============================================================

with open(CLASS_PATH,"r") as file:
    class_names = json.load(file)

print("\nTotal Classes :",len(class_names))

# ============================================================
# LOAD DATASET
# ============================================================

print("\nLoading Dataset...")

dataset = VideoDataset(
    dataset_path=FRAMES_PATH,
    sequence_length=SEQUENCE_LENGTH,
    transform=transform
)

print("Total Videos :",len(dataset))

train_size = int(TRAIN_RATIO * len(dataset))
test_size = len(dataset) - train_size

_, test_dataset = random_split(
    dataset,
    [train_size,test_size]
)

test_loader = DataLoader(
    test_dataset,
    batch_size=BATCH_SIZE,
    shuffle=False,
    num_workers=0
)

print("Testing Samples :",len(test_dataset))

# ============================================================
# LOAD MODEL
# ============================================================

print("\nLoading Model...")

model = CNNLSTM(
    num_classes=len(class_names)
)

model.load_state_dict(
    torch.load(
        MODEL_PATH,
        map_location=device
    )
)

model = model.to(device)

model.eval()

print("Model Loaded Successfully")







# ============================================================
# EVALUATION
# ============================================================

all_predictions = []
all_labels = []
all_probabilities = []

correct = 0
total = 0

print("\nStarting Evaluation...")

with torch.no_grad():

    for frames, labels in tqdm(test_loader, desc="Evaluating"):

        frames = frames.to(device)
        labels = labels.to(device)

        outputs = model(frames)

        probabilities = torch.softmax(outputs, dim=1)

        _, predictions = torch.max(outputs, 1)

        correct += (predictions == labels).sum().item()
        total += labels.size(0)

        all_predictions.extend(
            predictions.cpu().numpy()
        )

        all_labels.extend(
            labels.cpu().numpy()
        )

        all_probabilities.extend(
            probabilities.cpu().numpy()
        )

accuracy = 100 * correct / total

print("\n" + "=" * 60)
print("Evaluation Completed")
print("=" * 60)

print(f"Accuracy : {accuracy:.2f}%")

# ============================================================
# CLASSIFICATION REPORT
# ============================================================

report = classification_report(
    all_labels,
    all_predictions,
    target_names=class_names,
    digits=4
)

print("\nClassification Report\n")
print(report)

with open(
    os.path.join(
        SAVE_PATH,
        "classification_report.txt"
    ),
    "w"
) as file:

    file.write(report)

print("\nclassification_report.txt saved.")

# ============================================================
# CONFUSION MATRIX
# ============================================================

cm = confusion_matrix(
    all_labels,
    all_predictions
)

plt.figure(figsize=(20,20))

plt.imshow(
    cm,
    interpolation="nearest",
    cmap="Blues"
)

plt.title("Confusion Matrix")
plt.colorbar()

plt.xlabel("Predicted Label")
plt.ylabel("True Label")

plt.tight_layout()

plt.savefig(
    os.path.join(
        SAVE_PATH,
        "confusion_matrix.png"
    ),
    dpi=300
)

plt.close()

print("confusion_matrix.png saved.")









# ============================================================
# ROC CURVE
# ============================================================

print("\nGenerating ROC Curve...")

all_labels_bin = label_binarize(
    all_labels,
    classes=np.arange(len(class_names))
)

all_probabilities = np.array(all_probabilities)

plt.figure(figsize=(10,8))

for i in range(len(class_names)):

    fpr, tpr, _ = roc_curve(
        all_labels_bin[:, i],
        all_probabilities[:, i]
    )

    roc_auc = auc(fpr, tpr)

    plt.plot(
        fpr,
        tpr,
        lw=1,
        label=f"{class_names[i]} (AUC={roc_auc:.2f})"
    )

plt.plot(
    [0,1],
    [0,1],
    linestyle="--",
    color="black"
)

plt.xlabel("False Positive Rate")
plt.ylabel("True Positive Rate")
plt.title("ROC Curve")
plt.legend(
    loc="lower right",
    fontsize=5,
    ncol=2
)

plt.tight_layout()

plt.savefig(
    os.path.join(
        SAVE_PATH,
        "roc_curve.png"
    ),
    dpi=300
)

plt.close()

print("roc_curve.png saved.")

# ============================================================
# SAVE CONFUSION MATRIX VALUES
# ============================================================

np.savetxt(
    os.path.join(
        SAVE_PATH,
        "confusion_matrix.csv"
    ),
    cm,
    delimiter=",",
    fmt="%d"
)

print("confusion_matrix.csv saved.")

# ============================================================
# FINAL SUMMARY
# ============================================================

print("\n" + "="*60)
print("Evaluation Completed Successfully")
print("="*60)

print(f"Accuracy : {accuracy:.2f}%")
print(f"Total Test Samples : {total}")

print("\nFiles Saved:")

print(os.path.join(SAVE_PATH, "classification_report.txt"))
print(os.path.join(SAVE_PATH, "confusion_matrix.png"))
print(os.path.join(SAVE_PATH, "confusion_matrix.csv"))
print(os.path.join(SAVE_PATH, "roc_curve.png"))