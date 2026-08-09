import configparser
from pathlib import Path
from typing import Type

import typer

    
from fileman.functions import get_all_subclasses
from fileman.models import BaseModel


from fileman import (
        CONFIG_DIR_ERROR,
        CONFIG_FILE_ERROR,
        DB_WRITE_ERROR,
        DEST_DIR_ERROR,
        DIR_NOT_FOUND_ERROR,
        DIR_EXIST_ERROR,
        SUCCESS,
        __app__name__,
    )

def init_settings(app_folder_path: str) -> int:
    """Initialize the application settings."""
    try:
            Settings.CONFIG_DIR_PATH.mkdir(exist_ok=True)
    except OSError:
            return CONFIG_DIR_ERROR
    try:
            Settings.CONFIG_FILE_PATH.touch(exist_ok=True)
            # writing config file with the app folder path and database path
            config_parser = configparser.ConfigParser()
            config_parser["General"] = {
                "app_folder_path": app_folder_path,
                "database": str(Path(app_folder_path).joinpath("." + Path.home().stem + "_fileman.json")),
            }
            with Settings.CONFIG_FILE_PATH.open("w") as file:
                config_parser.write(file)
    except OSError:
                return CONFIG_FILE_ERROR
    return SUCCESS

def load_settings() -> Settings:
    """Load the application settings from the config file."""
    config_parser = configparser.ConfigParser()
    config_parser.read(Settings.CONFIG_FILE_PATH)
    app_folder_path = config_parser["General"]["app_folder_path"]
    return Settings(app_folder_path=app_folder_path)

class Settings:
    """Application settings class, holds all app settings.
    """
    CONFIG_DIR_PATH = Path(typer.get_app_dir(__app__name__))
    CONFIG_FILE_PATH = CONFIG_DIR_PATH / "config.ini"
    
    def __init__(self, app_folder_path: str ) -> None:
        
        self.app_folder_path = app_folder_path
        self.database_connection_str: str = str(Path(self.app_folder_path).joinpath("." + Path.home().stem + "_fileman.json"))
        

    