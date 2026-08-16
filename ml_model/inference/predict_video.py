# ============================================================
# File Name : predict_video.py
# Project   : Smart Surveillance Analytics System
# Model     : CNN + LSTM
#
# Purpose:
# Predict activity from a new video using trained CNN + LSTM.
#
# Flow:
# Video
#   ↓
# Extract 20 Frames
#   ↓
# Resize + Normalize
#   ↓
# CNN
#   ↓
# LSTM
#   ↓
# Predicted Action
# ============================================================

# ============================================================
# IMPORT LIBRARIES
# ============================================================

import os
import json
import cv2
import torch
import numpy as np

from PIL import Image
from torchvision import transforms

# Import trained model
import sys
from pathlib import Path

# Project root ko Python path me add karo
ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT / "training"))

from model import CNNLSTM


# ============================================================
# CONFIGURATION
# ============================================================

# Best trained model
MODEL_PATH = ROOT / "saved_models" / "best_cnn_lstm.pth"

CLASS_PATH = ROOT / "saved_models" / "class_names.json"
# Frames per video
SEQUENCE_LENGTH = 20

# Image size
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

    transforms.Resize((224,224)),

    transforms.ToTensor(),

    transforms.Normalize(

        mean=[0.485,0.456,0.406],

        std=[0.229,0.224,0.225]

    )

])


# ============================================================
# LOAD CLASS NAMES
# ============================================================

with open(CLASS_PATH,"r") as file:

    class_names = json.load(file)


print("\nTotal Classes :",len(class_names))


# ============================================================
# CREATE MODEL
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

model.to(device)

model.eval()


print("\nModel Loaded Successfully")





# ============================================================
# EXTRACT FRAMES FROM VIDEO
# ============================================================

def extract_frames(video_path):

    cap = cv2.VideoCapture(video_path)

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    if total_frames == 0:
        raise ValueError("Video has no frames.")

    frame_indices = np.linspace(
        0,
        total_frames - 1,
        SEQUENCE_LENGTH,
        dtype=int
    )

    frames = []

    current_frame = 0
    selected = 0

    while cap.isOpened():

        ret, frame = cap.read()

        if not ret:
            break

        if selected < len(frame_indices) and current_frame == frame_indices[selected]:

            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            image = Image.fromarray(frame)

            image = transform(image)

            frames.append(image)

            selected += 1

        current_frame += 1

    cap.release()

    if len(frames) < SEQUENCE_LENGTH:

        while len(frames) < SEQUENCE_LENGTH:
            frames.append(frames[-1])

    frames = torch.stack(frames)

    return frames.unsqueeze(0)




# ============================================================
# PREDICT VIDEO
# ============================================================

# ============================================================
# PREDICT VIDEO
# ============================================================

def predict(video_path):

    frames = extract_frames(video_path)

    frames = frames.to(device)

    with torch.no_grad():

        outputs = model(frames)

        probabilities = torch.softmax(outputs, dim=1)

        confidence, predicted = torch.max(probabilities, dim=1)

    class_name = class_names[predicted.item()]

    confidence = confidence.item() * 100

    print("\n===================================")
    print("Prediction Result")
    print("===================================")
    print("Video :", os.path.basename(video_path))
    print("Predicted Class :", class_name)
    print(f"Confidence : {confidence:.2f}%")

    return class_name, confidence

    # ============================================================
# MAIN
# ============================================================

# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    video_path = input("\nEnter Video Path : ").strip()

    if not os.path.exists(video_path):

        print("\nVideo not found.")

    else:

        predict(video_path)