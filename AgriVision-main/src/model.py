import torch
import torch.nn as nn
from torchvision import models

def create_agrivision_model(num_classes=19, freeze_backbone=False):
    # Init EfficientNet-B0 model
    weights = models.EfficientNet_B0_Weights.DEFAULT
    model = models.efficientnet_b0(weights=weights)

    if freeze_backbone:
        for param in model.features.parameters():
            param.requires_grad = False

    # Classifier
    in_features = model.classifier[1].in_features

    model.classifier[1] = nn.Linear(in_features=in_features, out_features=num_classes)

    return model

if __name__ == "__main__":
    model = create_agrivision_model(num_classes=19)

    dummy_input = torch.randn(16, 3, 224, 224)

    output = model(dummy_input)

    print(f"New Classifier architecture: \n{model.classifier}")
    print(f"Output size: {output.shape} (Expected: [16, 19])")