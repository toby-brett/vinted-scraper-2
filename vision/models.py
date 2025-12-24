import torch.nn as nn
from torchvision.models import resnet34, resnet50
from torchvision import models
import torch

class REGRESSOR(nn.Module):
    def __init__(self):
        super().__init__()
        self.backbone = resnet34(weights="IMAGENET1K_V1")

        for name, param in self.backbone.named_parameters():
            if "layer3" in name or "layer4" in name:
                param.requires_grad = True
            else:
                param.requires_grad = False

        for m in self.backbone.modules():
            if isinstance(m, nn.BatchNorm2d):
                m.eval()
                m.requires_grad_(False)

        self.backbone.fc = nn.Identity()
        self.regressor = nn.Sequential(
            nn.Linear(512, 512),
            nn.ReLU(),
            nn.Dropout(0.5),
            nn.Linear(512, 256),
            nn.ReLU(),
            nn.Dropout(0.5),
            nn.Linear(256, 1)
        )

    def forward(self, x):
        x = self.backbone(x)
        return self.regressor(x).squeeze(1)


def CLASSIFY(num_classes=18):
    model = models.resnet50(weights=models.ResNet50_Weights.IMAGENET1K_V1)

    # Freeze layers 1 & 2, train layers 3 & 4 + head
    for param in model.parameters():
        param.requires_grad = False

    # Improved classification head
    in_features = model.fc.in_features
    model.fc = nn.Sequential(
        nn.Linear(in_features, 1024),
        nn.BatchNorm1d(1024),
        nn.ReLU(inplace=True),
        nn.Dropout(0.4),
        nn.Linear(1024, 512),
        nn.ReLU(inplace=True),
        nn.Dropout(0.3),
        nn.Linear(512, num_classes)
    )

    return model