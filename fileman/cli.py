"""This module provides the RP fileman CLI."""
# rptodo/cli.py

import os
from pathlib import Path
from typing import Optional

import typer

from typing import List, Optional


from fileman import (DIR_ALREADY_ADDED_ERROR, ERRORS, __app__name__, __version__, config, database, fileman)

app = typer.Typer()

# TODO: Rendre la journalisaton des fichiers optionnelle lors de l'ajout d'un répertoire
# TODO: Rendre la jjournalisation plus performante (par lots)
# TODO: Rendre la journalisation plus détaillée (fichiers modifiés, ajoutés, supprimés)


def get_file_manager() -> fileman.FileManager:
    if config.CONFIG_FILE_PATH.exists():
        db_path = database.get_database_path(config.CONFIG_FILE_PATH)
        
    else:
        typer.secho(
            'Config file not found. Please, run "fileman init"',
            fg=typer.colors.RED,
        )
        raise typer.Exit(1)
    if not db_path.exists():
        typer.secho(
            'Database not found. Please, run "fileman init"',
            fg=typer.colors.RED,
        )
        raise typer.Exit(1)
        
    return fileman.FileManager(db_path)

def _version_callback(value: bool) -> None:
    if value:
        typer.echo(f"{__app__name__} v{__version__}")
        raise typer.Exit()

@app.command()
def init(
    
     app_folder_path: str = typer.Option(
        config.DEFAULT_APP_FOLDER_PATH,
        "--app-path",
        "-ap",
        prompt="fileman app dir location?",
        help="Path to the app dir.",)
    
) -> None:
    """Initialize the fileman database."""
    app_init_error = config.init_app(app_folder_path)
    if app_init_error:
        typer.secho(
            f'App initialisation failed with "{ERRORS[app_init_error]}"',
            fg=typer.colors.RED,
        )
        raise typer.Exit(1)
    
    else:
        typer.secho(f"The fileman folder location is {app_folder_path}", fg=typer.colors.GREEN)
        
            
@app.command()
def add(
         dirname: str = typer.Option( 
        "--dirname", 
        "-dir"),
      )-> None:

    """Add a new directory to the database."""
    
    file_manager = get_file_manager()
    current_directory = file_manager.add(dirname)
    
    if current_directory.error:
        typer.secho(
            f'Adding directory failed with "{ERRORS[current_directory.error]}"',
            fg=typer.colors.YELLOW if current_directory.error == DIR_ALREADY_ADDED_ERROR else typer.colors.RED,
        )
        raise typer.Exit(1)
    else:
        typer.secho(
            f'Directory "{dirname}" added successfully.',
            fg=typer.colors.GREEN,
        )
    

@app.callback()
def main(
    version: Optional[bool] = typer.Option(
        None,
        "--version",
        "-v",
        help="Show the application's version and exit.",
        callback=_version_callback,
        is_eager=True,
    )
) -> None:
    return

def print_dir_list(directories: List[str]) -> None:
    """List directories"""
    
    typer.secho("\ndirectories:\n", fg=typer.colors.BLUE, bold=True)
    columns = (
        "ID.  ",
        "| Directory path  ",
        "| Directory name ",
    )
    headers = "".join(columns)
    typer.secho(headers, fg=typer.colors.BLUE, bold=True)
    typer.secho("-" * len(headers), fg=typer.colors.BLUE)
    id = 1
    for dir in directories:
        
        typer.secho(
            f"{id}{(len(columns[0]) - len(str(id))) * ' '}"
            f"| {Path(dir).parent}{' ' * (len(columns[1]) - len(str(Path(dir).parent)))}"
            f"| {Path(dir).name} {' ' * (len(columns[1]) - len(str(Path(dir).name)))}",
            fg=typer.colors.BLUE,
        )
        id += 1
    typer.secho("-" * len(headers) + "\n", fg=typer.colors.BLUE)
    

@app.command(name="list-dir")
def list_dir() -> None:
    file_manager = get_file_manager()
    directories, result_code = file_manager.get_dir_list()
    if result_code:
        typer.secho(
            f'Directory listing failed with "{ERRORS[result_code]}"',
            fg=typer.colors.RED
        )
        raise typer.Exit()
    
    print_dir_list(directories)


@app.command(name="clear")
def clear_database() -> None:
    """Clear the database and the destination directory."""
    file_manager = get_file_manager()
    result = file_manager.clear()
    if result.error:
        typer.secho(
            f'Clearing failed with "{ERRORS[result.error]}"',
            fg=typer.colors.RED,
        )
    else:
        typer.secho("Database and destination directory cleared successfully.", fg=typer.colors.GREEN)

@app.command(name="clear-log")
def clear_log() -> None:
    """Clear the log file."""
    file_manager = get_file_manager()
    try:
        file_manager.clear_log()
    except Exception as e:
        typer.secho(
            f'Clearing log failed with "{str(e)}"',
            fg=typer.colors.RED,
        )
    else:
        typer.secho("Log file cleared successfully.", fg=typer.colors.GREEN)

