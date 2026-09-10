from pathlib import Path
from typing import Any

import joblib
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
MODEL_DIR = BASE_DIR / "MODELS" / "NUTRITION_RECOMENDATION_MODEL"
MODEL_PATH = MODEL_DIR / "cattle_nutrition_tree.pkl"
ENCODERS_PATH = MODEL_DIR / "label_encoders.pkl"
FEATURE_COLUMNS = [
    "Breed", "Category", "Weight_kg", "Age_months",
    "Milk_L_per_day", "BCS", "Activity_Level", "Health_Status",
]
TARGET_COLUMNS = [
    "DMI_kg_per_day", "CrudeProtein_pct_DM", "TDN_pct_DM",
    "Calcium_g_per_day", "Phosphorus_g_per_day", "Water_L_per_day",
]
HEALTH_NOTES = {
    "Normal": "Maintain standard balanced ration; ensure clean water and routine mineral mixture.",
    "FMD": "Offer soft/gruel feed split into more frequent small meals; add electrolytes and energy-dense concentrate; isolate animal; consult vet.",
    "Lumpy Skin Disease": "Increase protein and add Vitamin A, D, E and zinc; offer soft palatable feed; isolate from herd; ensure vector control.",
    "Ringworm": "Add biotin, zinc and Vitamin A/E; maintain hygiene; mild protein boost aids skin recovery; topical antifungal as advised by vet.",
}

_MODEL = None
_ENCODERS = None


def load_nutrition_recommendation_model() -> tuple[Any, dict]:
    global _MODEL, _ENCODERS
    if _MODEL is None or _ENCODERS is None:
        if not MODEL_PATH.exists():
            raise FileNotFoundError(f"Nutrition model not found at {MODEL_PATH}")
        if not ENCODERS_PATH.exists():
            raise FileNotFoundError(f"Nutrition label encoders not found at {ENCODERS_PATH}")
        _MODEL = joblib.load(MODEL_PATH)
        _ENCODERS = joblib.load(ENCODERS_PATH)
    return _MODEL, _ENCODERS


def get_nutrition_options() -> dict[str, list[str]]:
    _, encoders = load_nutrition_recommendation_model()
    return {name: encoder.classes_.tolist() for name, encoder in encoders.items()}


def get_recommendation(
    breed: str,
    category: str,
    weight: float,
    age: float,
    milk: float,
    bcs: float,
    activity: str,
    health: str,
) -> dict[str, float | str]:
    model, encoders = load_nutrition_recommendation_model()
    values = {
        "Breed": breed,
        "Category": category,
        "Weight_kg": weight,
        "Age_months": age,
        "Milk_L_per_day": milk,
        "BCS": bcs,
        "Activity_Level": activity,
        "Health_Status": health,
    }
    encoded = dict(values)
    for column in ("Breed", "Category", "Activity_Level", "Health_Status"):
        encoder = encoders[column]
        if values[column] not in encoder.classes_:
            choices = ", ".join(encoder.classes_)
            raise ValueError(f"Invalid {column}: {values[column]}. Expected one of: {choices}")
        encoded[column] = int(encoder.transform([values[column]])[0])

    prediction = model.predict(pd.DataFrame([encoded], columns=FEATURE_COLUMNS))[0]
    result = dict(zip(TARGET_COLUMNS, [round(float(value), 2) for value in prediction]))
    result["Special_Care_Notes"] = HEALTH_NOTES.get(health, "")
    return result
