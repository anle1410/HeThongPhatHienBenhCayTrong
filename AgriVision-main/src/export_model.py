import torch
import os
from model import create_agrivision_model

def export_to_onnx(pth_path, onnx_path, num_classes=19):
    print("Downloading Pytorch model...")
    device = torch.device("cpu") # Because model will be running on phones

    model = create_agrivision_model(num_classes=num_classes)

    if not os.path.exists(pth_path):
        print(f"ERRROR: Can not find the file {pth_path}")
        return
    
    model.load_state_dict(torch.load(pth_path, map_location=device))
    model.eval()

    dummy_input = torch.randn(1, 3, 224, 224, device=device)

    print("Converting to ONNX...")

    # Export file
    torch.onnx.export(
        model,
        dummy_input,
        onnx_path,
        export_params=True,
        opset_version=11,
        do_constant_folding=True,
        input_names=['input'],
        output_names=['output'],
        dynamic_axes={'input': {0: 'batch_size'},
                      'output': {0: 'batch_size'}}
    )

    print(f"Export complete: {onnx_path}")

if __name__ == "__main__":
    PTH_FILE = "../models/best_agrivision_model.pth"
    ONNX_FILE = "../models/agrivision_model.onnx"

    export_to_onnx(PTH_FILE, ONNX_FILE)