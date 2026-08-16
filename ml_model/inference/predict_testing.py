# ============================================================
# File Name : predict_testing.py
# Project   : Smart Surveillance Analytics System
# Purpose   :
# Predict all testing videos listed in testing_labels.csv
# and update predicted_label automatically.
# ============================================================

# ============================================================
# IMPORTS
# ============================================================

import os
import json
import cv2
import torch
import pandas as pd
import numpy as np

from pathlib import Path
from PIL import Image

from torchvision import transforms

import sys

# ============================================================
# PROJECT PATHS
# ============================================================

ROOT = Path(__file__).resolve().parents[1]

sys.path.append(str(ROOT / "training"))

from model import CNNLSTM

# ============================================================
# ============================================================
# CONFIGURATION
# ============================================================

MODEL_PATH = ROOT / "saved_models" / "best_cnn_lstm.pth"

CLASS_PATH = ROOT / "saved_models" / "class_names.json"

TEST_FOLDER = Path(
    r"D:\Project\Dataset Videos\New folder\UCF101\Testing Videos"
)

CSV_PATH = TEST_FOLDER / "testing_labels.csv"

SEQUENCE_LENGTH = 20
IMAGE_SIZE = 224

# ============================================================
# DEVICE
# ============================================================

device = torch.device(
    "cuda" if torch.cuda.is_available() else "cpu"
)

print(f"\nUsing Device : {device}")

# ============================================================
# IMAGE TRANSFORM
# ============================================================

transform = transforms.Compose([
    transforms.Resize((IMAGE_SIZE, IMAGE_SIZE)),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    )
])

# ============================================================
# LOAD CLASS NAMES
# ============================================================

with open(CLASS_PATH, "r") as file:
    class_names = json.load(file)

print(f"Total Classes : {len(class_names)}")

# ============================================================
# LOAD MODEL
# ============================================================

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
# READ VIDEO
# ============================================================

def load_video(video_path):

    cap = cv2.VideoCapture(str(video_path))

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    if total_frames == 0:
        cap.release()
        return None

    indices = np.linspace(
        0,
        total_frames - 1,
        SEQUENCE_LENGTH,
        dtype=int
    )

    frames = []

    current = 0
    index_pointer = 0

    while cap.isOpened():

        ret, frame = cap.read()

        if not ret:
            break

        if index_pointer < len(indices) and current == indices[index_pointer]:

            frame = cv2.cvtColor(
                frame,
                cv2.COLOR_BGR2RGB
            )

            frame = Image.fromarray(frame)

            frame = transform(frame)

            frames.append(frame)

            index_pointer += 1

        current += 1

    cap.release()

    # Agar frames kam milen to last frame repeat karo
    while len(frames) < SEQUENCE_LENGTH:

        if len(frames) == 0:
            return None

        frames.append(frames[-1])

    frames = torch.stack(frames)

    frames = frames.unsqueeze(0)

    return frames


# ============================================================
# PREDICT SINGLE VIDEO
# ============================================================

def predict_video(video_path):

    frames = load_video(video_path)

    if frames is None:
        return None, 0

    frames = frames.to(device)

    with torch.no_grad():

        outputs = model(frames)

        probabilities = torch.softmax(
            outputs,
            dim=1
        )

        confidence, prediction = torch.max(
            probabilities,
            dim=1
        )

    predicted_class = class_names[
        prediction.item()
    ]

    confidence = confidence.item() * 100

    return predicted_class, confidence






# ============================================================
# READ CSV
# ============================================================

print("\nLoading CSV...")

df = pd.read_csv(CSV_PATH)

df.columns = df.columns.str.strip()

print("CSV Columns :", df.columns.tolist())

if "Predicted_label" not in df.columns:
    df["Predicted_label"] = ""

if "confidence" not in df.columns:
    df["confidence"] = ""

df["Predicted_label"] = df["Predicted_label"].fillna("").astype(str)
df["confidence"] = df["confidence"].fillna("").astype(str)

print(f"Total Testing Videos : {len(df)}")



# ============================================================
# START PREDICTION

# ============================================================



# ============================================================
# START PREDICTION
# ============================================================

for index, row in df.iterrows():

    video_name = str(row["video_name"]).strip()
    actual_label = str(row["actual_label"]).strip()

    if not video_name.lower().endswith((".avi", ".mp4")):
        video_name += ".avi"

    video_path = TEST_FOLDER / actual_label / video_name

    print("\n-------------------------")
    print("Video Name  :", video_name)
    print("Actual Label:", actual_label)
    print("Video Path  :", video_path)
    print("Exists      :", video_path.exists())

    if not video_path.exists():
        print(f"Video Not Found : {video_path}")
        continue

    print(f"\nProcessing : {video_name}")

    predicted_label, confidence = predict_video(video_path)

    if predicted_label is None:
        print("Prediction Failed")
        continue

    df.at[index, "Predicted_label"] = str(predicted_label)
    df.at[index, "confidence"] = f"{confidence:.2f}"

    print(f"Actual    : {actual_label}")
    print(f"Predicted : {predicted_label}")
    print(f"Confidence: {confidence:.2f}%")


    # ============================================================
# SAVE UPDATED CSV
# ============================================================

OUTPUT_CSV = TEST_FOLDER / "testing_predictions.csv"

df.to_csv(OUTPUT_CSV, index=False)

print("\nUpdated CSV Saved Successfully!")

# ============================================================
# CALCULATE ACCURACY
# ============================================================

# Make sure predicted column is string
df["Predicted_label"] = df["Predicted_label"].fillna("").astype(str)
df["actual_label"] = df["actual_label"].astype(str)

correct = (df["actual_label"] == df["Predicted_label"]).sum()
total = len(df)

accuracy = (correct / total) * 100 if total > 0 else 0

# ============================================================
# FINAL RESULTS
# ============================================================

print("\n" + "=" * 60)
print("TESTING COMPLETED")
print("=" * 60)
print(f"Total Videos       : {total}")
print(f"Correct Prediction : {correct}")
print(f"Accuracy           : {accuracy:.2f}%")
print("\nPrediction File Saved At:")
print(OUTPUT_CSV)
print("=" * 60)