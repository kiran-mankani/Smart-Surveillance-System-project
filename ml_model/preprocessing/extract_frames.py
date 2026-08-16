# ============================================================
# File Name : extract_frames.py
# Project   : Smart Surveillance Analytics System
# Purpose   : Extract frames from all UCF101 videos
# Author    : Kiran (FYP)
# ============================================================

# ============================================================
# STEP 1 - Import Required Libraries
# ============================================================

import cv2                      # OpenCV -> Read videos and save frames
from pathlib import Path        # Handle folders and file paths
from tqdm import tqdm           # Show progress bar


# ============================================================
# STEP 2 - Dataset Path
# Change this path only if your dataset location changes.
# ============================================================

DATASET_PATH = Path(
    r"D:\Project\Dataset Videos\New folder\UCF101\UCF-101"
)

# ============================================================
# STEP 3 - Output Folder
# Extracted frames will be stored here.
# ============================================================

OUTPUT_PATH = Path(
    r"D:\Project\Smart-Surveillance-System\ml_model\dataset\extracted_frames"
)

# Create folder if it does not exist
OUTPUT_PATH.mkdir(parents=True, exist_ok=True)

# ============================================================
# STEP 4 - Configuration
# ============================================================

FRAME_SIZE = (224, 224)     # Image size for CNN
FRAMES_PER_VIDEO = 20        # Number of frames extracted per video


# ============================================================
# STEP 5 - Frame Extraction Function
# ============================================================

def extract_frames(video_path, output_folder):
    """
    Extract fixed number of frames from one video.

    Parameters
    ----------
    video_path : Path
        Path of video file

    output_folder : Path
        Folder where frames will be saved
    """

    # Open video
    cap = cv2.VideoCapture(str(video_path))

    # If video cannot be opened
    if not cap.isOpened():
        print(f"Cannot open: {video_path}")
        return

    # Total frames inside video
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    # Skip empty videos
    if total_frames == 0:
        cap.release()
        return

    # Calculate interval
    interval = max(total_frames // FRAMES_PER_VIDEO, 1)

    frame_index = 0
    saved_count = 0

    while True:

        success, frame = cap.read()

        if not success:
            break

        # Save one frame after every interval
        if frame_index % interval == 0:

            # Resize frame
            frame = cv2.resize(frame, FRAME_SIZE)

            # Create frame filename
            frame_name = output_folder / f"frame_{saved_count:03d}.jpg"

            # Save image
            cv2.imwrite(str(frame_name), frame)

            saved_count += 1

            # Stop after required number of frames
            if saved_count >= FRAMES_PER_VIDEO:
                break

        frame_index += 1

    cap.release()


# ============================================================
# STEP 6 - Process Complete Dataset
# ============================================================

def process_dataset():

    print("=" * 60)
    print("Frame Extraction Started...")
    print("=" * 60)

    # Read every action folder
    class_folders = sorted(DATASET_PATH.iterdir())

    for class_folder in tqdm(class_folders, desc="Processing Classes"):

        if not class_folder.is_dir():
            continue

        class_name = class_folder.name

        # Create output class folder
        class_output = OUTPUT_PATH / class_name
        class_output.mkdir(parents=True, exist_ok=True)

        # Read all AVI videos
        videos = list(class_folder.glob("*.avi"))

        for video in videos:

            video_name = video.stem

            # Create folder for one video's frames
            video_output = class_output / video_name
            video_output.mkdir(parents=True, exist_ok=True)

            extract_frames(video, video_output)

    print("\nFrame Extraction Completed Successfully.")
    print(f"\nFrames saved inside:\n{OUTPUT_PATH}")


# ============================================================
# STEP 7 - Main Function
# ============================================================

if __name__ == "__main__":

    process_dataset()