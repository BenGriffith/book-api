import typer
import requests
from decouple import config

from app import schemas


SERVER_IP = config("SERVER_IP")
PORT = config("PORT")
SERVER_URL = f"http://{SERVER_IP}:{PORT}"

BOOKS_URL = 'https://www.googleapis.com/books/v1/volumes'
SEARCH_URL = BOOKS_URL + '?q={}'
NOT_FOUND = 'Not found'
DEFAULT_LANGUAGE = "en"


def admin_login(username: str, password: str):
    pass


def _book_prompt():

    try:
        user_input = int(typer.prompt("What would you like to do?\nPress 1 to create a book\nPress 2 to create multiple books\n"))
    except ValueError:
        return _book_prompt()

    if user_input == 1:
        typer.echo("create a book") # placeholder - TBD
    elif user_input == 2:
        typer.echo("create multiple books") # placeholder - TBD
    else:
        return _book_prompt()



def main():

    user_input = typer.prompt("What books would you like to search for and add to the collection?")

    query = SEARCH_URL.format(user_input.replace(' ', '+'))
    response = requests.get(query)
    response_data = response.json()["items"]

    for row in response_data[:2]:
        book = row["volumeInfo"]
        
        # create author
        authors = []
        for author in book["authors"]:
            first_name, *unused, last_name = author.split(" ")

            author_create = schemas.AuthorBase(
                first_name=first_name,
                last_name=last_name
            ).dict()

            authors.append(author_create)
        
        for author in authors:
            response = requests.post(f"{SERVER_URL}/authors", json=author)
        
        # create book
        book_create = schemas.BookCreate(
            title=book["title"],
            publisher=book["publisher"],
            published_year=book["publishedDate"].split("-")[0],
            description=book["description"],
            page_count=book["pageCount"],
            average_rating=book["averageRating"],
            authors=authors,
            user_id=44 # magic number for initial testing
        ).dict()

        response = requests.post(f"{SERVER_URL}/books", json=book_create)
        
    
if __name__ == "__main__":
    typer.run(main)