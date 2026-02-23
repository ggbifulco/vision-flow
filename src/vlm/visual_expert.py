from transformers import AutoModelForCausalLM, AutoTokenizer
from PIL import Image
from src.core.base_model import BaseModel
from src.config.settings import Settings

class VisualExpert(BaseModel):
    def load_model(self):
        print(f"[*] Caricamento Moondream2 su {self.device}...")
        self.model = AutoModelForCausalLM.from_pretrained(
            Settings.VLM_MODEL_ID, 
            trust_remote_code=True, 
            revision=Settings.REVISION
        ).to(self.device)
        self.tokenizer = AutoTokenizer.from_pretrained(Settings.VLM_MODEL_ID, revision=Settings.REVISION)

    def predict(self, frame_pil, query="Descrivi cosa sta succedendo in questa scena."):
        # Moondream2 riceve un'immagine PIL e una stringa di testo
        answer = self.model.answer_question(frame_pil, query, self.tokenizer)
        return answer
