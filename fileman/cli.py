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

@app.command(name="list")
def list_all() -> None:
    """List directories"""
    file_manager = get_file_manager()
    
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
        
@app.command(name="add-dir")
def add_directory(
         dirname: str = typer.Option( 
        "--dirname", 
        "-dir"),
      )-> None:     
    file_manager = get_file_manager()
    result = file_manager.add_directory(dirname)
    if result.error:
        typer.secho(
            f'Adding directory failed with "{ERRORS[result.error]}"',
            fg=typer.colors.YELLOW if result.error == DIR_ALREADY_ADDED_ERROR else typer.colors.RED,
        )
    else:
        typer.secho(
            f'Directory "{dirname}" added successfully.',
            fg=typer.colors.GREEN,
        )   