


from dataclasses import asdict
import sys
from typing import Counter, Dict, List

_blank_file_stats = {
    "total_files": 0, 
    "total_size": 0, 
    "biggest_file":"",
    "biggest_file_size":-sys.maxsize,
    "smallest_file":"",
    "smallest_file_size":sys.maxsize,
    "average_file_size":0,
    "exts": {},
    "oldest_file":"",
    "oldest_file_date":"Mon Feb  8 03:44:42 2100",
    "newest_file":"",
    "newest_file_date":"Mon Feb 3 03:44:42 1902",
    "duplicate_files_count":0,
    "highest_file_duplication_count":0,
    "most_duplicated_file":""

    }


class FilesStats:
    
    def __init__(self, total_files: int = 0, total_size: int = 0, biggest_file:str = "", biggest_file_size:int =-sys.maxsize,
                 smallest_file:str = "", smallest_file_size:int = sys.maxsize,average_file_size:int = 0, oldest_file:str = "", 
                 oldest_file_date:str = "Mon Feb  8 03:44:42 2100", newest_file:str = "", 
                 newest_file_date:str = "Mon Feb 3 03:44:42 1902", duplicate_files_count:int = 0, highest_file_duplication_count:int = 0, most_duplicated_file:str = "",
                 exts:Dict[str,int]={}) -> None:
        self._total_files = total_files
        self._total_size = total_size
        self._biggest_file = biggest_file
        self._biggest_file_size = biggest_file_size
        self._smallest_file = smallest_file
        self._smallest_file_size = smallest_file_size
        self._average_file_size = average_file_size
        self._oldest_file = oldest_file
        self._oldest_file_date = oldest_file_date
        self._newest_file = newest_file
        self._newest_file_date = newest_file_date
        self._duplicate_files_count = duplicate_files_count
        self._highest_file_duplication_count = highest_file_duplication_count
        self._most_duplicated_file = most_duplicated_file
        # list of files extensions found and their numbers
        self._exts = exts
        
        
    def to_dict(self):
        # Create a copy of __dict__ and remove internal attributes
        data_dict = self.__dict__.copy()
        
        for key in list(data_dict.keys()):
            if key.startswith('_'):
                data_dict[key[1:]] = data_dict.pop(key)
        
        return data_dict
    
    @property
    def total_files(self):
        return self._total_files
    
    @total_files.setter
    def total_files(self, value):
        if not isinstance(value, int):
            raise ValueError("total_files must be an integer")
        self._total_files = value
        
    @property
    def total_size(self):
        return self._total_size
    
    @total_size.setter
    def total_size(self, value):
        if not isinstance(value, int):
            raise ValueError("total_size must be an integer")
        self._total_size = value
        
    @property
    def biggest_file(self):
        return self._biggest_file
    
    @biggest_file.setter
    def biggest_file(self, value):
        if not isinstance(value, str):
            raise ValueError("biggest_file must be a string")
        self._biggest_file = value
    
    @property
    def biggest_file_size(self):
        return self._biggest_file_size
    
    @biggest_file_size.setter
    def biggest_file_size(self, value):
        if not isinstance(value, int):
            raise ValueError("biggest_file_size must be an integer")
        self._biggest_file_size = value
        
    @property   
    def smallest_file(self):
        return self._smallest_file
    
    @smallest_file.setter
    def smallest_file(self, value):
        if not isinstance(value, str):
            raise ValueError("smallest_file must be a string")
        self._smallest_file = value
        
    @property
    def smallest_file_size(self):
        return self._smallest_file_size
    
    @smallest_file_size.setter
    def smallest_file_size(self, value):
        if not isinstance(value, int):
            raise ValueError("smallest_file_size must be an integer")
        self._smallest_file_size = value  
        
    @property
    def average_file_size(self):
        return self._average_file_size
    
    @average_file_size.setter
    def average_file_size(self, value):
        if not isinstance(value, int):
            raise ValueError("average_file_size must be an integer")
        self._average_file_size = value
        
    @property
    def oldest_file(self):
        return self._oldest_file
    
    @oldest_file.setter
    def oldest_file(self, value):
        if not isinstance(value, str):
            raise ValueError("oldest_file must be a string")
        self._oldest_file = value
        
    @property
    def oldest_file_date(self):
        return self._oldest_file_date
    
    @oldest_file_date.setter
    def oldest_file_date(self, value):
        if not isinstance(value, str):
            raise ValueError("oldest_file_date must be a string")
        self._oldest_file_date = value
        
    @property
    def newest_file(self):
        return self._newest_file
    
    @newest_file.setter
    def newest_file(self, value):
        if not isinstance(value, str):
            raise ValueError("newest_file must be a string")
        self._newest_file = value
        
    @property
    def newest_file_date(self):
        return self._newest_file_date
    
    @newest_file_date.setter
    def newest_file_date(self, value):
        if not isinstance(value, str):
            raise ValueError("newest_file_date must be a string")
        self._newest_file_date = value
        
    @property
    def duplicate_files_count(self):
        return self._duplicate_files_count
    
    @duplicate_files_count.setter
    def duplicate_files_count(self, value):
        if not isinstance(value, int):
            raise ValueError("duplicate_files_count must be an integer")
        self._duplicate_files_count = value
        
    @property
    def highest_file_duplication_count(self):
        return self._highest_file_duplication_count
    
    @highest_file_duplication_count.setter
    def highest_file_duplication_count(self, value):
        if not isinstance(value, int):
            raise ValueError("highest_file_duplication_count must be an integer")
        self._highest_file_duplication_count = value
        
    @property
    def most_duplicated_file(self):
        return self._most_duplicated_file

    @most_duplicated_file.setter
    def most_duplicated_file(self, value):
        if not isinstance(value, str):
            raise ValueError("most_duplicated_file must be a string")
        self._most_duplicated_file = value

    @property
    def exts(self) -> Dict[str,int]:
        return self._exts
    
    @exts.setter
    def exts(self, value: Dict[str,int]):
        if not isinstance(value, dict):
            raise ValueError("exts must be a dictionary")
        self._exts = value
        
