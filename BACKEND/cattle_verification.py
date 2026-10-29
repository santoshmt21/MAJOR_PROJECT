import base64
import io
import json
import logging
import math
import os
from typing import Any

from groq import APIConnectionError, APIStatusError, APITimeoutError, AsyncGroq
from PIL import Image, UnidentifiedImageError


logger = logging.getLogger(__name__)

SUPPORTED_CONTENT_TYPES = {
    "image/jpeg": "image/jpeg",
    "image/jpg": "image/jpeg",
    "image/png": "image/png",
    "image/webp": "image/webp",
}
SUPPORTED_PIL_FORMATS = {"JPEG", "PNG", "WEBP"}
DEFAULT_MAX_IMAGE_BYTES = 10 * 1024 * 1024
DEFAULT_ACCEPTANCE_THRESHOLD = 0.75
DEFAULT_TIMEOUT_SECONDS = 20.0
VERIFICATION_MODEL = "qwen/qwen3.8-27b"
REJECTION_MESSAGE = (
    "This image does not appear to contain cattle. Please upload a clear photo "
    "of a cow, bull, ox, or calf."
)


class CattleVerificationError(Exception):
    """Controlled error raised when an upload cannot be verified safely."""

    def __init__(self, status_code: int, detail: str):
        super().__init__(detail)
        self.status_code = status_code
        self.detail = detail


def _configured_float(name: str, default: float, minimum: float, maximum: float) -> float:
    value = os.getenv(name)
    if value is None:
        return default
    try:
        parsed = float(value)
    except ValueError:
        logger.warning("Ignoring invalid %s configuration.", name)
        return default
    if not minimum <= parsed <= maximum:
        logger.warning("Ignoring out-of-range %s configuration.", name)
        return default
    return parsed


def _configured_max_bytes() -> int:
    value = os.getenv("CATTLE_VERIFICATION_MAX_IMAGE_BYTES")
    if value is None:
        return DEFAULT_MAX_IMAGE_BYTES
    try:
        parsed = int(value)
    except ValueError:
        logger.warning("Ignoring invalid CATTLE_VERIFICATION_MAX_IMAGE_BYTES configuration.")
        return DEFAULT_MAX_IMAGE_BYTES
    if parsed <= 0:
        logger.warning("Ignoring non-positive CATTLE_VERIFICATION_MAX_IMAGE_BYTES configuration.")
        return DEFAULT_MAX_IMAGE_BYTES
    return parsed


def _validate_image(image_bytes: bytes, content_type: str | None) -> str:
    if content_type not in SUPPORTED_CONTENT_TYPES:
        raise CattleVerificationError(
            400,
            f"Unsupported file type '{content_type}'. Send JPEG, PNG, or WebP.",
        )
    if not image_bytes:
        raise CattleVerificationError(400, "The uploaded image is empty.")
    if len(image_bytes) > _configured_max_bytes():
        raise CattleVerificationError(
            413,
            "The image is too large. Please upload an image smaller than 10 MB.",
        )

    try:
        with Image.open(io.BytesIO(image_bytes)) as image:
            image.verify()
            image_format = image.format
    except (UnidentifiedImageError, OSError):
        raise CattleVerificationError(
            400,
            "The uploaded file is not a valid supported image.",
        ) from None

    if image_format not in SUPPORTED_PIL_FORMATS:
        raise CattleVerificationError(
            400,
            "The uploaded file is not a valid JPEG, PNG, or WebP image.",
        )
    return SUPPORTED_CONTENT_TYPES[content_type]


