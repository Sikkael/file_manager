"""This module provides the RP fileman CLI."""
# rptodo/cli.py

import os
from pathlib import Path
from typing import Optional

import typer

from typing import List, Optional


from fileman import (ERRORS, __app__name__, __version__, config, database, filehandler, fileman)

app = typer.Typer()

# TODO: Rendre la journalisaton des fichiers optionnelle lors de l'ajout d'un répertoire
# TODO: Ajouter une commande pour supprimer un répertoire de la base de données
# TODO: Rendre la jjournalisation plus performante (par lots)
# TODO: Rendre la journalisation plus détaillée (fichiers modifiés, ajoutés, supprimés)

@app.command()
def init(
    db_path: str = typer.Option(
        str(database.DEFAULT_DB_FILE_PATH),
        "--db-path",
        "-db",
        prompt="fileman database location?",
        help="Path to the fileman database file.",
    )
    
) -> None:
    """Initialize the fileman database."""
    app_init_error = config.init_app(db_path)
    if app_init_error:
        typer.secho(
            f'App initialisation failed with "{ERRORS[app_init_error]}"',
            fg=typer.colors.RED,
        )
        raise typer.Exit(1)
    
    else:
        typer.secho(f"The fileman database is {db_path}", fg=typer.colors.GREEN)
        
@app.command(name="set-dest")
def set_dest(
    dest_path: str = typer.Option(
        ..., 
        "--dest-path",
        "-dp",
        help="Path to the destination folder.",
    )
) -> None:
    """Set the destination folder."""
    file_manager = get_file_manager()
    dest_dit_init = file_manager.init_dest_dir(Path(dest_path))
    
    if dest_dit_init.error:
        typer.secho(
            f'Setting destination folder failed with "{ERRORS[dest_dit_init.error]}"',
            fg=typer.colors.RED,
        )
        raise typer.Exit(1)
    else:
        typer.secho(
            f'Destination folder set to "{dest_path}" successfully.',
            fg=typer.colors.GREEN,
        )
            
@app.command()
def add(
         dirname: str = typer.Option( 
        "--dirname", 
        "-dir"),
         not_found_ok:bool = typer.Option(
        False,
        "--not-found-ok",
        "-nfo",
        help="If the directory does not exist, do not raise an error.",
    ),
        update_now:bool = typer.Option(
        True,
        "--update-now",
        "-upn",
        help="Add all files infos to destination folder.",
    ),
      )-> None:
    """Add a new directory to the database."""
    file_manager = get_file_manager()
    current_directory = file_manager.add(dirname, not_found_ok)
    if current_directory.error:
        typer.secho(
            f'Adding directory failed with "{ERRORS[current_directory.error]}"',
            fg=typer.colors.RED,
        )
        raise typer.Exit(1)
    else:
        typer.secho(
            f'Directory "{dirname}" added successfully.',
            fg=typer.colors.GREEN,
        )
    if update_now:
        file_manager.update_files(Path(dirname))
        typer.secho(
            f'Files information in destination folder updated successfully.',
            fg=typer.colors.GREEN,
        )

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
    dir_list = file_manager.get_dir_list()
    if len(dir_list) == 0:
        typer.secho(
            "There are no dir list yet", fg=typer.colors.RED
        )
        raise typer.Exit()
    typer.secho("\ndir list:\n", fg=typer.colors.BLUE, bold=True)
    columns = (
        "ID.  ",
        "| Directory Name |",
     
    )
    headers = "".join(columns)
    typer.secho(headers, fg=typer.colors.BLUE, bold=True)
    typer.secho("-" * len(headers)+ "\n", fg=typer.colors.BLUE)
    id = -1
    for dirname in dir_list:
        id+=1
        typer.secho(
            f"{id+1}. | {dirname} |",
            fg=typer.colors.BLUE,
            bold=True
        )
        typer.secho("\n"+"-" * len(headers) + "\n", fg=typer.colors.BLUE)
        
@app.command(name="update")
def update_files(
    folder: str = typer.Option(
        ...,
        "--folder",
        "-f",
        help="Folder to update files information.",
    )
) -> None:
    """Update files information in destination folder."""
    file_manager = get_file_manager()
    _folder = Path(folder)
    if not _folder.exists():
        typer.secho(
            f'Folder "{folder}" does not exist.',
            fg=typer.colors.RED,
        )
        raise typer.Exit(1)
    file_manager.update_files(Path(folder))
    typer.secho(
        f'Files information in destination folder updated successfully.',
        fg=typer.colors.GREEN,
    )

@app.command(name="update-all")
def update_all() -> None:
    """Update files information in destination folder."""
    file_manager = get_file_manager()
    dir_list = file_manager.get_dir_list()
    for dirname in dir_list:
        file_manager.update_files(Path(dirname))
    typer.secho(
        f'Files information in destination folder updated successfully.',
        fg=typer.colors.GREEN,
    )

@app.command(name="remove")
def remove_files(
    
    
) -> None:
    """Remove remove files with the specified criteria in dest folder."""
    pass