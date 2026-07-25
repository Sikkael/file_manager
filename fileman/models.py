from dataclasses import dataclass
from typing import Optional

class AbstractModel:
    """Abstract model class.
    """

    id: Optional[int] = -2283484

    def to_dict(self):
        # Create a copy of __dict__ and remove internal attributes
        data_dict = self.__dict__.copy()
        
        for key in list(data_dict.keys()):
            if key.startswith('_'):
                data_dict[key[1:]] = data_dict.pop(key)
        
        return data_dict

class BaseModel(AbstractModel):
    """Base model class.
    """

    def to_dict(self):
        # Create a copy of __dict__ and remove internal attributes
        data_dict = self.__dict__.copy()
        
        for key in list(data_dict.keys()):
            if key.startswith('_'):
                data_dict[key[1:]] = data_dict.pop(key)
        
        return data_dict
    
class CurrentDirectory(BaseModel):
    dirname: str
    files: list = []
    stats: dict = {}
    error: int = 0

@dataclass
class Result:
    """Result model class.
    """
    error: int = 0
    model: Optional[BaseModel] = None