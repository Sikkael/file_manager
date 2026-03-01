"""This module provides the RP fileman config functionality."""
# fileman/config.py

import configparser
from pathlib import Path

import typer

from fileman import (
    CONFIG_FILE_ERROR, DB_WRITE_ERROR, DIR_NOT_FOUND_ERROR, DIR_EXIST_ERROR, FILE_ERROR, SUCCESS, __app__name__
)

from fileman.database import init_database
from fileman.fileman import init_dest_dir

CONFIG_DIR_PATH = Path(typer.get_app_dir(__app__name__))
CONFIG_FILE_PATH = CONFIG_DIR_PATH / "config.ini"
DEFAULT_DEST_FOLDER_PATH = Path.home().joinpath(
    "." + Path.home().stem + "_fileman"
)


def init_app(db_path: str, dest_path:str) -> int:
    """Initialize the application."""
    config_code = _init_config_file()
    if config_code != SUCCESS:
        return config_code
    ressource_code = _create_ressource(db_path,dest_path)
    
    if ressource_code != SUCCESS:
        return ressource_code
    
    return SUCCESS

def _init_config_file() -> int:
    try:
        CONFIG_DIR_PATH.mkdir(exist_ok=True)
    except OSError:
        return DIR_NOT_FOUND_ERROR
    try:
        CONFIG_FILE_PATH.touch(exist_ok=True)
    except OSError:
        return FILE_ERROR
    return SUCCESS

def _create_ressource(db_path: str, dest_path:str) -> int:
   
    if init_database(Path(db_path)) != SUCCESS:
            return DB_WRITE_ERROR
    if init_dest_dir(Path(dest_path)) != SUCCESS:
        return DIR_EXIST_ERROR
        
    config_parser = configparser.ConfigParser()
    config_parser["General"] = {
                                  "database": db_path, 
                                  "dest_directory": dest_path,                            
            
                              }
    try:
        with CONFIG_FILE_PATH.open("w") as file:
            config_parser.write(file)    
    except OSError:
        return CONFIG_FILE_ERROR
    return SUCCESS

def _create_dest_dir(dest_path: Path) -> int:
    """Initialize the destination directory."""
    dest_folfer = dest_path.joinpath(str(dest_path)+ "._fileman")
    if dest_folfer.exists():
       return DIR_EXIST_ERROR
    config_parser = configparser.ConfigParser()
    config_parser["General"]["dest_directory"]  = str(dest_folfer)                                
    try:
        Path(dest_path).mkdir(parents=True, exist_ok=True)
        with CONFIG_FILE_PATH.open("w") as file:
            config_parser.write(file)
        return SUCCESS
    except OSError:
        return DIR_EXIST_ERROR
