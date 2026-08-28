import io
import json
import logging
import os
from pathlib import Path
from typing import Optional

import numpy as np
import torch
from PIL import Image
from torchvision import transforms
import uvicorn
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from rag import initialize_rag_service, get_rag_service
from NUTRITION_RECOMEND import (
    get_nutrition_options,
    get_recommendation,
    load_nutrition_recommendation_model,
)
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def get_db_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", "5432")),
        database=os.getenv("DB_NAME", "PROJECT_PHASE_1"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD", "Anand@joy21")
    )

def map_breed_to_frontend(breed_row, traits):
    b_id, name, common_name, b_type, state, country, badge, desc, w_min, w_max, lifespan, milk_min, milk_max, img_url, _, _ = breed_row
    
    # Format origin
    if state:
        origin = f"{state}, {country}"
    else:
        origin = country
        
    # Format weight
    weight = f"{w_min}–{w_max} kg"
    
    # Format lifespan
    lifespan_str = f"{lifespan} years"
    
    # Format milk
    if milk_min is not None and milk_max is not None:
        milk = f"{milk_min:,}–{milk_max:,} L/year"
    else:
        milk = "Limited"
        
    # Color mapping
    colors = {
        "dairy": "#2D5016",
        "beef": "#1A1A1A",
        "draft": "#6B7280",
        "dual purpose": "#8B4513"
    }
    color = colors.get(b_type.lower(), "#C4872A")
    
    # Realistic nutrition mapping based on type
    nutrition_presets = {
        "dairy": {
            "dm": "18–26 kg/day",
            "protein": "16–18%",
            "energy": "1.62–1.72 Mcal NEl/kg",
            "fiber": "28–32% NDF",
            "tips": "Requires high-energy TMR diet. Supplement with bypass protein during peak lactation. Ensure adequate calcium and phosphorus."
        },
        "beef": {
            "dm": "18–22 kg/day",
            "protein": "11–13%",
            "energy": "1.28–1.42 Mcal NEg/kg",
            "fiber": "38–45% NDF",
            "tips": "Finish on high-grain diet for premium marbling. Avoid over-conditioning in breeding cows. Creep feeding calves improves weaning weights."
        },
        "draft": {
            "dm": "15–20 kg/day",
            "protein": "10–12%",
            "energy": "1.40–1.52 Mcal NEm/kg",
            "fiber": "40–48% NDF",
            "tips": "Maintains body condition on low-quality roughage. Supplement protein (urea-molasses block) in dry season. Provide shade and water."
        },
        "dual purpose": {
            "dm": "12–16 kg/day",
            "protein": "12–14%",
            "energy": "1.45–1.55 Mcal NEl/kg",
            "fiber": "35–40% NDF",
            "tips": "Thrives on crop residues and local fodder. Supplement with concentrates (1.5–2 kg) during lactation. Avoid high-grain diets."
        }
    }
    
    nutrition = nutrition_presets.get(b_type.lower(), {
        "dm": "14–18 kg/day",
        "protein": "12–15%",
        "energy": "1.45–1.60 Mcal NEl/kg",
        "fiber": "32–36% NDF",
        "tips": "Balance roughage with concentrates. Mineral supplementation critical. Ensure clean water access at all times."
    })
    
    # Custom tweaks for known breeds
    lname = name.lower()
    if "holstein" in lname:
        nutrition = {
            "dm": "22–26 kg/day",
            "protein": "16–18%",
            "energy": "1.65–1.72 Mcal NEl/kg",
            "fiber": "28–32% NDF",
            "tips": "Requires high-energy TMR diet. Supplement with bypass protein during peak lactation. Ensure adequate calcium and phosphorus to prevent milk fever."
        }
    elif "gir" in lname:
        nutrition = {
            "dm": "12–16 kg/day",
            "protein": "12–14%",
            "energy": "1.45–1.55 Mcal NEl/kg",
            "fiber": "35–40% NDF",
            "tips": "Thrives on crop residues and local fodder. Supplement with concentrates (1.5–2 kg) during lactation. Avoid high-grain diets to prevent acidosis."
        }
    elif "sahiwal" in lname:
        nutrition = {
            "dm": "14–18 kg/day",
            "protein": "13–15%",
            "energy": "1.50–1.62 Mcal NEl/kg",
            "fiber": "32–36% NDF",
            "tips": "Balance roughage with concentrates. Mineral supplementation critical — especially magnesium and phosphorus. Ensure salt licks year-round."
        }
    elif "angus" in lname:
        nutrition = {
            "dm": "18–22 kg/day",
            "protein": "11–13%",
            "energy": "1.28–1.42 Mcal NEg/kg",
            "fiber": "38–45% NDF",
            "tips": "Finish on high-grain diet for 90–120 days for premium marbling. Avoid over-conditioning in breeding cows. Creep feeding calves improves weaning weights."
        }
    elif "jersey" in lname:
        nutrition = {
            "dm": "16–20 kg/day",
            "protein": "17–19%",
            "energy": "1.62–1.70 Mcal NEl/kg",
            "fiber": "28–30% NDF",
            "tips": "Higher metabolizable protein needed due to rich milk. Prone to hypocalcemia — pre-partum anion diet essential. Avoid overfeeding — obesity risk is high in Jerseys."
        }
    elif "ongole" in lname:
        nutrition = {
            "dm": "15–20 kg/day",
            "protein": "10–12%",
            "energy": "1.40–1.52 Mcal NEm/kg",
            "fiber": "40–48% NDF",
            "tips": "Maintains body condition on low-quality roughage. Supplement protein (urea-molasses block) in dry season. Provide shade and water during peak heat."
        }

    return {
        "name": name,
        "origin": origin,
        "type": b_type,
        "weight": weight,
        "lifespan": lifespan_str,
        "milk": milk,
        "color": color,
        "badge": badge or f"{b_type} Breed",
        "desc": desc or f"Characteristics of {name} cattle.",
        "traits": traits,
        "nutrition": nutrition
    }

