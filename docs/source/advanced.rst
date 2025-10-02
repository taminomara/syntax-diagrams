Advanced API
============

.. currentmodule:: syntax_diagrams


Customizing hyperlink resolution
--------------------------------

When diagram is rendered as SVG, hyperlinks and their titles are added to the nodes
to create interactive elements. You can control this process by supplying
an implementation of `HrefResolver`.

For example, `Sphinx plugin`__ for syntax diagrams uses this functionality to link
nodes with grammars and production rules by their names.

__ https://sphinx-syntax.readthedocs.io/en/stable/

.. autoclass:: HrefResolver
    :members:


Customizing text measure
------------------------

SVG renderer needs to know dimensions of node's text in order to size the diagram
appropriately. By default, it uses a very crude heuristic of multiplying
length of text by an average character width. If you have a font file, though,
you can improve text measuring by providing an instance of `TrueTextMeasure`.

.. autoclass:: TextMeasure
    :members:

.. autoclass:: SimpleTextMeasure
    :class-doc-from: both

.. autoclass:: TrueTextMeasure
    :class-doc-from: both
