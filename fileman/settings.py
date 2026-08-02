import configparser
from pathlib import Path
from typing import Type

import typer

from fileman import (
    CONFIG_FILE_ERROR, DB_WRITE_ERROR, DEST_DIR_ERROR, DIR_NOT_FOUND_ERROR, DIR_EXIST_ERROR, FILE_ERROR, SUCCESS, BaseSettings, __app__name__
)
from fileman.function import get_all_subclasses
from fileman.models import BaseModel


class Settings(BaseSettings):
    """Application settings class, holds all app settings.
    """
    CONFIG_DIR_PATH = Path(typer.get_app_dir(__app__name__))
    CONFIG_FILE_PATH = CONFIG_DIR_PATH / "config.ini"
    DEFAULT_APP_FOLDER_PATH = Path.home().joinpath(
    "." + Path.home().stem + "_fileman"
   )

    DEFAULT_DB_CONNECTION_STR = DEFAULT_APP_FOLDER_PATH.joinpath("." + Path.home().stem + "_fileman.json")
    
    def __init__(self, app_folder_path: str = str(DEFAULT_APP_FOLDER_PATH)) -> None:
        
        self.app_folder_path = app_folder_path
        self.database_connection_str: str = str(Path(self.app_folder_path).joinpath("." + Path.home().stem + "_fileman.json"))
        
        
    def init_app(self) -> int:
        """Initialize the application."""
        init_code = self._init_config_file()
        if init_code != SUCCESS:
           self.CONFIG_DIR_PATH.rmdir()  # Remove the config directory if config file creation failed
           return init_code
        folder_code = self.init_app_folder()
        if folder_code != SUCCESS:
            return DEST_DIR_ERROR
        db_code = self._init_db(BaseModel)
        if db_code != SUCCESS:
            return db_code
        return SUCCESS
    
    def _init_config_file(self) -> int:
        try:
            self.CONFIG_DIR_PATH.mkdir(exist_ok=True)
        except OSError:
            return DIR_NOT_FOUND_ERROR

        try:
            self.CONFIG_FILE_PATH.touch(exist_ok=True)

            # writing config file with the app folder path and database path
            config_parser = configparser.ConfigParser()
            config_parser["General"] = {
                "app_folder_path": self.app_folder_path,
                "database": self.database_connection_str,
            }
            with self.CONFIG_FILE_PATH.open("w") as file:
                config_parser.write(file)
        except OSError:
            return CONFIG_FILE_ERROR
        return SUCCESS
    
    def init_app_folder(self) -> int:
        """Initialize the application folder."""
        if Path(self.app_folder_path).exists():
            return DIR_EXIST_ERROR
        try:
            Path(self.app_folder_path).mkdir(parents=True, exist_ok=True)
            return SUCCESS
        except OSError:
            return DEST_DIR_ERROR
        
    def _init_db(self, base_type: Type) -> int:
        """Initialize the database."""
        db_path = Path(self.database_connection_str)
        try:
            db_path.touch(exist_ok=True)
            _d_ = get_all_subclasses(cls=base_type)
            with db_path.open("w") as db:
                db.write(base_type().to_json())
            
            return SUCCESS
        except OSError:
            return DB_WRITE_ERROR

    