# Contributing to Syntax Diagrams

## Set up your environment

We use [`uv`] and [`poe`] to run tasks, but it is possible to use pure pip as well.

[`uv`]: https://docs.astral.sh/uv/
[`poe`]: https://poethepoet.natn.io/index.html

### Using pip

1. Create a virtual environment with python `3.13` or newer
   (some of dev tools don't work with older pythons).

2. Make sure your pip is up to date:

   ```shell
   pip install -U pip
   ```

2. Install Syntax Diagrams in development mode, and install dev dependencies:

   ```shell
   pip install -e . --group dev
   ```

3. Install pre-commit hooks:

   ```shell
   prek install
   ```

4. [Install `poe`], either globally or in virtual environment:

   ```shell
   pip install poethepoet
   ```

[Install `poe`]: https://poethepoet.natn.io/installation.html

### Using uv

1. Sync your virtual environment:

   ```shell
   uv sync
   ```

2. Install pre-commit hooks:

   ```shell
   uv run prek install
   ```

3. [Install `poe`] if you don't have it already:

   ```shell
   uv tool install poethepoet
   ```


## Run commands

We use `poe` for most of the tasks:

```shell
poe lint  # Lint and fix code style.
poe test  # Run tests.
poe test-all  # Run tests for all pythons.
```

You can see all commands in `poe`'s help:

```shell
poe --help
```

Note: tests use Cairo for image diffing. On Linux, install the system
dependencies:

```shell
sudo apt-get update
sudo apt-get install -y libcairo2-dev libjpeg-dev libgif-dev
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

You'll get a local installation of the *try* page that runs against the
local backend.


## Build docs

Use `poe` commands:

```shell
poe doc  # Build HTML.
poe doc-watch  # Run sphinx-autobuild.
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
