import typer
import requests


def _book_prompt():

    try:
        user_input = int(typer.prompt("What would you like to do?\nPress 1 to create a book\nPress 2 to create multiple books\n"))
    except:
        return _book_prompt()

    if user_input == 1:
        typer.echo("create a book") # placeholder - TBD
    elif user_input == 2:
        typer.echo("create multiple books") # placeholder - TBD
    else:
        return _book_prompt()


def main():
    _book_prompt()

    
if __name__ == "__main__":
    typer.run(main)