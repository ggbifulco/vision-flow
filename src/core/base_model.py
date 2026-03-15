from abc import ABC, abstractmethod


class BaseModel(ABC):
    def __init__(self):
        self.model = None
        self.load_model()

    @abstractmethod
    def load_model(self):
        pass

    @abstractmethod
    def predict(self, input_data):
        pass
