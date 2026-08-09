
import os


def get_all_subclasses(cls)-> dict:
    """Recursively fetches all subclasses of a given class."""
    subclasses = dict()
       
    for subclass in cls.__subclasses__():
           subclasses[subclass.__name__] = {}
           subclasses.update(get_all_subclasses(subclass))
    return subclasses


def GetFileNames(_path: str) -> list:
    """_summary_
    From : https://stackoverflow.com/questions/3207219/how-do-i-list-all-files-of-a-directory
    Args:
        _path (_type_): string: path to the directory to search for files

    Returns:
        _type_: list: list of filepaths found in the directory and its subdirectories
    """
    filepaths = []
    for root,_,files in os.walk(_path):
        if len(files) > 0:
            for file in files:
                filepaths.append(os.path.join(root,file))
    return filepaths
