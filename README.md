# Example Petstore REST Services with Connexion 3

Example petstore REST implementation with Connexion 3 AsyncApp, Sqlalchemy, and Marshmallow

## Installation

First, you need to clone this repository:

```bash
git clone git@github.com:johnbyrne7/c3petstore.git
```

Or:

```bash
git clone https://github.com/johnbyrne7/c3petstore.git
```

Then change into the `c3petstore` folder:

```bash
cd c3petstore
```

Next, create a virtual environment and install all the dependencies:

```bash
python3.13 -m venv .venv  #  or whatever you need for python3.13
source .venv/bin/activate   # on Windows, use ".venv\scripts\activate" instead
pip install -r requirements.txt
```

## How to Test the Example Application

**Before run the example application, make sure you have activated the virtual enviroment.**


```bash
pytest tests/
```

Or, you can run a local HTTP application like this:

```bash
python app.py
```

The application will run on http://127.0.0.1:8080.

Use this to see the swagger documentation  http://127.0.0.1:8080/api/v3/docs/

## License

This project is licensed under the MIT License (see the `LICENSE` file for details).