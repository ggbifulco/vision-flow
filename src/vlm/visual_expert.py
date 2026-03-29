import base64
import io
import logging
from typing import Optional

from src.core.base_model import BaseModel
from src.core.circuit_breaker import CircuitBreaker
from src.config.settings import Settings

logger = logging.getLogger(__name__)

_vlm_circuit = CircuitBreaker(failure_threshold=5, recovery_timeout=60.0)


def get_vlm_circuit() -> CircuitBreaker:
    return _vlm_circuit


class VisualExpert(BaseModel):
    def load_model(self) -> None:
        self.provider: str = Settings.VLM_PROVIDER
        if self.provider == "gemini":
            from google import genai

            logger.info(f"Initializing Gemini VLM (Model: {Settings.GEMINI_MODEL_ID})...")
            self.client = genai.Client(api_key=Settings.GEMINI_API_KEY)
            logger.info("Gemini client ready.")
        else:
            from groq import Groq

            logger.info(f"Initializing Groq VLM (Model: {Settings.VLM_MODEL_ID})...")
            self.client = Groq(api_key=Settings.GROQ_API_KEY)
            logger.info("Groq client ready.")

    def predict(self, frame_pil, query: str = "Describe what is happening in this scene.") -> str:
        if not _vlm_circuit.can_execute():
            raise RuntimeError("VLM circuit breaker is open — service temporarily unavailable")
        try:
            if self.provider == "gemini":
                result = self._predict_gemini(frame_pil, query)
            else:
                result = self._predict_groq(frame_pil, query)
            _vlm_circuit.record_success()
            return result
        except Exception:
            _vlm_circuit.record_failure()
            raise

    def _predict_gemini(self, frame_pil, query: str) -> str:
        response = self.client.models.generate_content(
            model=Settings.GEMINI_MODEL_ID,
            contents=[frame_pil, query],
        )
        if not response.text:
            raise ValueError("Empty response from Gemini")
        return response.text

    def _predict_groq(self, frame_pil, query: str) -> str:
        buf = io.BytesIO()
        frame_pil.save(buf, format="JPEG")
        base64_image = base64.b64encode(buf.getvalue()).decode("utf-8")

        response = self.client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": query},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}",
                            },
                        },
                    ],
                }
            ],
            model=Settings.VLM_MODEL_ID,
            max_tokens=512,
        )

        if not response.choices or not response.choices[0].message.content:
            raise ValueError("Empty response from Groq")
        return response.choices[0].message.content

    def switch_provider(self, provider: str) -> None:
        Settings.VLM_PROVIDER = provider
        self.load_model()
        logger.info(f"VLM provider switched to: {provider}")
