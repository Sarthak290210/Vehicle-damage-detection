from pathlib import Path

import torch
from torch import nn
from torchvision import models, transforms
from PIL import Image, ImageOps

# Works no matter which folder you launch Streamlit from.
MODEL_PATH = Path(__file__).resolve().parent / "model" / "saved_model.pth"

# Same order as ImageFolder's alphabetical class order in the notebook:
# ['F_Breakage', 'F_Crushed', 'F_Normal', 'R_Breakage', 'R_Crushed', 'R_Normal']
class_names = ['Front Breakage', 'Front Crushed', 'Front Normal', 'Rear Breakage', 'Rear Crushed', 'Rear Normal']

trained_model = None

# Identical to the notebook's evaluation preprocessing (no random augmentation).
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
])


class CarClassifierResNetUnfreeze(nn.Module):
    def __init__(self, nums_classes=6):
        super().__init__()
        # weights=None: the trained weights are loaded from saved_model.pth below,
        # so there is no need to download the ImageNet weights on every start.
        self.model = models.resnet50(weights=None)
        self.model.fc = nn.Sequential(
            nn.Dropout(0.223),
            nn.Linear(self.model.fc.in_features, nums_classes)
        )

    def forward(self, x):
        return self.model(x)


def load_model():
    model = CarClassifierResNetUnfreeze()
    model.load_state_dict(torch.load(MODEL_PATH, map_location="cpu"))
    model.eval()
    return model


def predict(image_path):
    # exif_transpose fixes phone photos that are stored rotated
    image = ImageOps.exif_transpose(Image.open(image_path)).convert("RGB")
    image_tensor = transform(image).unsqueeze(0)

    global trained_model
    if trained_model is None:
        trained_model = load_model()

    with torch.no_grad():
        output = trained_model(image_tensor)
        _, predicted_class = torch.max(output, 1)
        return class_names[predicted_class.item()]