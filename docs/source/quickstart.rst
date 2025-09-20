Quickstart
==========

.. currentmodule:: syntax_diagrams

Install ``syntax-diagrams``:

.. code-block:: console

    $ pip install syntax-diagrams

Describe a syntax diagram using
:ref:`constructors <constructors>` or :ref:`YAML <literals>`:

.. tab-set::
    :sync-group: diagram-example

    .. tab-item:: Python
        :sync: python

        .. code-block:: python

            from syntax_diagrams import *

            diagram = sequence(
                choice(
                    terminal("lexer"),
                    skip(),
                    terminal("parser"),
                )
                terminal("grammar"),
                non_terminal("identifier"),
                terminal(";"),
            )

    .. tab-item:: YAML
        :sync: yaml

        .. code-block:: python

            import yaml

            from syntax_diagrams import *

            diagram = yaml.load("""
                - choice:
                  - "lexer"
                  -
                  - "parser"
                  default: 1
                - grammar
                - non_terminal: "identifier"
                - ";"
            """)

Render the diagram using `render_svg` or `render_text`:

.. code-block:: python

    svg = render_svg(diagram)

Customize rendering by providing `SvgRenderSettings` or `TextRenderSettings`:

.. code-block:: python

    svg = render_svg(
        diagram,
        max_width=500,
        settings=SvgRenderSettings(
            arrow_style=ArrowStyle.TRIANGLE,
            css_class="my-diagram",
        ),
    )

Use `online editor`__ to play with diagram descriptions and settings.

__ https://taminomara.github.io/syntax-diagrams/try/