class StatsManager:
    def __init__(self, files_metadata: Dict[str, Dict], directories: List[str]) -> None:
        self._files_metadata = files_metadata
        self._directories = directories
        self._files_stats = FilesStats()
        
        
    def refresh_stats(self) -> None:
        self._set_total_files()
        self._set_total_size()
        self._set_biggest_file()
        self._set_smallest_file()
        self._set_average_file_size()
        self._set_oldest_file()
        self._set_newest_file()
        self._set_duplicate_files_count()
        self._set_highest_file_duplication_count()
        self._set_most_duplicated_file()
        self._set_exts()
        return self._files_stats
    
    def get_stats(self) -> FilesStats:
        return self._files_stats
        
    def _set_total_files(self) -> None:
        self._files_stats.total_files = len(self._files_metadata)
        
    def _set_total_size(self) -> None:
        self._files_stats.total_size = sum([self._files_metadata[k]["size"] 
                                        for k in self._files_metadata.keys()])
    def _set_biggest_file(self) -> None:
        _biggest_file_key_ = max(self._files_metadata.keys(), key=lambda k: self._files_metadata[k]["size"]) if self._files_metadata else ""
        self._files_stats.biggest_file = self._files_metadata[_biggest_file_key_]["file_path"] if _biggest_file_key_ else ""
        self._files_stats.biggest_file_size = self._files_metadata[_biggest_file_key_]["size"] if _biggest_file_key_ else 0
    
    def _set_smallest_file(self) -> None:    
        _smallest_file_key_ = min(self._files_metadata.keys(), key=lambda k: self._files_metadata[k]["size"]) if self._files_metadata else ""
        self._files_stats.smallest_file = self._files_metadata[_smallest_file_key_]["file_path"] if _smallest_file_key_ else ""
        self._files_stats.smallest_file_size = self._files_metadata[_smallest_file_key_]["size"] if _smallest_file_key_ else 0  
   
    def _set_average_file_size(self) -> None:
         self._files_stats.average_file_size = self._files_stats.total_size // self._files_stats.total_files if self._files_stats.total_files > 0 else 0
   
    def _set_oldest_file(self) -> None:
        _oldest_file_key_ = min(self._files_metadata.keys(), key=lambda k: self._files_metadata[k]["created"]) if self._files_metadata else ""
        self._files_stats.oldest_file = self._files_metadata[_oldest_file_key_]["file_path"] if _oldest_file_key_ else ""
        self._files_stats.oldest_file_date = self._files_metadata[_oldest_file_key_]["created"] if _oldest_file_key_ else "Mon Feb  8 03:44:42 2100"
   
    def _set_newest_file(self) -> None:        
        _newest_file_key_ = max(self._files_metadata.keys(), key=lambda k: self._files_metadata[k]["created"]) if self._files_metadata else ""
        self._files_stats.newest_file = self._files_metadata[_newest_file_key_]["file_path"] if _newest_file_key_ else ""
        self._files_stats.newest_file_date = self._files_metadata[_newest_file_key_]["created"] if _newest_file_key_ else "Mon Feb 3 03:44:42 1902"        
        
    def _set_duplicate_files_count(self) -> None:
        self._files_stats.duplicate_files_count = sum([len(self._files_metadata[k]["duplicates"]) for k in self._files_metadata.keys()])
        
    def _set_highest_file_duplication_count(self) -> None:
        self._files_stats.highest_file_duplication_count = max([len(self._files_metadata[k]["duplicates"]) for k in self._files_metadata.keys()]) if self._files_metadata else 0    
    
    def _set_most_duplicated_file(self) -> None:
        self._files_stats.most_duplicated_file = self._files_metadata[max(self._files_metadata.keys(), key=lambda k: len(self._files_metadata[k]["duplicates"]))]["file_path"] if self._files_metadata else ""
            
    def _set_exts(self) -> None:
        self._files_stats.exts = dict(Counter({k:self._files_metadata[k]["ext"] for k in self._files_metadata}.values()))  