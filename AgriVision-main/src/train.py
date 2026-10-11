import torch
import torch.nn as nn
import torch.optim as optim
import os
import time
from data_loader import get_data_loaders
from model import create_agrivision_model

def train_model(data_dir, num_epochs=10, batch_size=16, learning_rate=0.001):
    # Config device to use CUDA or CPU
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Training on device: {device}")

    # Init Data Loader and Model
    train_loader, val_loader, classes = get_data_loaders(data_dir, batch_size=batch_size)
    num_classes = len(classes)

    model = create_agrivision_model(num_classes=num_classes, freeze_backbone=False)
    model = model.to(device)

    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=learning_rate)

    best_val_acc = 0.0

    # Archiving model
    os.makedirs("../models", exist_ok=True)

    print("\nSTART TRAINING...")
    start_time = time.time()

    # Training loop
    for epoch in range(num_epochs):
        print(f'\nEpoch {epoch+1}/{num_epochs}')
        print('-' * 15)

        for phase in ['train', 'val']:
            if phase == 'train':
                model.train()
                dataloader = train_loader
            else:
                model.eval()
                dataloader = val_loader
            
            running_loss = 0.0
            running_corrects = 0

            for inputs, labels in dataloader:
                inputs = inputs.to(device)
                labels = labels.to(device)

                optimizer.zero_grad()

                # Forward pass
                with torch.set_grad_enabled(phase == 'train'):
                    outputs = model(inputs)
                    _, preds = torch.max(outputs, 1)
                    loss = criterion(outputs, labels)

                    # Backward pass + Optimize
                    if phase == 'train':
                        loss.backward()
                        optimizer.step()
                
                # Result
                running_loss += loss.item() * inputs.size(0)
                running_corrects += torch.sum(preds == labels.data)
            
            epoch_loss = running_loss / len(dataloader.dataset)
            epoch_acc = running_corrects.double() / len(dataloader.dataset)

            print(f'{phase.capitalize()} | Loss: {epoch_loss:.4f} | Accuracy: {epoch_acc:.4f}')

            if phase == 'val' and epoch_acc > best_val_acc:
                best_val_acc = epoch_acc
                torch.save(model.state_dict(), '../models/best_agrivision_model.pth')
                print("The best model has been updated and saved (best_agrivision_model.pth).")

    time_elapsed = time.time() - start_time
    print(f"\nTraining complete in {time_elapsed // 60:.0f} minutes {time_elapsed % 60:.0f} seconds.")
    print(f"Highest validation accuracy: {best_val_acc:.4f}")

if __name__ == '__main__':
    DATA_PATH = "../data/raw/PlantVillage_Filtered"

    train_model(data_dir=DATA_PATH, num_epochs=5, batch_size=6)