

class AbstractRepository:
    
    def add(self, model):
        raise NotImplementedError("Subclasses must implement this method.")
    
    def get(self):
        raise NotImplementedError("Subclasses must implement this method.")
    
    def update(self, item):
        raise NotImplementedError("Subclasses must implement this method.")
    
    def delete(self, item):
        raise NotImplementedError("Subclasses must implement this method.")
    