"""_summary_ : This module defines the FileMetadata class, which is responsible for extracting and storing metadata information about a file. The class takes in the file path, destination path, hash value, and latest index as parameters. It provides a method to retrieve the metadata as a dictionary.

    Returns:
        _type_: _description_
"""

import os
import time
import hashlib
from typing import Dict

from fileman.hashfiles import compute_file_hash


class FileMetadata:
    def __init__(self, origin_path, file_path, _destination_path, h, _latest_index):
        self.origin_path = origin_path
        self.file_path = file_path
        self._destination_path = _destination_path
        self.h = h
        self._latest_index = _latest_index

    def get_metadata(self):
        
        f = {
            "id": self._latest_index,
            "file_path": str(self.file_path),
            "parent": str(self.origin_path),
            "size": self.file_path.stat().st_size,
            "created": time.ctime(os.path.getctime(self.file_path)),
            "modified": time.ctime(os.path.getmtime(self.file_path)),
            "hash": self.h,
            "name": self._destination_path.name,
            "destination_path": str(self._destination_path),
            "ext": self.file_path.suffix,
            "duplicates": []
        }
        return f    

class FileMetadataManager:
    def __init__(self, metadata_dict:Dict[str, Dict]={}, latest_index:int=0):
        self.metadata_dict_ = metadata_dict
        self.latest_index = latest_index

    def add_file_metadata(self,origin_path, file_path, destination_path)-> bool:
        # Hash generation
        h = compute_file_hash(file_path)  # Placeholder for actual hash generation
        
        # Check for duplicates        
        if h in self.metadata_dict_ and file_path != self.metadata_dict_[h]["file_path"] \
        and file_path != self.metadata_dict_[h]["file_path"]:
            self.metadata_dict_[h]["duplicates"].append(str(file_path))
            return False
        # Create FileMetadata instance and store metadata
        
        metadata = FileMetadata(origin_path, file_path, destination_path, h, self.latest_index)
        self.metadata_dict_[metadata.h] = metadata.get_metadata()
        self.latest_index += 1
        return True


    def get_all_metadata(self) -> Dict[str, Dict]:
        return self.metadata_dict_