def _parse_verification_response(response: Any) -> dict[str, Any]:
    try:
        content = response.choices[0].message.content
    except (AttributeError, IndexError, TypeError) as exc:
        raise CattleVerificationError(502, "The cattle verification response was invalid.") from exc

    if not isinstance(content, str):
        raise CattleVerificationError(502, "The cattle verification response was invalid.")

    try:
        result = json.loads(content)
    except json.JSONDecodeError as exc:
        raise CattleVerificationError(502, "The cattle verification response was not valid JSON.") from exc

    if not isinstance(result, dict):
        raise CattleVerificationError(502, "The cattle verification response was invalid.")

    is_cattle = result.get("is_cattle")
    confidence = result.get("confidence")
    reason = result.get("reason")
    if type(is_cattle) is not bool:
        raise CattleVerificationError(502, "The cattle verification response was missing a valid decision.")
    if isinstance(confidence, bool) or not isinstance(confidence, (int, float)):
        raise CattleVerificationError(502, "The cattle verification response had an invalid confidence.")
    if not math.isfinite(float(confidence)) or not 0 <= float(confidence) <= 1:
        raise CattleVerificationError(502, "The cattle verification response had an invalid confidence.")
    if not isinstance(reason, str) or not reason.strip() or len(reason) > 500:
        raise CattleVerificationError(502, "The cattle verification response had an invalid reason.")

    return {
        "is_cattle": is_cattle,
        "confidence": float(confidence),
        "reason": reason.strip(),
    }


async def verify_cattle_image(
    image_bytes: bytes,
    content_type: str | None,
) -> dict[str, Any]:
    """Verify an image with Groq before it reaches any local prediction model."""
    mime_type = _validate_image(image_bytes, content_type)
    api_key = os.getenv("API_KEY")
    if not api_key:
        raise CattleVerificationError(
            503,
            "Cattle image verification is not configured. Please try again later.",
        )

    image_data_url = (
        f"data:{mime_type};base64,"
        f"{base64.b64encode(image_bytes).decode('ascii')}"
    )
    timeout = _configured_float(
        "CATTLE_VERIFICATION_TIMEOUT_SECONDS",
        DEFAULT_TIMEOUT_SECONDS,
        1.0,
        60.0,
    )
    threshold = _configured_float(
        "CATTLE_VERIFICATION_THRESHOLD",
        DEFAULT_ACCEPTANCE_THRESHOLD,
        0.0,
        1.0,
    )
    client = AsyncGroq(api_key=api_key, timeout=timeout)

    try:
        response = await client.chat.completions.create(
            model=VERIFICATION_MODEL,
            temperature=0,
            response_format={"type": "json_object"},
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": (
                                "Determine whether this image visibly contains at least one real "
                                "cattle animal: cow, bull, ox, or calf. Do not classify people, "
                                "dogs, buffaloes, goats, sheep, horses, vehicles, landscapes, "
                                "drawings, toys, or unrelated objects as cattle. If the image is "
                                "ambiguous, obscured, blurry, or lacks enough evidence, reject it. "
                                "Return only JSON with exactly these fields: is_cattle (boolean), "
                                "confidence (number from 0 to 1, representing your reported "
                                "confidence and not a calibrated probability), and reason "
                                "(short string)."
                            ),
                        },
                        {
                            "type": "image_url",
                            "image_url": {"url": image_data_url},
                        },
                    ],
                }
            ],
        )
    except APITimeoutError as exc:
        raise CattleVerificationError(
            504,
            "Cattle image verification timed out. Please try again.",
        ) from exc
    except APIStatusError as exc:
        if exc.status_code == 429:
            raise CattleVerificationError(
                429,
                "Cattle image verification is temporarily rate-limited. Please try again later.",
            ) from exc
        logger.warning("Groq cattle verification returned status %s.", exc.status_code)
        raise CattleVerificationError(
            502,
            "Cattle image verification is temporarily unavailable. Please try again later.",
        ) from exc
    except APIConnectionError as exc:
        raise CattleVerificationError(
            502,
            "Cattle image verification is temporarily unavailable. Please try again later.",
        ) from exc
    except Exception as exc:
        logger.exception("Unexpected cattle verification provider error.")
        raise CattleVerificationError(
            502,
            "Cattle image verification failed. Please try again later.",
        ) from exc
    finally:
        await client.close()

    verification = _parse_verification_response(response)
    if not verification["is_cattle"] or verification["confidence"] < threshold:
        raise CattleVerificationError(422, REJECTION_MESSAGE)
    return verification
