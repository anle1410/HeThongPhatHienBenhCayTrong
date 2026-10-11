import torch
from sympy.stats.rv import probability
from torchvision import transforms
from PIL import Image
import os
from model import create_agrivision_model

def predict_image(image_path, model_path, class_names):
    # Device configuration
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    # Start model
    num_classes = len(class_names)
    model = create_agrivision_model(num_classes=num_classes)

    if not os.path.exists(model_path):
        print(f"ERROR: Can not find the weight file in {model_path}")
        return None, None
    
    # Load weights
    model.load_state_dict(torch.load(model_path, map_location=device))
    model.to(device)

    model.eval()

    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])

    try:
        img = Image.open(image_path).convert('RGB')
    except Exception as e:
        print(f"ERROR when reading image: {e}")
        return None, None

    # Covert to Tensor and add Batch
    img_tensor = transform(img).unsqueeze(0).to(device)

    # Prediction
    with torch.no_grad():
        outputs = model(img_tensor)
        probabilities = torch.nn.functional.softmax(outputs[0], dim=0)
        max_prob, predicted_idx = torch.max(probabilities, dim=0)

        predicted_class = class_names[predicted_idx.item()]
        confidence = max_prob.item() * 100

    # Print result
    print(f"\n{'-' * 30}")
    print("PREDICTION RESULT")
    print(f"{'-' * 30}")
    print(f"Folder: {os.path.basename(image_path)}")
    print(f"Predict: {predicted_class}")
    print(f"Confidence: {confidence:.2f}%")
    print(f"{'-' * 30}\n")

    return predicted_class, confidence

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

    if len(CLASSES) < 19:
        CLASSES = [f"Disease {i}" for i in range(19)]

    TEST_IMAGE_PATH = "../data/raw/PlantVillage_Filtered/Corn_(maize)___healthy/0a1a49a8-3a95-415a-b115-4d6d136b980b___R.S_HL 8216 copy.jpg"
    MODEL_WEIGHTS_PATH = "../models/best_agrivision_model.pth"

    if os.path.exists(TEST_IMAGE_PATH):
        predict_image(TEST_IMAGE_PATH, MODEL_WEIGHTS_PATH, CLASSES)
    else:
        print(f"Please check you TEST_IMAGE_PATH, make sure it's a valid path and have a real image")