# ============================================================
# File Name : dataset.py
# Project   : Smart Surveillance Analytics System
# Model     : CNN + LSTM
#
# Purpose:
#   Extracted video frames ko load karna aur CNN + LSTM
#   ke liye sequence banana.
# ============================================================


# ============================================================
# IMPORTS
# ============================================================

from pathlib import Path

import torch

from torch.utils.data import Dataset

from torchvision import transforms

from PIL import Image



# ============================================================
# DATASET CLASS
# ============================================================


class VideoDataset(Dataset):


    def __init__(self,
                 dataset_path,
                 sequence_length=20,
                 transform=None):


        # Dataset path

        self.dataset_path = Path(dataset_path)


        # Frames per video

        self.sequence_length = sequence_length



        # ====================================================
        # IMAGE TRANSFORM
        # ====================================================

        if transform is None:


            self.transform = transforms.Compose([

                # CNN input size

                transforms.Resize(
                    (224,224)
                ),


                # Convert PIL image to Tensor

                transforms.ToTensor(),



                # ImageNet normalization
                # ResNet18 CNN ke liye

                transforms.Normalize(

                    mean=[
                        0.485,
                        0.456,
                        0.406
                    ],

                    std=[
                        0.229,
                        0.224,
                        0.225
                    ]

                )

            ])


        else:

            self.transform = transform




        # ====================================================
        # CLASSES
        # ====================================================


        self.classes = sorted(

            [

                folder.name

                for folder in self.dataset_path.iterdir()

                if folder.is_dir()

            ]

        )



        # Class to number mapping


        self.class_to_idx = {


            class_name:index

            for index, class_name

            in enumerate(self.classes)

        }



        # Store videos

        self.samples = []



        # Load dataset

        self.load_dataset()





    # ========================================================
    # SCAN DATASET
    # ========================================================


    def load_dataset(self):


        for class_name in self.classes:


            class_folder = (

                self.dataset_path /

                class_name

            )



            # Every video folder

            for video_folder in class_folder.iterdir():



                if not video_folder.is_dir():

                    continue




                # Get frames

                frames = sorted(

                    video_folder.glob("*.jpg")

                )



                # Use only videos having enough frames

                if len(frames) >= self.sequence_length:



                    frames = frames[

                        :self.sequence_length

                    ]



                    self.samples.append(

                        (

                            frames,

                            self.class_to_idx[class_name]

                        )

                    )






    # ========================================================
    # LENGTH
    # ========================================================


    def __len__(self):

        return len(self.samples)






    # ========================================================
    # GET ONE VIDEO SAMPLE
    # ========================================================


    def __getitem__(self,index):


        frame_paths, label = self.samples[index]



        frames = []



        for frame_path in frame_paths:



            # Read image

            image = Image.open(

                frame_path

            ).convert("RGB")



            # PIL -> Tensor

            image = self.transform(image)



            frames.append(image)





        # Shape:
        # (20,3,224,224)

        frames = torch.stack(frames)



        return frames, label






# ============================================================
# TEST DATASET
# ============================================================


if __name__ == "__main__":



    dataset = VideoDataset(


        dataset_path=

        r"D:\Project\Smart-Surveillance-System\ml_model\dataset\extracted_frames",



        sequence_length=20

    )



    print("="*50)

    print("Dataset Loaded Successfully")

    print("="*50)



    print(

        "Total Videos :",

        len(dataset)

    )



    print(

        "Total Classes:",

        len(dataset.classes)

    )




    frames,label = dataset[0]



    print()

    print(

        "One Sample Shape:",

        frames.shape

    )


    print(

        "Label:",

        label

    )