import torch
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import confusion_matrix, classification_report
import numpy as np
import os

from data_loader import get_data_loaders
from model import create_agrivision_model

def evaluate_and_plot_matrix(data_dir, model_path, batch_size=16):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Analysing on device: {device}")

    # Load validation data
    _, val_loader, class_names = get_data_loaders(data_dir, batch_size=batch_size)
    num_classes = len(class_names)

    model = create_agrivision_model(num_classes=num_classes)
    if not os.path.exists(model_path):
        print(f"ERROR: Can not find {model_path}")
        return

    model.load_state_dict(torch.load(model_path, map_location=device))
    model.to(device)
    model.eval()

    all_preds = []
    all_labels = []

    print("Predicting on Validation set")
    with torch.no_grad():
        for inputs, labels in val_loader:
            inputs = inputs.to(device)
            labels = labels.to(device)

            outputs = model(inputs)
            _, preds = torch.max(outputs, 1)

            all_preds.extend(preds.cpu().numpy())
            all_labels.extend(labels.cpu().numpy())

    # Print classification report
    print("\n" + "=" * 50)
    print("CLASSIFICATION REPORT")
    print("=" * 50)
    print(classification_report(all_labels, all_preds, target_names=class_names))

    # Draw matrix
    cm = confusion_matrix(all_labels, all_preds)

    # Chart configuration
    plt.figure(figsize=(16, 12))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                xticklabels=class_names, yticklabels=class_names)

    plt.title("Confusion matrix - AgriVision", fontsize=16, fontweight='bold', pad=20)
    plt.ylabel("True label", fontsize=12)
    plt.xlabel("Predicted Label", fontsize=12)

    plt.xticks(rotation=45, ha='right')
    plt.yticks(rotation=0)

    plt.tight_layout()
    save_path = "../models/confusion_matrix.png"
    plt.savefig(save_path, dpi=300)
    print(f"\nSaved chart in: {save_path}")

    plt.show()

if __name__ == "__main__":
    DATA_PATH = "../data/raw/PlantVillage_Filtered"
    MODEL_WEIGHTS_PATH = "../models/best_agrivision_model.pth"

    evaluate_and_plot_matrix(data_dir=DATA_PATH, model_path=MODEL_WEIGHTS_PATH)