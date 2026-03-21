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
# TODO: Ajouter une commande pour supprimer un répertoire de la base de données
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
    db_path: str = typer.Option(
        str(database.DEFAULT_DB_FILE_PATH),
        "--db-path",
        "-db",
        prompt="fileman database location?",
        help="Path to the fileman database file.",
    
    ),
    dest_path: str = typer.Option(
        config.DEFAULT_DEST_FOLDER_PATH,
        "--dest-path",
        "-dp",
        prompt="fileman destination dir location?",
        help="Path to the destination dir.",)
    
) -> None:
    """Initialize the fileman database."""
    app_init_error = config.init_app(db_path,dest_path)
    if app_init_error:
        typer.secho(
            f'App initialisation failed with "{ERRORS[app_init_error]}"',
            fg=typer.colors.RED,
        )
        raise typer.Exit(1)
    
    else:
        typer.secho(f"The fileman database is {db_path}\nThe destination path is {dest_path}", fg=typer.colors.GREEN)
        
            
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