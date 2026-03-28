import base64
import io
import logging
from typing import Optional
from src.core.base_model import BaseModel
from src.config.settings import Settings

logger = logging.getLogger(__name__)


class VisualExpert(BaseModel):
    def load_model(self) -> None:
        self.provider: str = Settings.VLM_PROVIDER
        if self.provider == "gemini":
            from google import genai

            logger.info(
                f"Initializing Gemini VLM (Model: {Settings.GEMINI_MODEL_ID})..."
            )
            self.client = genai.Client(api_key=Settings.GEMINI_API_KEY)
            logger.info("Gemini client ready.")
        else:
            from groq import Groq

            logger.info(f"Initializing Groq VLM (Model: {Settings.VLM_MODEL_ID})...")
            self.client = Groq(api_key=Settings.GROQ_API_KEY)
            logger.info("Groq client ready.")

    def predict(
        self, frame_pil, query: str = "Describe what is happening in this scene."
    ) -> str:
        if self.provider == "gemini":
            return self._predict_gemini(frame_pil, query)
        else:
            return self._predict_groq(frame_pil, query)

    def _predict_gemini(self, frame_pil, query: str) -> str:
        try:
            response = self.client.models.generate_content(
                model=Settings.GEMINI_MODEL_ID,
                contents=[frame_pil, query],
            )
            if not response.text:
                raise ValueError("Empty response from Gemini")
            return response.text
        except Exception as e:
            logger.error(f"Gemini prediction failed: {e}")
            raise

    def _predict_groq(self, frame_pil, query: str) -> str:
        try:
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
        except Exception as e:
            logger.error(f"Groq prediction failed: {e}")
            raise

    def switch_provider(self, provider: str) -> None:
        Settings.VLM_PROVIDER = provider
        self.load_model()
        logger.info(f"VLM provider switched to: {provider}")
