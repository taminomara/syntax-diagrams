# Contributing to Sphinx-LuaLs

## Set up your environment

1. Check out the repo:

   ```shell
   git clone git@github.com:taminomara/neat-railroad-diagrams.git
   ```

2. Create a virtual environment with python `3.12` or newer.

3. Install Neat Railroad Diagrams in development mode, and install dev dependencies:

   ```shell
   pip install -e .[dev]
   ```

4. Install pre-commit hooks:

   ```shell
   pre-commit install
   ```

## Run tests

To run tests, simply run `pytest` and `pyright`:

```shell
pytest  # Run unit tests.
pyright  # Run type check.
```

To fix code style, you can manually run pre-commit hooks:

```shell
pre-commit run -a  # Fix code style.
```


## Build docs

Just run `sphinx` as usual, nothing special is required:

```shell
cd docs/
make html
```
