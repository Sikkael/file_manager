from abc import ABC, abstractmethod
from fileman.abstract_model import AbstractModel
from typing import Any


class AbstractRepository(ABC):
    
    @abstractmethod
    def add(self, model: AbstractModel)->AbstractModel:
        raise NotImplementedError("Subclasses must implement this method.")

    @abstractmethod
    def get(self, item_id: Any) -> AbstractModel:
        raise NotImplementedError("Subclasses must implement this method.")
    
    @abstractmethod
    def update(self, item: AbstractModel)->AbstractModel:
        raise NotImplementedError("Subclasses must implement this method.")
    
    @abstractmethod
    def delete(self, item: AbstractModel)->bool:
        raise NotImplementedError("Subclasses must implement this method.")
    