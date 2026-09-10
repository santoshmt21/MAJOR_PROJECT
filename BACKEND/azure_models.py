import os
from pathlib import Path

from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient


BASE_DIR = Path(__file__).resolve().parent
MODEL_DIR = BASE_DIR / "MODELS"


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


def download_blob_resumable(blob_client, local_path):
    """Download Azure blob safely in chunks."""

    properties = blob_client.get_blob_properties()
    total_size = properties.size

    print(
        f"☁️ Blob size: "
        f"{total_size / (1024 * 1024):.1f} MB"
    )

    local_path.parent.mkdir(parents=True, exist_ok=True)

    temp_path = Path(str(local_path) + ".part")

    # ---------------------------------------------------------
    # IMPORTANT:
    # Small metadata files are downloaded FRESH.
    # This prevents corrupted JSON/PKL files from being resumed.
    # ---------------------------------------------------------
    if local_path.suffix.lower() in [".json", ".pkl"]:
        if local_path.exists():
            local_path.unlink()

        if temp_path.exists():
            temp_path.unlink()

        downloaded = 0

    else:
        # -----------------------------------------------------
        # Large model files: resume safely if possible
        # -----------------------------------------------------
        downloaded = (
            temp_path.stat().st_size
            if temp_path.exists()
            else 0
        )

        # Already complete
        if (
            local_path.exists()
            and local_path.stat().st_size == total_size
        ):
            print(f"✅ Already complete: {local_path.name}")
            return

        # Old partial final file
        if (
            local_path.exists()
            and local_path.stat().st_size < total_size
        ):
            if not temp_path.exists():
                local_path.rename(temp_path)

            downloaded = temp_path.stat().st_size

        # Corrupt/oversized partial file
        if downloaded > total_size:
            print("⚠️ Invalid partial file. Starting fresh.")
            temp_path.unlink()
            downloaded = 0

    print(
        f"⬇️ Downloading {blob_client.blob_name} "
        f"({downloaded / (1024 * 1024):.1f} / "
        f"{total_size / (1024 * 1024):.1f} MB)"
    )

    chunk_size = 4 * 1024 * 1024  # 4 MB

    # Append for resumable large models.
    # Fresh files start from an empty .part file.
    with open(temp_path, "ab") as file:

        while downloaded < total_size:

            length = min(
                chunk_size,
                total_size - downloaded
            )

            print(
                f"   📦 Downloading bytes "
                f"{downloaded:,} - "
                f"{downloaded + length - 1:,}"
            )

            stream = blob_client.download_blob(
                offset=downloaded,
                length=length,
                max_concurrency=1,
            )

            data = stream.readall()

            if not data:
                raise RuntimeError(
                    f"Azure returned empty data while downloading "
                    f"{blob_client.blob_name} "
                    f"at byte {downloaded}"
                )

            file.write(data)
            file.flush()

            downloaded += len(data)

            print(
                f"   ✅ Progress: "
                f"{downloaded / (1024 * 1024):.1f} / "
                f"{total_size / (1024 * 1024):.1f} MB"
            )

    # ---------------------------------------------------------
    # Verify final size
    # ---------------------------------------------------------
    actual_size = temp_path.stat().st_size

    if actual_size != total_size:
        raise RuntimeError(
            f"Download incomplete for "
            f"{blob_client.blob_name}: "
            f"{actual_size} / {total_size} bytes"
        )

    # Atomic replacement
    temp_path.replace(local_path)

    print(
        f"✅ Downloaded: "
        f"{blob_client.blob_name}"
    )


def ensure_models():

    account_url = os.getenv(
        "AZURE_STORAGE_ACCOUNT_URL"
    )

    container_name = os.getenv(
        "AZURE_STORAGE_CONTAINER",
        "models"
    )

    if not account_url:
        print(
            "ℹ️ Azure Storage not configured. "
            "Using local MODELS folder."
        )
        return

    print(
        "☁️ Checking Azure Blob Storage "
        "for required models..."
    )

    credential = DefaultAzureCredential()

    blob_service_client = BlobServiceClient(
        account_url=account_url,
        credential=credential,
    )

    container_client = (
        blob_service_client
        .get_container_client(container_name)
    )

    for relative_path in MODEL_FILES:

        local_path = MODEL_DIR / relative_path

        blob_client = (
            container_client
            .get_blob_client(relative_path)
        )

        print(
            f"\n🔍 Checking: {relative_path}"
        )

        download_blob_resumable(
            blob_client,
            local_path,
        )

    print(
        "\n✅ All required models are available."
    )