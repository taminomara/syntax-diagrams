# Contributing

## Set up your environment

1. Check out the repo:

   ```shell
   git clone git@github.com:taminomara/syntax-diagrams.git
   ```

2. Create a virtual environment with python `3.12` or newer.

3. Install Syntax Diagrams in development mode, and install dev dependencies:

   ```shell
   pip install -e . --group dev
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

## Run debug server

You'll need node 22.2 or newer.

1. Navigate to `docs/try` and install dependencies:

   ```shell
   cd docs/try
   npm install
   ```

2. Start backend:

   ```shell
   python ./backend.py
   ```

3. Start frontend:

   ```shell
   npm run dev
   ```

You'll get a local installation of the *try* page that runs

## Build docs

To build the main part of documentation, just run `sphinx` as usual:

```shell
cd docs/
make html
```

To build the *try* page, navigate to `docs/try`, install dependencies
and run a production build:

```shell
cd docs/try
npm install
npm run build
```

Optionally preview the production build to make sure it works:

```shell
npm run preview
```
