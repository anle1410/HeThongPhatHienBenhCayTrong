import os
import torch
import numpy as np
import cv2
import matplotlib.pyplot as plt
from PIL import Image
from torchvision import transforms

from pytorch_grad_cam import GradCAM
from pytorch_grad_cam.utils.image import show_cam_on_image
from pytorch_grad_cam.utils.model_targets import ClassifierOutputTarget

from model import create_agrivision_model

def generate_heatmap(image_path, model_path, class_names):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Processing Grad-CAM on: {device}")

    num_classes = len(class_names)
    model = create_agrivision_model(num_classes=num_classes)

    if not os.path.exists(model_path):
        print(f"ERROR: Can not find the weight file {model_path}")
        return
    
    model.load_state_dict(torch.load(model_path, map_location=device))
    model.to(device)
    model.eval()

    target_layers = [model.features[-1]]

    # Preprocessing
    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])

    img = Image.open(image_path).convert('RGB')
    input_tensor = transform(img).unsqueeze(0).to(device)

    rgb_img = img.resize((224, 224))
    rgb_img = np.float32(rgb_img) / 255

    # Init GradCAM
    cam = GradCAM(model=model, target_layers=target_layers)

    # Get heat matrix
    grayscale_cam = cam(input_tensor=input_tensor, targets=None)
    grayscale_cam = grayscale_cam[0, :]

    # Stack heat map on to image
    visualization = show_cam_on_image(rgb_img, grayscale_cam, use_rgb=True)

    # Draw original picture
    plt.figure(figsize=(10, 5))
    plt.subplot(1, 2, 1)
    plt.imshow(rgb_img)
    plt.title("Original picture", fontsize=12)
    plt.axis('off')

    # Draw with heatmap
    plt.subplot(1, 2, 1)
    plt.imshow(visualization)
    plt.title('Grad-CAM heatmap', fontsize=12)
    plt.axis('off')

    plt.tight_layout()

    # Save file
    save_path = '../models/grad_cam_result.png'
    plt.savefig(save_path, dpi=300)
    print(f"Exported heatmap at: {save_path}")

    plt.show()

if __name__ == "__main__":
    CLASSES = [
        'Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot',
        'Corn_(maize)___Common_rust_',
        'Corn_(maize)___Northern_Leaf_Blight',
        'Corn_(maize)___healthy',
        'Pepper,_bell___Bacterial_spot',
        'Pepper,_bell___healthy',
        'Potato___Early_blight',
        'Potato___Late_blight',
        'Potato___healthy',
        'Tomato___Bacterial_spot',
        'Tomato___Early_blight',
        'Tomato___Late_blight',
        'Tomato___Leaf_Mold',
        'Tomato___Septoria_leaf_spot',
        'Tomato___Spider_mites Two-spotted_spider_mite',
        'Tomato___Target_Spot',
        'Tomato___Tomato_Yellow_Leaf_Curl_Virus',
        'Tomato___Tomato_mosaic_virus',
        'Tomato___healthy'
    ]

    TEST_IMAGE_PATH = "../data/raw/PlantVillage_Filtered/Potato___Early_blight/0a8a68ee-f587-4dea-beec-79d02e7d3fa4___RS_Early.B 8461.JPG"
    MODEL_WEIGHTS_PATH = "../models/best_agrivision_model.pth"

    if os.path.exists(TEST_IMAGE_PATH):
        generate_heatmap(TEST_IMAGE_PATH, MODEL_WEIGHTS_PATH, CLASSES)
    else:
        print("Please make sure TEST_IMAGE_PATH is valid.")