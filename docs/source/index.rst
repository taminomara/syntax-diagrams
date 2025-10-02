Syntax Diagrams
===============

Python library for rendering syntax diagrams (a.k.a. railroad diagrams).


Features
--------

-   Automatic line wrapping, keeping width of the diagram below limits.
-   Clever rendering of optionals, avoiding clutter where possible.
-   Automatic right-to-left rendering in one-or-more loops.
-   Producing SVGs or ASCII art.
-   `Try it in your browser.`__
-   See also: `sphinx-syntax`__, a Sphinx plugin for documenting grammars.

__ https://syntax-diagrams.readthedocs.io/en/stable/try
__ https://sphinx-syntax.readthedocs.io/en/stable/


Example output
--------------

This is a part of `SQLite's grammar`__ rendered with this library:

__ https://sqlite.org/lang_select.html

.. syntax:diagram::

    - optional:
      - "WITH"
      - optional: "RECURSIVE"
      - one_or_more:
        - non_terminal: "common-table-expression"
        repeat: ","
    - one_or_more:
      - text: select-core
        group:
        - choice:
          - stack:
            -
              - "SELECT"
              - choice:
                -
                - "DISTINCT"
                - "ALL"
              - one_or_more:
                - non_terminal: "result-column"
                repeat: ","
            -
              - optional:
                - "FROM"
                - choice:
                  - one_or_more:
                    - non_terminal: "table-or-subquery"
                    repeat: ","
                  - non_terminal: "join-clause"
            -
              - optional:
                - "WHERE"
                - non_terminal: "expr"
            -
              - optional:
                - "GROUP"
                - "BY"
                - one_or_more:
                  - non_terminal: "expr"
                  repeat: ","
              - optional:
                - "HAVING"
                - non_terminal: "expr"
            -
              - optional:
                - "WINDOW"
                - one_or_more:
                  - non_terminal: "window-name"
                  - "AS"
                  - non_terminal: "window-defn"
                  repeat: ","
                skip: true
                skip_bottom: true
          -
            - "VALUES"
            - one_or_more:
              - "("
              - one_or_more:
                  non_terminal: "expr"
                repeat: ","
              - ")"
              repeat: ","
      repeat:
        non_terminal: "compound-operator"
    - optional:
      - "ORDER"
      - "BY"
      - one_or_more:
        - non_terminal: "ordering-term"
        repeat: ","
    - optional:
      - barrier:
        - "LIMIT"
        - non_terminal: "expr"
        - choice:
          -
          -
            - "OFFSET"
            - non_terminal: "expr"
          -
            - ","
            - non_terminal: "expr"
      skip: true
      skip_bottom: true


Table of contents
-----------------

.. toctree::
    :maxdepth: 2

    quickstart
    describe
    render
    advanced

.. toctree::
    :hidden:
    :caption: Links

    GitHub <https://github.com/taminomara/syntax-diagrams/>
    Try in browser <https://syntax-diagrams.readthedocs.io/en/stable/try>
