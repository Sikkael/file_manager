"""Top-level package for RP fileman."""
# fileman/__init__.py

__app__name__ = "fileman"
__version__ = "0.1.1"

from fileman.settings import Settings


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

def create_app(config_path: str = str()) -> None:
    """Create the fileman application."""
    from fileman.config import init_app
    
    settings = Settings()
    app_init_error = init_app(config_path)
    if app_init_error:
        raise RuntimeError(f"App initialisation failed with {ERRORS[app_init_error]}")
    