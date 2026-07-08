from typing import Optional


class BaseModel:
    """Base model class.
    """

    id: Optional[str] = None

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


