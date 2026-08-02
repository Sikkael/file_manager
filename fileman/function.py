
def get_all_subclasses(cls)-> dict:
    """Recursively fetches all subclasses of a given class."""
    subclasses = dict()
       
    for subclass in cls.__subclasses__():
           subclasses[subclass.__name__] = {}
           subclasses.update(get_all_subclasses(subclass))
    return subclasses