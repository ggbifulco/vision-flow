from abc import ABC, abstractmethod
from src.config.settings import Settings

class BaseModel(ABC):
    def __init__(self):
        self.device = Settings.DEVICE
        self.model = None
        self.load_model()

    @abstractmethod
    def load_model(self):
        pass

    @abstractmethod
    def predict(self, input_data):
        pass
