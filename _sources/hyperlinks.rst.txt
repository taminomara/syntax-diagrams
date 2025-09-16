Customizing hyperlink resolution
================================


.. currentmodule:: syntax_diagrams

When diagram is rendered as SVG, hyperlinks and their titles are added to the nodes
to create interactive elements. You can control this process by supplying
an implementation of `HrefResolver`.

For example, `Sphinx plugin`__ for syntax diagrams uses this functionality to link
nodes with grammars and production rules by their names.

__ https://taminomara.github.io/sphinx-syntax

.. autoclass:: HrefResolver
    :members:
