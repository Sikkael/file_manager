"""Top-level package for RP fileman."""
# fileman/__init__.py

__app__name__ = "fileman"
__version__ = "0.1.1"




(
    SUCCESS,
    DIR_NOT_FOUND_ERROR,
    FILE_ERROR,
    CONFIG_DIR_ERROR,
    CONFIG_FILE_ERROR,
    DB_READ_ERROR,
    DB_WRITE_ERROR,
    JSON_ERROR,
    ID_ERROR,
    DIR_EXIST_ERROR,
    DEST_DIR_ERROR,
    DIR_ALREADY_ADDED_ERROR,
    METADATA_ERROR,
    FILE_HANDLING_ERROR,
    EMPTY_DIR_LIST_ERROR,
    DIR_ID_ERROR,
) = range(16)

ERRORS = {
    DIR_NOT_FOUND_ERROR: "directory not found error",
    FILE_ERROR: "file error",
    CONFIG_DIR_ERROR: "config directory error",
    CONFIG_FILE_ERROR: "config file error",
    DB_READ_ERROR: "database read error",
    DB_WRITE_ERROR: "database write error",
    ID_ERROR: "fileman id error",
    JSON_ERROR: "json decode error",
    DIR_EXIST_ERROR: "destination directory already exist error",
    DIR_ALREADY_ADDED_ERROR: "directory already added error",
    DEST_DIR_ERROR: "destination directory error",
    METADATA_ERROR: "metadata error",
    FILE_HANDLING_ERROR: "file handling error",
    EMPTY_DIR_LIST_ERROR: "empty directory list error\nPlease add directory to list.",
    DIR_ID_ERROR: "directory id error",
}

(NEW, MOVED, DUPLICATE, ERROR) = range(4)

FILE_PROCESSING_ERRORS = (OSError, FileNotFoundError, PermissionError)

class BaseSettings:
    """Base settings class for the application."""
    
    def __init__(self, app_folder_path: str = str()) -> None:
        self.app_folder_path = app_folder_path
        
    def init_app(self) -> int:
        """Initialize the application."""
        raise NotImplementedError("Subclasses should implement this method.")
    
def create_app(settings:BaseSettings, app_folder_path: str = str()) -> None:
    """Create the fileman application."""
    
    if not app_folder_path:
        settings = BaseSettings()
    else:
        settings = BaseSettings(app_folder_path)
    
    app_init_error = settings.init_app()
    if app_init_error:
        raise RuntimeError(f"App initialisation failed with {ERRORS[app_init_error]}")
    