# ─────────────────────────────────────────────
# Logging
# ─────────────────────────────────────────────
logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────
# Config
# ─────────────────────────────────────────────
MODELS_DIR = Path(os.getenv("MODELS_DIR", "MODELS"))

MODEL_PATHS = [
    MODELS_DIR / "cattle_breed_model_v2/best.pt",
    MODELS_DIR / "best_vit_small_patch16_224_cattle.pth",
    MODELS_DIR / "ViT_Results_85Plus/best_vit_small_patch16_224_cattle.pth",
]
SKIN_MODEL_PATH = MODELS_DIR / "SKIN_DISEASE_MODELS/VIT/vit_cattle_skin_model.pth"
SKIN_YOLO_MODEL_PATH = MODELS_DIR / "SKIN_DISEASE_MODELS/YOLO/best (3).pt"
CLASS_NAMES_PATH = MODELS_DIR / "class_names.json"   # optional – auto-built if absent
SKIN_CLASS_NAMES_PATH = MODELS_DIR / "SKIN_DISEASE_MODELS/VIT/class_names.json"
IMAGE_SIZE  = 320
DEVICE      = torch.device("cuda" if torch.cuda.is_available() else "cpu")


def find_model_path() -> Path:
    for path in MODEL_PATHS:
        if path.exists():
            if path != MODEL_PATHS[0]:
                logger.info(f"Using fallback model path: {path}")
            return path

    candidates = sorted(MODELS_DIR.rglob("*.pth"))
    if candidates:
        fallback = candidates[0]
        logger.warning(f"Default model path not found; using first available .pth in {MODELS_DIR}: {fallback}")
        return fallback

    return MODEL_PATHS[0]

