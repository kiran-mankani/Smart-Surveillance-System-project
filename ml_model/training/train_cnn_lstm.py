# ============================================================
# File Name : train_cnn_lstm.py
# Project   : Smart Surveillance Analytics System
# Model     : CNN + LSTM
# ============================================================

import os
import json
import torch
import matplotlib.pyplot as plt

from torch.utils.data import DataLoader, random_split
from torch import nn
from torch.optim import AdamW
from torch.optim.lr_scheduler import ReduceLROnPlateau

from dataset import VideoDataset
from model import CNNLSTM
from engine import train_one_epoch, validate_one_epoch

from utils import (
    get_device,
    set_seed,
    create_directory,
    save_best_model,
    save_checkpoint,
    save_class_names
)


# ============================================================
# CONFIGURATION
# ============================================================
# ============================================================
# CONFIGURATION
# ============================================================

FRAMES_PATH = "../dataset/extracted_frames"

SAVE_PATH = "../saved_models"

BEST_MODEL_PATH = os.path.join(
    SAVE_PATH,
    "best_cnn_lstm.pth"
)

CHECKPOINT_PATH = os.path.join(
    SAVE_PATH,
    "checkpoint.pth"
)

BATCH_SIZE = 8

EPOCHS = 20

LEARNING_RATE = 0.0001

TRAIN_RATIO = 0.8

SEQUENCE_LENGTH = 20

SEED = 42


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    print("=" * 60)
    print("CNN + LSTM Training Started")
    print("=" * 60)


    # Seed
    set_seed(SEED)


    # Create folder
    create_directory(SAVE_PATH)


    # Device
    device = get_device()

    print("Using Device:", device)



    # ========================================================
    # GRAPH HISTORY LISTS
    # ========================================================

    train_losses = []
    val_losses = []

    train_accuracies = []
    val_accuracies = []




        # ============================================================
    # DATASET
    # ============================================================

    print("\nLoading Dataset...")

    dataset = VideoDataset(
        dataset_path=FRAMES_PATH,
        sequence_length=SEQUENCE_LENGTH
    )


    print("\nDataset Loaded Successfully")
    print("Total Videos :", len(dataset))
    print("Total Classes :", len(dataset.classes))


    # ============================================================
    # SAVE CLASS NAMES
    # ============================================================

    save_class_names(
        dataset.classes,
        os.path.join(
            SAVE_PATH,
            "class_names.json"
        )
    )


    # ============================================================
    # TRAIN / VALIDATION SPLIT
    # ============================================================

    train_size = int(TRAIN_RATIO * len(dataset))

    val_size = len(dataset) - train_size


    train_dataset, val_dataset = random_split(
        dataset,
        [train_size, val_size]
    )


    print("\nTraining Samples :", len(train_dataset))
    print("Validation Samples :", len(val_dataset))



    # ============================================================
    # DATALOADERS
    # ============================================================

    train_loader = DataLoader(
        train_dataset,
        batch_size=BATCH_SIZE,
        shuffle=True,
        num_workers=0
    )


    val_loader = DataLoader(
        val_dataset,
        batch_size=BATCH_SIZE,
        shuffle=False,
        num_workers=0
    )


    print("\nDataLoaders Created Successfully")






        # ============================================================
    # MODEL
    # ============================================================

    print("\nCreating CNN + LSTM Model...")


    model = CNNLSTM(
        num_classes=len(dataset.classes)
    )


    model = model.to(device)


    print("Model Ready")



    # ============================================================
    # LOSS FUNCTION
    # ============================================================

    criterion = nn.CrossEntropyLoss()



    # ============================================================
    # OPTIMIZER
    # ============================================================

    optimizer = AdamW(
        model.parameters(),
        lr=LEARNING_RATE
    )



    # ============================================================
    # CHECKPOINT
    # ============================================================

    # ============================================================
# LOAD CHECKPOINT
# ============================================================

start_epoch = 0
best_accuracy = 0.0

if os.path.exists(CHECKPOINT_PATH):

    print("\nLoading Checkpoint...")

    checkpoint = torch.load(
        CHECKPOINT_PATH,
        map_location=device
    )

    model.load_state_dict(
        checkpoint["model_state_dict"]
    )

    optimizer.load_state_dict(
        checkpoint["optimizer_state_dict"]
    )

    start_epoch = checkpoint["epoch"] + 1

    best_accuracy = checkpoint["best_accuracy"]

    print(f"Resuming from Epoch {start_epoch}")

