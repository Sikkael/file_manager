from ast import List
from dataclasses import dataclass
from typing import Optional

class AbstractModel:
    """Abstract model class.
    """

    


class BaseModel(AbstractModel):
    """Base model class.
    """
    
    id: Optional[int] = -2283484
    
    def to_dict(self):
        # Create a copy of __dict__ and remove internal attributes
        data_dict = self.__dict__.copy()
        
        for key in list(data_dict.keys()):
            if key.startswith('_'):
                data_dict[key[1:]] = data_dict.pop(key)
        
        return data_dict


class Directory(BaseModel):
    """Directory model class.
    """
    dirpath: str
    files: list = []
    stats: dict = {}

    
class Collection(AbstractModel):
      
      def __init__(self, lst: list = []) -> None:
          self._lst = lst 

@dataclass
class Result:
    """Result model class.
    """
    error: int = 0
    model: Optional[AbstractModel] = None