# ─────────────────────────────────────────────
# Load class names
#   Priority: MODELS/class_names.json  ▸  checkpoint key  ▸  numeric fallback
# ─────────────────────────────────────────────
def load_class_names(source, num_classes: int) -> list[str]:
    model_names = None
    if hasattr(source, "names"):
        model_names = source.names
        if isinstance(model_names, dict):
            model_names = [model_names[k] for k in sorted(model_names, key=lambda x: int(x))]
        elif isinstance(model_names, (list, tuple)):
            model_names = list(model_names)

    if CLASS_NAMES_PATH.exists():
        with open(CLASS_NAMES_PATH) as f:
            names = json.load(f)
        logger.info(f"Loaded {len(names)} class names from {CLASS_NAMES_PATH}")
        if model_names is not None and len(names) != len(model_names):
            logger.warning(
                "class_names.json contains %d names but the model defines %d names; using model names instead.",
                len(names), len(model_names)
            )
            return model_names
        if num_classes > 0 and len(names) != num_classes:
            logger.warning(
                "class_names.json contains %d names but expected %d classes; using model names when available.",
                len(names), num_classes
            )
            if model_names is not None:
                return model_names
        return names

    if isinstance(source, dict):
        for key in ("class_names", "classes", "idx_to_class", "label_names"):
            if key in source:
                names = source[key]
                if isinstance(names, dict):
                    names = [names[str(i)] for i in range(len(names))]
                logger.info(f"Loaded {len(names)} class names from checkpoint key '{key}'")
                if model_names is not None and len(names) != len(model_names):
                    logger.warning(
                        "Checkpoint class list contains %d names but the model defines %d names; using model names instead.",
                        len(names), len(model_names)
                    )
                    return model_names
                return names

    if model_names is not None:
        logger.info(f"Loaded {len(model_names)} class names from model names")
        return model_names

    if num_classes > 0:
        logger.warning("No class names found – using numeric labels.")
        return [f"class_{i}" for i in range(num_classes)]

    raise ValueError("No class names were found for the model.")


# ─────────────────────────────────────────────
# Load model
# ─────────────────────────────────────────────
def load_yolo_model():
    try:
        from ultralytics import YOLO
    except ImportError as exc:
        raise ImportError(
            "Ultralytics is required to load the YOLO model. "
            "Install it with `pip install ultralytics`."
        ) from exc

    model_path = find_model_path()
    if not model_path.exists():
        raise FileNotFoundError(f"Model not found at {model_path}")

    logger.info(f"Loading YOLO model from {model_path}")
    model = YOLO(model_path)
    logger.info(f"YOLO model loaded")
    return model


def load_vit_model():
    try:
        import timm
    except ImportError:
        logger.warning("timm not available; ViT model will not be loaded")
        return None

    vit_path = MODELS_DIR / "ViT_Results_85Plus/best_vit_small_patch16_224_cattle.pth"
    if not vit_path.exists():
        logger.warning(f"ViT checkpoint not found at {vit_path}")
        return None

    try:
        logger.info(f"Loading ViT model from {vit_path}")
        ckpt = torch.load(vit_path, map_location=DEVICE)

        state_dict = (
            ckpt.get("model_state_dict")
            or ckpt.get("state_dict")
            or ckpt.get("model")
            or (
                ckpt
                if isinstance(ckpt, dict)
                and any(
                    k.startswith(("blocks.", "patch_embed.", "cls_token"))
                    for k in ckpt
                )
                else None
            )
        )

        if state_dict is None:
            logger.warning("Cannot find state_dict in ViT checkpoint")
            return None

        head_key = next(
            (k for k in state_dict if k in ("head.weight", "classifier.weight", "fc.weight")),
            None,
        )
        if head_key is None:
            logger.warning("Cannot find classification head in ViT state_dict")
            return None

        num_classes = state_dict[head_key].shape[0]
        model = timm.create_model(
            "vit_small_patch16_224", pretrained=False, num_classes=num_classes
        )
        model.load_state_dict(state_dict, strict=True)
        model.to(DEVICE)
        model.eval()
        logger.info(f"ViT model loaded with {num_classes} classes")
        return model
    except Exception as e:
        logger.exception(f"Failed to load ViT model: {e}")
        return None


