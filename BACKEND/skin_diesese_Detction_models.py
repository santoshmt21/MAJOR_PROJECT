from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib.pyplot as plt
import torch
import timm
from PIL import Image
from torchvision import transforms

MODEL_PATH = Path(r"C:\Users\Santosh\Desktop\PROJECT_PHASE_1\BACKEND\MODELS\SKIN_DISEASE_MODELS\VIT\vit_cattle_skin_model.pth")
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")


def load_class_names(num_classes: int) -> list[str]:
    skin_class_names_json = Path("MODELS/SKIN_DISEASE_MODELS/VIT/class_names.json")
    if skin_class_names_json.exists():
        with open(skin_class_names_json, "r", encoding="utf-8") as f:
            names = json.load(f)
        if isinstance(names, list) and len(names) >= num_classes:
            return names[:num_classes]

    return [f"class_{i}" for i in range(num_classes)]


def get_state_dict(ckpt: dict) -> dict | None:
    if isinstance(ckpt, dict):
        for key in ("model_state_dict", "state_dict", "model"):
            value = ckpt.get(key)
            if isinstance(value, dict):
                return value

    if isinstance(ckpt, dict) and any(
        k.startswith(("blocks.", "patch_embed.", "cls_token", "norm.")) for k in ckpt
    ):
        return ckpt

    return None


def build_model(model_path: Path = MODEL_PATH) -> tuple[torch.nn.Module, list[str], transforms.Compose]:
    ckpt = torch.load(model_path, map_location="cpu")
    state_dict = get_state_dict(ckpt)

    if state_dict is None:
        raise ValueError(f"Could not find a usable state_dict in checkpoint: {model_path}")

    head_key = next((k for k in state_dict if k in ("head.weight", "classifier.weight", "fc.weight")), None)
    if head_key is None:
        raise ValueError("Checkpoint does not contain a classification head")

    num_classes = state_dict[head_key].shape[0]
    class_names = load_class_names(num_classes)

    model = timm.create_model("vit_base_patch16_224", pretrained=False, num_classes=num_classes)
    model.load_state_dict(state_dict, strict=True)
    model = model.to(DEVICE)
    model.eval()

    transform = transforms.Compose(
        [
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.5, 0.5, 0.5], std=[0.5, 0.5, 0.5]),
        ]
    )

    return model, class_names, transform


def denormalize(tensor: torch.Tensor) -> torch.Tensor:
    mean = torch.tensor([0.5, 0.5, 0.5]).view(3, 1, 1)
    std = torch.tensor([0.5, 0.5, 0.5]).view(3, 1, 1)
    return tensor * std + mean


def predict_image(image_path: str | Path, model: torch.nn.Module, class_names: list[str], transform: transforms.Compose):
    image = Image.open(image_path).convert("RGB")
    image_tensor = transform(image).unsqueeze(0).to(DEVICE)

    with torch.no_grad():
        logits = model(image_tensor)
        probs = torch.softmax(logits, dim=1)
        confidence, pred_idx = torch.max(probs, dim=1)

    predicted_class = class_names[pred_idx.item()]
    confidence_pct = confidence.item() * 100
    return predicted_class, confidence_pct, image


def show_prediction(image_path: str | Path, model: torch.nn.Module, class_names: list[str], transform: transforms.Compose):
    predicted_class, confidence_pct, image = predict_image(image_path, model, class_names, transform)

    plt.figure(figsize=(6, 6))
    plt.imshow(image)
    plt.title(f"Predicted: {predicted_class}\nConfidence: {confidence_pct:.1f}%", fontsize=12)
    plt.axis("off")
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Predict cattle skin disease using the ViT model")
    parser.add_argument("image", nargs="?", default=None, help="Path to the input image file")
    args = parser.parse_args()

    image_path = args.image
    if image_path is None:
        image_path = input("Enter image path: ").strip()

    model, class_names, transform = build_model()
    predicted_class, confidence_pct, _ = predict_image(image_path, model, class_names, transform)

    print(f"Predicted class: {predicted_class}")
    print(f"Confidence: {confidence_pct:.2f}%")

    show_prediction(image_path, model, class_names, transform)