else:

    print("\nNo Checkpoint Found. Starting Fresh Training")

    # ============================================================
    # LR SCHEDULER
    # ============================================================

    scheduler = ReduceLROnPlateau(
        optimizer,
        mode="max",
        patience=3
    )



    # ============================================================
    # MIXED PRECISION
    # ============================================================

    scaler = torch.amp.GradScaler(
        "cuda",
        enabled=(device.type == "cuda")
    )


    print("\nModel Setup Completed")







        # ============================================================
    # TRAINING LOOP
    # ============================================================

    print("\nStarting Training...")


    for epoch in range(start_epoch, EPOCHS):

        print("\n" + "=" * 60)
        print(
            f"Epoch [{epoch+1}/{EPOCHS}]"
        )
        print("=" * 60)



        # -----------------------------
        # Training
        # -----------------------------

        train_loss, train_acc = train_one_epoch(
    model,
    train_loader,
    optimizer,
    criterion,
    device,
    scaler
)



        # -----------------------------
        # Validation
        # -----------------------------

        val_loss, val_acc = validate_one_epoch(
            model,
            val_loader,
            criterion,
            device
        )



        # ====================================================
        # SAVE VALUES FOR GRAPHS
        # ====================================================

        train_losses.append(train_loss)

        val_losses.append(val_loss)

        train_accuracies.append(train_acc)

        val_accuracies.append(val_acc)



        print("\nTraining Loss :", train_loss)

        print("Training Accuracy :", train_acc)


        print("\nValidation Loss :", val_loss)

        print("Validation Accuracy :", val_acc)



        # ====================================================
        # LEARNING RATE UPDATE
        # ====================================================

        scheduler.step(val_acc)



               # ====================================================
        # SAVE BEST MODEL
        # ====================================================

        if val_acc > best_accuracy:

            best_accuracy = val_acc

            save_best_model(
                model,
                BEST_MODEL_PATH
            )

            print("\nBest Model Saved!")


        # ====================================================
        # SAVE CHECKPOINT
        # ====================================================

        save_checkpoint(
            model,
            optimizer,
            epoch,
            best_accuracy,
            CHECKPOINT_PATH
        )



        # ====================================================
        # SAVE CHECKPOINT
        # ====================================================




print("\nTraining Completed Successfully")







        # ============================================================
    # SAVE TRAINING HISTORY
    # ============================================================

history = {

        "train_loss": train_losses,

        "validation_loss": val_losses,

        "train_accuracy": train_accuracies,

        "validation_accuracy": val_accuracies

    }


history_path = os.path.join(
        SAVE_PATH,
        "training_history.json"
    )


with open(history_path, "w") as f:

        json.dump(
            history,
            f,
            indent=4
        )


print("\nTraining History Saved")



    # ============================================================
    # LOSS GRAPH
    # ============================================================

plt.figure(figsize=(8,5))


plt.plot(
        train_losses,
        label="Training Loss"
    )


plt.plot(
        val_losses,
        label="Validation Loss"
    )


plt.xlabel("Epoch")

plt.ylabel("Loss")

plt.title(
        "Training and Validation Loss"
    )


plt.legend()


loss_path = os.path.join(
        SAVE_PATH,
        "loss_curve.png"
    )


plt.savefig(loss_path)

plt.close()



    # ============================================================
    # ACCURACY GRAPH
    # ============================================================

plt.figure(figsize=(8,5))


plt.plot(
        train_accuracies,
        label="Training Accuracy"
    )


plt.plot(
        val_accuracies,
        label="Validation Accuracy"
    )


plt.xlabel("Epoch")

plt.ylabel("Accuracy")


plt.title(
        "Training and Validation Accuracy"
    )


plt.legend()


accuracy_path = os.path.join(
        SAVE_PATH,
        "accuracy_curve.png"
    )


plt.savefig(accuracy_path)

plt.close()



print("\nGraphs Saved Successfully")
print("Loss Graph :", loss_path)

print("Accuracy Graph :", accuracy_path)