# bean-total-public
Bean Total accounting automation system

## Installation

This project requires Python 3.10 or newer. It uses Poetry for dependency management.

To install dependencies, run: 

```bash
$ poetry install
```

To run the FastAPI app, use:

```bash
poetry run gunicorn -k uvicorn.workers.UvicornWorker src.main:app
```


## Contributing

The main code is in the `src/` directory. Tests are in the `tests/` directory.
