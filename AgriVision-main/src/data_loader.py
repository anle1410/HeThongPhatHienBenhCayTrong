import os
import torch
from torchvision import datasets, transforms
from torch.utils.data import DataLoader, random_split

def get_data_loaders(data_dir, batch_size=32, train_split=0.8):
    # Train set
    train_transforms = transforms.Compose([
        transforms.Resize((224, 224)), # 224x224px Standardization
        transforms.RandomHorizontalFlip(),
        transforms.RandomRotation(20),
        transforms.ColorJitter(brightness=0.2, contrast=0.2),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])

    # Validation/Test set
    val_transforms = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])

    #Load dataset
    full_dataset = datasets.ImageFolder(root=data_dir, transform=train_transforms)

    num_classes = len(full_dataset.classes)
    print(f"Found {num_classes} plant diseases classes.")
    print(full_dataset.classes)

    # Splitting data
    total_size = len(full_dataset)
    train_size = int(train_split * total_size)
    val_size = total_size - train_size

    generator = torch.Generator().manual_seed(42)
    train_dataset, val_dataset = random_split(full_dataset, [train_size, val_size], generator=generator)

    # Update transform
    val_dataset.dataset.transform = val_transforms

    # Create DataLoader
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True, num_workers=2, pin_memory=True)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False, num_workers=2, pin_memory=True)

    return train_loader, val_loader, full_dataset.classes

if __name__ == "__main__":
    DATA_PATH = "../data/raw/PlantVillage_Filtered"

    if os.path.exists(DATA_PATH):
        train_loader, val_loader, classes = get_data_loaders(data_dir=DATA_PATH, batch_size=16)
        print(f"Number of training batches: {len(train_loader)}")
        print(f"Number of validation batches: {len(val_loader)}")
    else:
        print(f"Please download the dataset and place it in the {DATA_PATH}")