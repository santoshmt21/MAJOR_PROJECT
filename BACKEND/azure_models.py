import os
from pathlib import Path

from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient


BASE_DIR = Path(__file__).resolve().parent
MODEL_DIR = BASE_DIR / "MODELS"

# Runtime models/files required by the application
MODEL_FILES = [
    "class_names.json",
    "cattle_breed_model_v2/best.pt",

    "ViT_Results_85Plus/best_vit_small_patch16_224_cattle.pth",

    "SKIN_DISEASE_MODELS/VIT/vit_cattle_skin_model.pth",
    "SKIN_DISEASE_MODELS/VIT/class_names.json",
    "SKIN_DISEASE_MODELS/YOLO/best (3).pt",

    "NUTRITION_RECOMENDATION_MODEL/cattle_nutrition_tree.pkl",
    "NUTRITION_RECOMENDATION_MODEL/label_encoders.pkl",
]


def ensure_models():
    """
    Download required ML models from Azure Blob Storage.

    On local development, if Azure storage settings are not configured,
    this function does nothing and the existing local MODELS folder is used.
    """

    account_url = os.getenv("AZURE_STORAGE_ACCOUNT_URL")
    container_name = os.getenv("AZURE_STORAGE_CONTAINER", "models")

    # Local development: use existing MODELS folder
    if not account_url:
        print("ℹ️ Azure Storage not configured. Using local MODELS folder.")
        return

    print("☁️ Checking Azure Blob Storage for required models...")

    credential = DefaultAzureCredential()
    blob_service_client = BlobServiceClient(
        account_url=account_url,
        credential=credential,
    )

    container_client = blob_service_client.get_container_client(container_name)

    for relative_path in MODEL_FILES:
        local_path = MODEL_DIR / relative_path

        if local_path.exists():
            print(f"✅ Already exists: {relative_path}")
            continue

        local_path.parent.mkdir(parents=True, exist_ok=True)

        print(f"⬇️ Downloading: {relative_path}")

        blob_client = container_client.get_blob_client(relative_path)

        with open(local_path, "wb") as file:
            download_stream = blob_client.download_blob()
            download_stream.readinto(file)

        print(f"✅ Downloaded: {relative_path}")

    print("✅ All required models are available.")