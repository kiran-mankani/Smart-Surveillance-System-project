# ============================================================
# File Name : model.py
# Project   : Smart Surveillance Analytics System
# Model     : CNN + LSTM
#
# Purpose:
#     Ye file CNN + LSTM architecture banati hai.
#
# CNN  -> Har frame se features nikalega.
# LSTM -> Frames ki sequence samjhega.
# FC   -> Final action class predict karega.
# ============================================================


# ============================================================
# STEP 1 - Import Libraries
# ============================================================

import torch
import torch.nn as nn
from torchvision import models


# ============================================================
# STEP 2 - CNN + LSTM Model
# ============================================================

class CNNLSTM(nn.Module):

    def __init__(
        self,
        num_classes,
        hidden_size=256,
        num_layers=2,
        dropout=0.3
    ):

        super().__init__()

        # ====================================================
        # STEP 2.1
        # Load Pretrained ResNet18
        #
        # weights="DEFAULT"
        # Matlab ImageNet par pehle se trained model.
        # Isse training fast aur accurate hoti hai.
        # ====================================================

        self.cnn = models.resnet18(weights=models.ResNet18_Weights.DEFAULT)

        # ====================================================
        # STEP 2.2
        # Last FC Layer remove kar do.
        #
        # ResNet18 normally:
        #
        # Image
        #   ↓
        # CNN
        #   ↓
        # FC (1000 classes)
        #
        # Hume FC nahi chahiye.
        # Sirf features chahiye.
        # ====================================================

        self.cnn = nn.Sequential(
            *list(self.cnn.children())[:-1]
        )

        # ====================================================
        # STEP 2.3
        # LSTM
        #
        # CNN output:
        #
        # 512 features per frame
        # ====================================================

        self.lstm = nn.LSTM(

            input_size=512,

            hidden_size=hidden_size,

            num_layers=num_layers,

            batch_first=True,

            dropout=dropout

        )

        # ====================================================
        # STEP 2.4
        # Dropout
        # ====================================================

        self.dropout = nn.Dropout(dropout)

        # ====================================================
        # STEP 2.5
        # Final Classification Layer
        # ====================================================

        self.fc = nn.Linear(

            hidden_size,

            num_classes

        )

    # ========================================================
    # STEP 3 - Forward Function
    #
    # Input Shape:
    #
    # (Batch, Sequence, Channel, Height, Width)
    #
    # Example:
    #
    # (8,20,3,224,224)
    # ========================================================

    def forward(self, x):

        batch_size, seq_len, c, h, w = x.size()

        # CNN ek time par ek image process karta hai.
        #
        # Isliye reshape karte hain.

        x = x.view(batch_size * seq_len, c, h, w)

        # CNN Features

        x = self.cnn(x)

        # Shape:
        #
        # (Batch*Seq,512,1,1)

        x = x.view(batch_size, seq_len, 512)

        # LSTM

        lstm_output, (hidden, cell) = self.lstm(x)

        # Last Time Step

        x = lstm_output[:, -1, :]

        # Dropout

        x = self.dropout(x)

        # Final Prediction

        x = self.fc(x)

        return x


# ============================================================
# STEP 4 - Testing
# ============================================================

if __name__ == "__main__":

    # Dummy Input
    dummy = torch.randn(

        2,      # Batch Size

        20,     # Frames

        3,      # RGB

        224,

        224

    )

    model = CNNLSTM(

        num_classes=70

    )

    output = model(dummy)

    print("=" * 50)
    print("CNN + LSTM Model Created Successfully")
    print("=" * 50)

    print("Input Shape :", dummy.shape)

    print("Output Shape:", output.shape)