def load_skin_disease_model():
    try:
        import timm
    except ImportError:
        logger.warning("timm not available; skin disease ViT model will not be loaded")
        return None

    if not SKIN_MODEL_PATH.exists():
        logger.warning(f"Skin disease checkpoint not found at {SKIN_MODEL_PATH}")
        return None

    try:
        logger.info(f"Loading skin disease ViT model from {SKIN_MODEL_PATH}")
        ckpt = torch.load(SKIN_MODEL_PATH, map_location=DEVICE)

        state_dict = (
            ckpt.get("model_state_dict")
            or ckpt.get("state_dict")
            or ckpt.get("model")
            or (
                ckpt
                if isinstance(ckpt, dict)
                and any(
                    k.startswith(("blocks.", "patch_embed.", "cls_token"))
                    for k in ckpt
                )
                else None
            )
        )

        if state_dict is None:
            logger.warning("Cannot find state_dict in skin disease checkpoint")
            return None

        head_key = next(
            (k for k in state_dict if k in ("head.weight", "classifier.weight", "fc.weight")),
            None,
        )
        if head_key is None:
            logger.warning("Cannot find classification head in skin disease checkpoint")
            return None

        num_classes = state_dict[head_key].shape[0]
        model = timm.create_model(
            "vit_base_patch16_224", pretrained=False, num_classes=num_classes
        )
        model.load_state_dict(state_dict, strict=True)
        model.to(DEVICE)
        model.eval()
        logger.info(f"Skin disease ViT model loaded with {num_classes} classes")
        return model
    except Exception as e:
        logger.exception(f"Failed to load skin disease ViT model: {e}")
        return None


def load_skin_yolo_model():
    try:
        from ultralytics import YOLO
    except ImportError as exc:
        raise ImportError(
            "Ultralytics is required to load the skin YOLO model."
        ) from exc

    if not SKIN_YOLO_MODEL_PATH.exists():
        raise FileNotFoundError(f"Skin YOLO model not found at {SKIN_YOLO_MODEL_PATH}")

    logger.info(f"Loading skin disease YOLO model from {SKIN_YOLO_MODEL_PATH}")
    model = YOLO(SKIN_YOLO_MODEL_PATH)
    logger.info("Skin disease YOLO model loaded")
    return model




# ─────────────────────────────────────────────
# FastAPI app
# ─────────────────────────────────────────────
app = FastAPI(
    title="Cattle Breed Classifier",
    description="Dual-model cattle breed identification (YOLO + ViT)",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],       # tighten in production
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── global model state ────────────────────────
YOLO_MODEL = None
VIT_MODEL: Optional[torch.nn.Module] = None
SKIN_VIT_MODEL: Optional[torch.nn.Module] = None
SKIN_YOLO_MODEL = None
CLASS_NAMES: Optional[list[str]] = None
SKIN_CLASS_NAMES: Optional[list[str]] = None
VIT_TRANSFORM = transforms.Compose(
    [
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(
            mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]
        ),
    ]
)
SKIN_VIT_TRANSFORM = transforms.Compose(
    [
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.5, 0.5, 0.5], std=[0.5, 0.5, 0.5]),
    ]
)


@app.on_event("startup")
async def startup_event():
    global YOLO_MODEL, VIT_MODEL, SKIN_VIT_MODEL, SKIN_YOLO_MODEL, CLASS_NAMES, SKIN_CLASS_NAMES
    try:
        YOLO_MODEL = load_yolo_model()
        VIT_MODEL = load_vit_model()
        SKIN_VIT_MODEL = load_skin_disease_model()
        SKIN_YOLO_MODEL = load_skin_yolo_model()
        if YOLO_MODEL is None:
            raise RuntimeError("YOLO model failed to load")
        num_classes = len(YOLO_MODEL.names) if hasattr(YOLO_MODEL, "names") else 0
        CLASS_NAMES = load_class_names(YOLO_MODEL, num_classes)
        if SKIN_CLASS_NAMES_PATH.exists():
            with open(SKIN_CLASS_NAMES_PATH, "r", encoding="utf-8") as f:
                SKIN_CLASS_NAMES = json.load(f)
        else:
            SKIN_CLASS_NAMES = [f"class_{i}" for i in range(4)]
        logger.info(f"✅ YOLO model ready")
        if VIT_MODEL is not None:
            logger.info(f"✅ ViT model ready")
        else:
            logger.info(f"⚠️  ViT model not available")
        if SKIN_VIT_MODEL is not None:
            logger.info(f"✅ Skin disease ViT model ready")
        else:
            logger.info(f"⚠️  Skin disease ViT model not available")
        if SKIN_YOLO_MODEL is not None:
            logger.info(f"✅ Skin disease YOLO model ready")
        else:
            logger.info(f"⚠️  Skin disease YOLO model not available")

        # Initialize RAG service
        logger.info("Initializing RAG service...")
        initialize_rag_service()
        logger.info("✅ RAG service ready")
    except Exception as e:
        logger.error(f"❌ Model failed to load: {e}")
        raise