@app.command(name="update-all")
def update_all() -> None:
    """Update all directories in the database."""
    file_manager = get_file_manager()
    result = file_manager.update_all()
    if result.error:
        typer.secho(
            f'Updating failed with "{ERRORS[result.error]}"',
            fg=typer.colors.RED,
        )
    else:
        typer.secho("All directories updated successfully.", fg=typer.colors.GREEN)
        
@app.command(name="update")
def update_directory(
    dir_id: int = typer.Option(
        -4678,
        "--dir-id",
        "-id",
        help="The directory id to update."
    )
) -> None:
    """Update a specific directory in the database."""
    file_manager = get_file_manager()
    directories, code = file_manager.get_dir_list()
    if code:
        typer.secho(
            f'Failed to retrieve directory list with "{ERRORS[code]}"',
            fg=typer.colors.RED,
        )
        raise typer.Exit(1)
    
    if dir_id == -4678:
        print_dir_list(directories)
        dir_id = int(typer.prompt("Directory id to update?"))
        
    if dir_id < 1:
        typer.secho(
            "Invalid directory id. Please provide a positive integer.",
            fg=typer.colors.RED,
        )
        raise typer.Exit(1)
    
    if dir_id > len(directories):
        typer.secho(
            f"Directory id {dir_id} does not exist. Please provide a valid directory id.",
            fg=typer.colors.RED,
        )
        raise typer.Exit(1)
    dirname, result_code = file_manager.update_dir_by_id(dir_id)
    if result_code:
        typer.secho(
            f'Updating failed with "{ERRORS[result_code]}"',
            fg=typer.colors.RED,
        )   
    else:
        typer.secho(f'Directory "{dirname}" updated successfully.', fg=typer.colors.GREEN)
        
        
@app.command(name="remove-dups")
def remove_duplicates() -> None:
    """Remove duplicates from the destination directory."""
    file_manager = get_file_manager()
    message,code = file_manager.remove_duplicates()
    if code:
        typer.secho(
            f'Removing duplicates failed with "{ERRORS[code]}"',
            fg=typer.colors.RED,
        )
    else:
        typer.secho(message, fg=typer.colors.GREEN)
        
@app.command(name="remove-dir")
def remove_directory(
    dir_id: int = typer.Option(
        -4679,
        "--dir-id",
        "-id",
        help="Remove files from directory with specified id in destination directory."
        "The directory will be removed from the database if the operation is successful."
    )
) -> None:
    """Remove a specific directory from the database and the files corresponding to it from the destination directory."""
    file_manager = get_file_manager()
    directories, code = file_manager.get_dir_list()
    if code:
        typer.secho(
            f'Failed to remove directory in list and files in destination directory with "{ERRORS[code]}"',
            fg=typer.colors.RED,
        )
        raise typer.Exit(1)
    
    if dir_id == -4679:
        print_dir_list(directories)
        dir_id = int(typer.prompt("Directory id to remove?"))
        
    
    dirname, result_code = file_manager.remove_dir_by_id(dir_id)
    if result_code:
        typer.secho(
            f'Removing failed with "{ERRORS[result_code]}"',
            fg=typer.colors.RED,
        )   
    else:
        typer.secho(f'Directory "{dirname}" removed successfully.', fg=typer.colors.GREEN)
        
@app.command(name="get-stats")
def get_stats() -> None:
    """Get statistics about the files in the destination directory."""
    file_manager = get_file_manager()
    stats, code = file_manager.get_stats()
    if code:
        typer.secho(
            f'Getting stats failed with "{ERRORS[code]}"',
            fg=typer.colors.RED,
        )   
    else:
        
        typer.secho(f"{stats}", fg=typer.colors.GREEN)
        
@app.command(name="get-duplicates")
def get_duplicates() -> None:
    """Get the list of duplicate files in the destination directory."""
    file_manager = get_file_manager()
    duplicates, code = file_manager.get_duplicates()
    if code:
        typer.secho(
            f'Getting duplicates failed with "{ERRORS[code]}"',
            fg=typer.colors.RED,
        )   
    else:
        if not duplicates:
            typer.secho("No duplicate files found.", fg=typer.colors.GREEN)
        else:
            typer.secho("Duplicate files:", fg=typer.colors.GREEN, bold=True)
            for dup in duplicates:
                typer.secho(dup, fg=typer.colors.GREEN)
                
@app.command(name="up-stats")
def update_stats() -> None:
    """Update the statistics about the files in the destination directory."""
    file_manager = get_file_manager()
    message, code = file_manager.update_stats()
    if code:
        typer.secho(
            f'Updating stats failed with "{ERRORS[code]}"',
            fg=typer.colors.RED,
        )   
    else:
        typer.secho(message, fg=typer.colors.GREEN)