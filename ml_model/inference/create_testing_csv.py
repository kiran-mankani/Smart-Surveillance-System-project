import os
import pandas as pd


TEST_FOLDER = r"D:\Project\Dataset Videos\New folder\UCF101\Testing Videos"


data = []


for label in os.listdir(TEST_FOLDER):

    class_folder = os.path.join(
        TEST_FOLDER,
        label
    )

    if os.path.isdir(class_folder):

        for video in os.listdir(class_folder):

            if video.lower().endswith((".avi", ".mp4")):

                data.append({
                    "video_name": video,
                    "actual_label": label
                })


df = pd.DataFrame(data)


output = os.path.join(
    TEST_FOLDER,
    "testing_labels.csv"
)


df.to_csv(
    output,
    index=False
)


print("CSV Created Successfully")
print("Location:", output)
print("Total Videos:", len(df))