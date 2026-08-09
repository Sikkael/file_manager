from ast import List
from dataclasses import dataclass
from typing import Any, Optional

from fileman.functions import GetFileNames

class AbstractModel:
    """Abstract model class.
    """

    


class BaseModel(AbstractModel):
    """Base model class.
    """
    
    def __init__(self, id: Optional[int] = None) -> None:
        self.id = id 
    
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
    def __init__(self, id: Optional[int] = None, dirpath: str = "", files: list[str] = [], stats: dict = {}) -> None:
        super().__init__(id)
        self.dirpath = dirpath
        self.files = files
        self.stats = stats

    
class Collection(AbstractModel):
      
      def __init__(self, lst: list = []) -> None:
          self._lst = lst 

@dataclass
class Result:
    """Result model class.
    """
    error: int = 0
    model: Optional[AbstractModel] = None
    
    
def directory_builder(dirpath: str) -> Directory:
    """Build a Directory model instance."""
    if not dirpath:
        raise ValueError("Directory path cannot be empty.")
    
    files = GetFileNames(dirpath)
    
    return Directory(dirpath=dirpath, files=files, stats={})