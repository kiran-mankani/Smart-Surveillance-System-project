# ============================================================
# File Name : engine.py
# Project   : Smart Surveillance Analytics System
# Model     : CNN + LSTM
#
# Purpose:
#   Training and Validation Engine
# ============================================================

import torch
from tqdm import tqdm

from utils import calculate_accuracy


# ============================================================
# TRAIN ONE EPOCH
# ============================================================

def train_one_epoch(
    model,
    dataloader,
    optimizer,
    criterion,
    device,
    scaler
):
    """
    Train model for one epoch.
    """

    # Training mode ON
    model.train()

    running_loss = 0.0
    running_accuracy = 0.0

    progress_bar = tqdm(
        dataloader,
        desc="Training",
        leave=False
    )

    for frames, labels in progress_bar:

        # Move tensors to GPU / CPU
        frames = frames.to(device)
        labels = labels.to(device)

        # Clear previous gradients
        optimizer.zero_grad()

        # Mixed Precision
        with torch.amp.autocast(
            device_type=device.type,
            enabled=(device.type == "cuda")
        ):

            outputs = model(frames)

            loss = criterion(outputs, labels)

        # Backpropagation
        scaler.scale(loss).backward()

        # Update Weights
        scaler.step(optimizer)

        scaler.update()

        # Accuracy
        accuracy = calculate_accuracy(outputs, labels)

        running_loss += loss.item()

        running_accuracy += accuracy

        progress_bar.set_postfix(
            loss=f"{loss.item():.4f}",
            acc=f"{accuracy:.4f}"
        )

    epoch_loss = running_loss / len(dataloader)

    epoch_accuracy = running_accuracy / len(dataloader)

    return epoch_loss, epoch_accuracy


# ============================================================
# VALIDATION
# ============================================================

def validate_one_epoch(
    model,
    dataloader,
    criterion,
    device
):
    """
    Validate model.
    """

    model.eval()

    running_loss = 0.0
    running_accuracy = 0.0

    progress_bar = tqdm(
        dataloader,
        desc="Validation",
        leave=False
    )

    with torch.no_grad():

        for frames, labels in progress_bar:

            frames = frames.to(device)
            labels = labels.to(device)

            with torch.amp.autocast(
                device_type=device.type,
                enabled=(device.type == "cuda")
            ):

                outputs = model(frames)

                loss = criterion(outputs, labels)

            accuracy = calculate_accuracy(
                outputs,
                labels
            )

            running_loss += loss.item()

            running_accuracy += accuracy

            progress_bar.set_postfix(
                loss=f"{loss.item():.4f}",
                acc=f"{accuracy:.4f}"
            )

    epoch_loss = running_loss / len(dataloader)

    epoch_accuracy = running_accuracy / len(dataloader)

    return epoch_loss, epoch_accuracy