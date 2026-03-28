from abc import ABC, abstractmethod
from typing import Any


class BaseModel(ABC):
    def __init__(self) -> None:
        self.model: Any = None
        self.load_model()

    @abstractmethod
    def load_model(self) -> None:
        pass

    @abstractmethod
    def predict(self, input_data: Any) -> Any:
        pass
