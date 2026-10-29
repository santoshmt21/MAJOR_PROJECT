import json
import os
import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import httpx
from PIL import Image
from groq import APIStatusError, APITimeoutError

from cattle_verification import CattleVerificationError, verify_cattle_image


def image_bytes() -> bytes:
    from io import BytesIO

    output = BytesIO()
    Image.new("RGB", (4, 4), "white").save(output, format="PNG")
    return output.getvalue()


def response(payload: dict) -> SimpleNamespace:
    return SimpleNamespace(
        choices=[
            SimpleNamespace(
                message=SimpleNamespace(content=json.dumps(payload))
            )
        ]
    )


class CattleVerificationTests(unittest.IsolatedAsyncioTestCase):
    async def test_accepts_cattle_above_threshold(self):
        client = SimpleNamespace(
            chat=SimpleNamespace(
                completions=SimpleNamespace(
                    create=AsyncMock(
                        return_value=response(
                            {
                                "is_cattle": True,
                                "confidence": 0.96,
                                "reason": "A real cow is clearly visible.",
                            }
                        )
                    )
                )
            ),
            close=AsyncMock(),
        )
        with patch.dict(os.environ, {"API_KEY": "test-key"}, clear=False), patch(
            "cattle_verification.AsyncGroq", return_value=client
        ):
            result = await verify_cattle_image(image_bytes(), "image/png")

        self.assertTrue(result["is_cattle"])
        client.chat.completions.create.assert_awaited_once()
        client.close.assert_awaited_once()

    async def test_rejects_non_cattle_decision(self):
        client = SimpleNamespace(
            chat=SimpleNamespace(
                completions=SimpleNamespace(
                    create=AsyncMock(
                        return_value=response(
                            {
                                "is_cattle": False,
                                "confidence": 0.99,
                                "reason": "A dog is visible.",
                            }
                        )
                    )
                )
            ),
            close=AsyncMock(),
        )
        with patch.dict(os.environ, {"API_KEY": "test-key"}, clear=False), patch(
            "cattle_verification.AsyncGroq", return_value=client
        ):
            with self.assertRaises(CattleVerificationError) as context:
                await verify_cattle_image(image_bytes(), "image/png")

        self.assertEqual(context.exception.status_code, 422)

    async def test_rejects_invalid_image_before_provider_call(self):
        client = SimpleNamespace(close=AsyncMock())
        with patch.dict(os.environ, {"API_KEY": "test-key"}, clear=False), patch(
            "cattle_verification.AsyncGroq", return_value=client
        ) as groq:
            with self.assertRaises(CattleVerificationError) as context:
                await verify_cattle_image(b"not an image", "image/png")

        self.assertEqual(context.exception.status_code, 400)
        groq.assert_not_called()

    async def test_rejects_malformed_provider_response(self):
        client = SimpleNamespace(
            chat=SimpleNamespace(
                completions=SimpleNamespace(
                    create=AsyncMock(
                        return_value=response(
                            {
                                "is_cattle": "yes",
                                "confidence": 1.2,
                                "reason": "",
                            }
                        )
                    )
                )
            ),
            close=AsyncMock(),
        )
        with patch.dict(os.environ, {"API_KEY": "test-key"}, clear=False), patch(
            "cattle_verification.AsyncGroq", return_value=client
        ):
            with self.assertRaises(CattleVerificationError) as context:
                await verify_cattle_image(image_bytes(), "image/png")

        self.assertEqual(context.exception.status_code, 502)

    async def test_fails_closed_when_api_key_is_missing(self):
        with patch.dict(os.environ, {"API_KEY": ""}, clear=False), patch(
            "cattle_verification.AsyncGroq"
        ) as groq:
            with self.assertRaises(CattleVerificationError) as context:
                await verify_cattle_image(image_bytes(), "image/png")

        self.assertEqual(context.exception.status_code, 503)
        groq.assert_not_called()

    async def test_maps_provider_timeout_to_controlled_error(self):
        client = SimpleNamespace(
            chat=SimpleNamespace(
                completions=SimpleNamespace(
                    create=AsyncMock(
                        side_effect=APITimeoutError(
                            httpx.Request("POST", "https://api.groq.com")
                        )
                    )
                )
            ),
            close=AsyncMock(),
        )
        with patch.dict(os.environ, {"API_KEY": "test-key"}, clear=False), patch(
            "cattle_verification.AsyncGroq", return_value=client
        ):
            with self.assertRaises(CattleVerificationError) as context:
                await verify_cattle_image(image_bytes(), "image/png")

        self.assertEqual(context.exception.status_code, 504)

    async def test_maps_provider_rate_limit_to_controlled_error(self):
        client = SimpleNamespace(
            chat=SimpleNamespace(
                completions=SimpleNamespace(
                    create=AsyncMock(
                        side_effect=APIStatusError(
                            "rate limited",
                            response=httpx.Response(
                                429,
                                request=httpx.Request(
                                    "POST", "https://api.groq.com"
                                ),
                            ),
                            body=None,
                        )
                    )
                )
            ),
            close=AsyncMock(),
        )
        with patch.dict(os.environ, {"API_KEY": "test-key"}, clear=False), patch(
            "cattle_verification.AsyncGroq", return_value=client
        ):
            with self.assertRaises(CattleVerificationError) as context:
                await verify_cattle_image(image_bytes(), "image/png")

        self.assertEqual(context.exception.status_code, 429)


if __name__ == "__main__":
    unittest.main()
