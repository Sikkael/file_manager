"""RP fileman entry point script."""
# rptodo/__main__.py

from fileman import cli, __app__name__

def main():
    cli.app(prog_name=__app__name__)
    nom = input("Enter your name: ")
    print(f"Hello, {nom}!")

if __name__ == "__main__":
    main()