# ─────────────────────────────────────────────
# Routes
# ─────────────────────────────────────────────

@app.get("/", tags=["Health"])
def root():
    return {"status": "ok", "model": "cattle_breed_model_v2", "device": str(DEVICE)}


@app.get("/health", tags=["Health"])
def health():
    return {
        "status": "healthy" if YOLO_MODEL is not None else "model_not_loaded",
        "num_classes": len(CLASS_NAMES) if CLASS_NAMES else 0,
        "device": str(DEVICE),
        "yolo_loaded": YOLO_MODEL is not None,
        "vit_loaded": VIT_MODEL is not None,
    }


@app.get("/classes", tags=["Info"])
def get_classes():
    """Return all breed labels the model can predict."""
    if CLASS_NAMES is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    return {"num_classes": len(CLASS_NAMES), "classes": CLASS_NAMES}


@app.post("/predict", tags=["Prediction"])
async def predict(file: UploadFile = File(..., description="Cattle image (JPEG / PNG)")):
    """
    Upload a cattle image and receive breed predictions from both YOLO and ViT models.

    Returns predictions from both models:
    - **yolo**: YOLO top-1 and top-5 predictions
    - **vit**: ViT top-1 and top-5 predictions (if available)
    - **filename**: uploaded file name
    """
    if YOLO_MODEL is None:
        raise HTTPException(status_code=503, detail="YOLO model is not loaded yet.")

    # ── validate content type ────────────────
    if file.content_type not in ("image/jpeg", "image/png", "image/jpg", "image/webp"):
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{file.content_type}'. Send JPEG or PNG."
        )

    try:
        image_bytes = await file.read()
        img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        np_img = np.array(img)

        yolo_result = None
        vit_result = None

        # ── YOLO prediction ──────────────────────
        try:
            results = YOLO_MODEL.predict(
                source=img,
                device="cuda" if DEVICE.type == "cuda" else "cpu",
                imgsz=IMAGE_SIZE,
                save=False,
                verbose=False,
            )

            if results:
                result = results[0]
                probs = getattr(result, "probs", None)
                if probs is not None:
                    scores = getattr(probs, "data", probs)
                    if not isinstance(scores, torch.Tensor):
                        scores = torch.as_tensor(scores, device=DEVICE)
                    else:
                        scores = scores.to(DEVICE)

                    if scores.dim() > 0:
                        top5_probs, top5_idx = torch.topk(
                            scores, k=min(5, len(CLASS_NAMES))
                        )
                        yolo_result = {
                            "predicted_class": CLASS_NAMES[top5_idx[0].item()],
                            "confidence": round(top5_probs[0].item(), 4),
                            "top5": [
                                {
                                    "class": CLASS_NAMES[i.item()],
                                    "confidence": round(p.item(), 4),
                                }
                                for p, i in zip(top5_probs, top5_idx)
                            ],
                        }
        except Exception as e:
            logger.exception(f"YOLO prediction error: {e}")
            yolo_result = {"error": str(e)}

        # ── ViT prediction ───────────────────────
        if VIT_MODEL is not None:
            try:
                tensor = VIT_TRANSFORM(img).unsqueeze(0).to(DEVICE)
                with torch.no_grad():
                    logits = VIT_MODEL(tensor)
                    probs = torch.softmax(logits, dim=1)[0]
                    top5_probs, top5_idx = torch.topk(
                        probs, k=min(5, len(CLASS_NAMES))
                    )
                    vit_result = {
                        "predicted_class": CLASS_NAMES[top5_idx[0].item()],
                        "confidence": round(top5_probs[0].item(), 4),
                        "top5": [
                            {
                                "class": CLASS_NAMES[i.item()],
                                "confidence": round(p.item(), 4),
                            }
                            for p, i in zip(top5_probs, top5_idx)
                        ],
                    }
            except Exception as e:
                logger.exception(f"ViT prediction error: {e}")
                vit_result = {"error": str(e)}

        return JSONResponse(
            {
                "yolo": yolo_result,
                "vit": vit_result,
                "filename": file.filename,
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Prediction error")
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")


class NutritionRecommendationRequest(BaseModel):
    breed: str
    category: str
    weight_kg: float
    age_months: float
    milk_yield_l: float
    bcs: float
    activity_level: str
    health_status: str


@app.post("/nutrition-recommendation", tags=["Nutrition"])
async def nutrition_recommendation(payload: NutritionRecommendationRequest):
    """Return nutrient targets and health notes from the persisted decision-tree model."""
    try:
        recommendation = get_recommendation(
            breed=payload.breed,
            category=payload.category,
            weight=payload.weight_kg,
            age=payload.age_months,
            milk=payload.milk_yield_l,
            bcs=payload.bcs,
            activity=payload.activity_level,
            health=payload.health_status,
        )
        return JSONResponse({"recommendation": recommendation})
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except FileNotFoundError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("Nutrition recommendation error")
        raise HTTPException(status_code=500, detail=f"Recommendation failed: {str(exc)}") from exc


@app.get("/nutrition-options", tags=["Nutrition"])
async def nutrition_options():
    """Return categorical values supported by the persisted nutrition encoders."""
    try:
        return JSONResponse(get_nutrition_options())
    except FileNotFoundError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("Nutrition options error")
        raise HTTPException(status_code=500, detail=f"Nutrition options failed: {str(exc)}") from exc


@app.post("/predict-skin-disease", tags=["Prediction"])
async def predict_skin_disease(file: UploadFile = File(..., description="Cattle skin image (JPEG / PNG)")):
    """Upload a cattle skin image and receive predictions from both YOLO and ViT skin-disease models."""
    if SKIN_VIT_MODEL is None:
        raise HTTPException(status_code=503, detail="Skin disease ViT model is not loaded yet.")
    if SKIN_YOLO_MODEL is None:
        raise HTTPException(status_code=503, detail="Skin disease YOLO model is not loaded yet.")

    if file.content_type not in ("image/jpeg", "image/png", "image/jpg", "image/webp"):
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{file.content_type}'. Send JPEG or PNG."
        )

    try:
        image_bytes = await file.read()
        img = Image.open(io.BytesIO(image_bytes)).convert("RGB")

        yolo_result = None
        vit_result = None

        try:
            yolo_predictions = SKIN_YOLO_MODEL.predict(
                source=img,
                device="cuda" if DEVICE.type == "cuda" else "cpu",
                imgsz=224,
                save=False,
                verbose=False,
            )
            if yolo_predictions:
                result = yolo_predictions[0]
                probs = getattr(result, "probs", None)
                if probs is not None:
                    top1_idx = int(getattr(probs, "top1", 0))
                    top1_conf = float(getattr(probs, "top1conf", 0.0).item() if hasattr(getattr(probs, "top1conf", 0.0), "item") else getattr(probs, "top1conf", 0.0))
                    names = getattr(SKIN_YOLO_MODEL, "names", {})
                    yolo_result = {
                        "predicted_class": names.get(top1_idx, str(top1_idx)),
                        "confidence": round(top1_conf, 4),
                    }
        except Exception as e:
            logger.exception(f"Skin YOLO prediction error: {e}")
            yolo_result = {"error": str(e)}

        try:
            tensor = SKIN_VIT_TRANSFORM(img).unsqueeze(0).to(DEVICE)
            with torch.no_grad():
                logits = SKIN_VIT_MODEL(tensor)
                probs = torch.softmax(logits, dim=1)[0]
                top5_probs, top5_idx = torch.topk(probs, k=min(5, len(SKIN_CLASS_NAMES or ["class_0"])))

            vit_result = {
                "predicted_class": SKIN_CLASS_NAMES[top5_idx[0].item()] if SKIN_CLASS_NAMES else f"class_{top5_idx[0].item()}",
                "confidence": round(top5_probs[0].item(), 4),
                "top5": [
                    {
                        "class": SKIN_CLASS_NAMES[i.item()] if SKIN_CLASS_NAMES else f"class_{i.item()}",
                        "confidence": round(p.item(), 4),
                    }
                    for p, i in zip(top5_probs, top5_idx)
                ],
            }
        except Exception as e:
            logger.exception(f"Skin ViT prediction error: {e}")
            vit_result = {"error": str(e)}

        return JSONResponse(
            {
                "yolo": yolo_result,
                "vit": vit_result,
                "filename": file.filename,
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Skin disease prediction error")
        raise HTTPException(status_code=500, detail=f"Skin disease prediction failed: {str(e)}")


# ─────────────────────────────────────────────
# RAG Models
# ─────────────────────────────────────────────
class QuestionRequest(BaseModel):
    question: str


class IngestResponse(BaseModel):
    status: str
    message: str


class AnswerResponse(BaseModel):
    question: str
    answer: str
    data_ingested: bool


# ─────────────────────────────────────────────
# RAG Routes
# ─────────────────────────────────────────────
@app.post("/rag/ingest", tags=["RAG"], response_model=IngestResponse)
def ingest_documents():
    """Ingest PDF documents from Artifacts folder into vector store."""
    try:
        rag_service = get_rag_service()
        if rag_service is None:
            return IngestResponse(
                status="error",
                message="RAG service not initialized"
            )
        
        success = rag_service.ingest_data()
        if success:
            return IngestResponse(
                status="success",
                message="Documents ingested successfully"
            )
        else:
            return IngestResponse(
                status="error",
                message="Failed to ingest documents. Check if Artifacts folder exists."
            )
    except Exception as e:
        logger.error(f"Error in ingest endpoint: {str(e)}")
        return IngestResponse(
            status="error",
            message=f"Error: {str(e)}"
        )


@app.post("/rag/ask", tags=["RAG"], response_model=AnswerResponse)
def ask_question(request: QuestionRequest):
    """Ask a question based on ingested documents."""
    try:
        rag_service = get_rag_service()
        if rag_service is None:
            return AnswerResponse(
                question=request.question,
                answer="RAG service not initialized",
                data_ingested=False
            )
        
        if not rag_service.is_data_ingested():
            return AnswerResponse(
                question=request.question,
                answer="Please ingest documents first by calling /rag/ingest endpoint",
                data_ingested=False
            )
        
        answer = rag_service.answer_question(request.question)
        return AnswerResponse(
            question=request.question,
            answer=answer,
            data_ingested=True
        )
    except Exception as e:
        logger.error(f"Error in ask endpoint: {str(e)}")
        return AnswerResponse(
            question=request.question,
            answer=f"Error processing question: {str(e)}",
            data_ingested=False
        )


@app.get("/rag/status", tags=["RAG"])
def rag_status():
    """Check if RAG service is ready and data is ingested."""
    try:
        rag_service = get_rag_service()
        if rag_service is None:
            return {"status": "not_initialized"}
        
        return {
            "status": "ready",
            "data_ingested": rag_service.is_data_ingested(),
            "artifacts_path": "./Artifacts"
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.get("/breeds", tags=["Breeds"])
def get_breeds_from_db():
    """Fetch breed details from PostgreSQL database (cattle_breeds and breed_traits tables)."""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Fetch breeds
        cur.execute("SELECT id, breed_name, common_name, breed_type, origin_state, origin_country, category_badge, description, weight_min_kg, weight_max_kg, lifespan_years, milk_yield_min_lpy, milk_yield_max_lpy, image_url, created_at, updated_at FROM cattle_breeds ORDER BY breed_name ASC;")
        breeds_rows = cur.fetchall()
        
        # Fetch traits
        cur.execute("SELECT breed_id, trait FROM breed_traits;")
        traits_rows = cur.fetchall()
        
        cur.close()
        conn.close()
        
        # Group traits by breed_id
        traits_by_breed = {}
        for b_id, trait in traits_rows:
            traits_by_breed.setdefault(b_id, []).append(trait)
            
        # Map breeds
        formatted_breeds = []
        for row in breeds_rows:
            b_id = row[0]
            traits = traits_by_breed.get(b_id, [])
            formatted_breeds.append(map_breed_to_frontend(row, traits))
            
        return formatted_breeds
    except Exception as e:
        logger.error(f"Error fetching breeds from database: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error connecting to database or fetching breeds: {str(e)}"
        )


# ─────────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────────
if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=False)