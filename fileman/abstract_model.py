from abc import ABC, abstractmethod
class AbstractModel:
    """Abstract model for the fileman application."""
    
    @abstractmethod
    def __init__(self) -> None:
        pass
    
    