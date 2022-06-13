import urllib.parse
from time import sleep

import typer
import requests
from decouple import config
from fastapi import status

from app import schemas


SERVER_IP = config("SERVER_IP")
PORT = config("PORT")
SERVER_URL = f"http://{SERVER_IP}:{PORT}"


BASE_URL = 'https://www.googleapis.com/books/v1/volumes'
SEARCH_URL = BASE_URL + "?{}"
BOOK_URL = BASE_URL + '/{}'
SEARCH_RESULTS = 5
NOT_FOUND = 'Not found'
DEFAULT_LANGUAGE = "en"
MAX_LOAD = 10


def create_user(username):

    user_email = typer.prompt("What is your email address?")
    user_first_name = typer.prompt("What is your first name?")
    user_last_name = typer.prompt("What is your last name?")
    user_password = typer.prompt("What password would you like to use?")

    user = schemas.UserCreate(
        username=username,
        email=user_email,
        first_name=user_first_name,
        last_name=user_last_name,
        password=user_password
    ).dict()

    response = requests.post(f"{SERVER_URL}/users", json=user)

    if response.status_code == status.HTTP_201_CREATED:
        typer.echo(f"Congratulations! {username} has been created!")
        return main()

    typer.echo(f"{response.json()['detail']}.")
    return main()


def user_auth(username: str, password: str):
    
    response = requests.post(
            f"{SERVER_URL}/token", 
            data={"username": username, "password": password},
            headers={"content-type": "application/x-www-form-urlencoded"}
            )

    if response.status_code == status.HTTP_401_UNAUTHORIZED:
        typer.echo(f"{response.json()['detail']}. Please try again.\n")
        return main()

    access_token = {"Authorization": f"Bearer {response.json()['access_token']}"}
    user = requests.get(f"{SERVER_URL}/users/me", headers=access_token)

    return user, access_token


def user_login_prompt():
    
    username = typer.prompt("What is your username?")
    if username:
        password = typer.prompt("What is your password?", hide_input=True)

    return username, password


def greeting():

    typer.echo("\nWelcome to Reading Lists!")
    greeting_prompt = typer.prompt("What would you like to do? [login or create]")
    return greeting_prompt


def google_books_request(user_input, search_index):

    params = {
        "q": user_input,
        "startIndex": search_index,
        "maxResults": SEARCH_RESULTS,
        "langRestrict": DEFAULT_LANGUAGE
    }

    query_string = urllib.parse.urlencode(params)
    query = SEARCH_URL.format(query_string)
    response = requests.get(query).json()

    return response
    

def main():

    greeting_action = greeting()

    if greeting_action.lower() == "login":
        username, password = user_login_prompt()
        user, access_token = user_auth(username, password)
    else:
        username = typer.prompt("What username would you like to create an account with?")
        create_user(username)


    if user:

        user_input = typer.prompt("What books would you like to search for and create?")
        search_index = 0
        books_loaded = 0
        stop_load = False

        google_books_response = google_books_request(user_input, search_index)

        while True:
            
            for google_book in google_books_response["items"]:

                book_id = google_book.get("id")
                google_book_exist_response = requests.get(f"{SERVER_URL}/books/google/{book_id}", headers=access_token).json()

                if google_book_exist_response is None:
                    
                    query = BOOK_URL.format(book_id)
                    google_book_response = requests.get(query).json()

                    book_info = google_book_response.get("volumeInfo")
                    book_title = book_info.get("title")
                    book_authors = ", ".join(book_info.get("authors", NOT_FOUND))
                    book_publisher = book_info.get("publisher", NOT_FOUND).strip('"')
                    book_published_date = book_info.get("publishedDate", NOT_FOUND)
                    book_description = book_info.get("description", NOT_FOUND)
                    book_page_count = book_info.get("pageCount", 0)
                    book_average_rating = book_info.get("averageRating", 0)
                    book_language = book_info.get("language", NOT_FOUND)
                    
                    if book_language != DEFAULT_LANGUAGE:
                        continue

                    user_id = user.json().get("id")
                
                    book_create = schemas.BookCreate(
                        title=book_title,
                        authors=book_authors,
                        publisher=book_publisher,
                        published_date=book_published_date,
                        description=book_description,
                        page_count=book_page_count,
                        average_rating=book_average_rating,
                        google_books_id=book_id,
                        user_id=user_id,
                    ).dict()

                    book_response = requests.post(f"{SERVER_URL}/books", json=book_create, headers=access_token)
                    
                    if book_response.status_code == status.HTTP_201_CREATED:
                        books_loaded += 1
                        print(book_title)

                    if books_loaded >= MAX_LOAD:
                        stop_load = True
                        break

            if stop_load:
                typer.echo(f"All done! {books_loaded} books were created.")
                break

            search_index += SEARCH_RESULTS
            sleep(20)

            google_books_response = google_books_request(user_input, search_index)

    return main()

    
if __name__ == "__main__":
    typer.run(main)