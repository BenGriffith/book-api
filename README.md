## General Info

FastAPI application allowing individuals to manage their reading lists from an ever-growing books database. The API includes endpoints for managing users, books and lists using POST, GET, PATCH, DELETE and PUT with additional endpoints for user password encryption and OAuth. Lastly, it interfaces with a terminal application built using Typer. Please feel free to check it out here: https://github.com/BenGriffith/book-api-cli.

Swagger / OpenAPI

![Swagger](images/swagger.png "Swagger / OpenAPI")

## Setup
To run this project, follow the steps below:
```
$ git clone https://github.com/BenGriffith/book-api.git
$ cd app/
$ cp .env-template .env
```

Open .env, populate the environment variables and continue with the following command:
```
$ docker-compose --env-file app/.env up -d
```

Navigate to your browser and type in `http://localhost:8000/docs`. You should see content similar to the Swagger / OpenAPI image above. Alternatively, you could run `$ curl http://localhost:8000/docs` from the command line and verify the HTML output.