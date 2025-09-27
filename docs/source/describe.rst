Describing diagrams
===================


.. role:: python(code)
   :language: python
   :class: highlight

.. currentmodule:: syntax_diagrams

.. invisible-code-block: python

    from syntax_diagrams import *


.. _literals:

Using YAML or Python literals
-----------------------------

Diagram elements are described as simple types suitable for encoding
in JSON-like formats. The specific representation was chosen to be ergonomic
when writing diagrams in YAML syntax.


.. type:: Element[T]

    Describes an element of a syntax diagram.

    -   If element is `None`, it's rendered as a simple line with no additional content.
        This can be used to create optional elements using `Choice`.

    -   If element is a list, it's rendered as a `Sequence`.

    -   If element is a string, it's rendered as a `Terminal`.

    -   Otherwise, an element should be a dict containing one of the following keys:
        `terminal <Terminal>`,
        `non_terminal <NonTerminal>`,
        `comment <Comment>`,
        `sequence <Sequence>`,
        `stack <Stack>`,
        `no_break <NoBreak>`,
        `choice <Choice>`,
        `optional <Optional>`,
        `one_or_more <OneOrMore>`,
        `zero_or_more <ZeroOrMore>`,
        `barrier <Barrier>`,
        `group <Group>`.

    **Example:**

    .. tab-set::

        .. tab-item:: YAML

            .. code-block:: yaml

                - choice:
                  - "lexer"
                  -
                  - "parser"
                  default: 1
                - grammar
                - non_terminal: "identifier"
                - ";"

        .. tab-item:: Python

            .. code-block:: python

                diagram = sequence(
                    choice(
                        terminal("lexer"),
                        skip(),
                        terminal("parser"),
                    ),
                    terminal("grammar"),
                    non_terminal("identifier"),
                    terminal(";"),
                )

        .. tab-item:: Rendered

            .. syntax:diagram::

                - choice:
                  - "lexer"
                  -
                  - "parser"
                  default: 1
                - "grammar"
                - non_terminal: "identifier"
                - ";"


.. type:: Terminal[T]

    Describes a terminal node with optional additional settings.

    **Dict keys:**

    -   :python:`terminal: str`, *required*

        Text of the terminal, required.

    -   :python:`href: str`

        Makes text node into a hyperlink.

    -   :python:`title: str`

        Title for hyperlink.

    -   :python:`css_class: str`

        Adds CSS class to node's ``<g>`` element.

    -   :python:`resolve: bool`

        If set to `False`, this node will not be passed to `HrefResolver`
        before rendering.

    -   :python:`resolver_data: T`

        Additional data for `HrefResolver`.

    **Example:**

    .. tab-set::

        .. tab-item:: YAML

            .. code-block:: yaml

                terminal: "INT"
                href: "#syntax_diagrams.Terminal"

        .. tab-item:: Python

            .. code-block:: python

                diagram = terminal("INT", href="#syntax_diagrams.Terminal")

        .. tab-item:: Rendered

            .. syntax:diagram::

                terminal: "INT"
                href: "#syntax_diagrams.Terminal"


    Terminal nodes without settings can be encoded as simple strings:

    .. tab-set::

        .. tab-item:: YAML

            .. code-block:: yaml

                "INT"

        .. tab-item:: Rendered

            .. syntax:diagram::

                "INT"


.. type:: NonTerminal[T]

    Describes a non-terminal node with optional additional settings.

    **Dict keys:**

    -   :python:`non_terminal: str`, *required*

        Text of the non-terminal, required.

    -   :python:`href: str`

        Makes text node into a hyperlink.

    -   :python:`title: str`

        Title for hyperlink.

    -   :python:`css_class: str`

        Adds CSS class to node's ``<g>`` element.

    -   :python:`resolve: bool`

        If set to `False`, this node will not be passed to `HrefResolver`
        before rendering.

    -   :python:`resolver_data: T`

        Additional data for `HrefResolver`.

    **Example:**

    .. tab-set::

        .. tab-item:: YAML

            .. code-block:: yaml

                non_terminal: "expr"
                href: "#syntax_diagrams.NonTerminal"

        .. tab-item:: Python

            .. code-block:: python

                diagram = non_terminal("expr", href="#syntax_diagrams.NonTerminal")

        .. tab-item:: Rendered

            .. syntax:diagram::

                non_terminal: "expr"
                href: "#syntax_diagrams.NonTerminal"


.. type:: Comment[T]

    Describes a comment node with optional additional settings.

    **Dict keys:**

    -   :python:`comment: str`, *required*

        Text of the terminal, required.

    -   :python:`href: str`

        Makes text node into a hyperlink.

    -   :python:`title: str`

        Title for hyperlink.

    -   :python:`css_class: str`

        Adds CSS class to node's ``<g>`` element.

    -   :python:`resolve: bool`

        If set to `False`, this node will not be passed to `HrefResolver`
        before rendering.

    -   :python:`resolver_data: T`

        Additional data for `HrefResolver`.

    **Example:**

    .. tab-set::

        .. tab-item:: YAML

            .. code-block:: yaml

                comment: "escaped literal"
                href: "#syntax_diagrams.Comment"

        .. tab-item:: Python

            .. code-block:: python

                diagram = comment("escaped literal", href="#syntax_diagrams.Comment")

        .. tab-item:: Rendered

            .. syntax:diagram::

                comment: "escaped literal"
                href: "#syntax_diagrams.Comment"



.. type:: Sequence[T]

    Describes an automatically wrapped sequence of elements.

    **Dict keys:**

    -   :python:`sequence: list[Element[T]]`, *required*

        Elements in the sequence.

    -   :python:`linebreaks: _t.Literal["HARD", "SOFT", "DEFAULT"] | list[_t.Literal["HARD", "SOFT", "DEFAULT"]]`

        Specifies line breaks after each element of the sequence.

        If given as a string or a `LineBreak`, this line break will be used
        after each of the sequence's elements.

        If given as a list of line breaks, each of list's element determines line break
        after each of the sequence's elements. This list must be one item shorter
        than number of elements in the sequence.

    **Example:**

    .. tab-set::

        .. tab-item:: YAML

            .. code-block:: yaml

                sequence:
                - comment: "escaped literal"
                - "ESC"
                - "CHAR"
                linebreaks:
                - "NO_BREAK"
                - "DEFAULT"

        .. tab-item:: Python

            .. code-block:: python

                diagram = sequence(
                    comment("escaped literal"),
                    terminal("ESC"),
                    terminal("CHAR"),
                    linebreaks=[
                        LineBreak.NO_BREAK,
                        LineBreak.DEFAULT,
                    ],
                )

        .. tab-item:: Rendered

            .. syntax:diagram::

                sequence:
                - comment: "escaped literal"
                - "ESC"
                - "CHAR"
                linebreaks:
                - "NO_BREAK"
                - "DEFAULT"

    Sequences without settings can also be encoded as simple lists:

    .. tab-set::

        .. tab-item:: YAML

            .. code-block:: yaml

                - comment: "escaped literal"
                - "ESC"
                - "CHAR"

        .. tab-item:: Rendered

            .. syntax:diagram::

                - comment: "escaped literal"
                - "ESC"
                - "CHAR"


.. type:: Stack[T]

    Describes a sequence of elements that wraps after each element.

    This is a shortcut for creating a `Sequence`
    with `~Sequence.linebreaks` set to `~LineBreak.HARD`.

    **Dict keys:**

    -   :python:`stack: list[Element[T]]`, *required*

        Elements in the stack.

    **Example:**

    .. tab-set::

        .. tab-item:: YAML

            .. code-block:: yaml

                stack:
                - comment: "escaped literal"
                - "ESC"
                - "CHAR"

        .. tab-item:: Python

            .. code-block:: python

                diagram = stack(
                    comment("escaped literal"),
                    terminal("ESC"),
                    terminal("CHAR"),
                )

        .. tab-item:: Rendered

            .. syntax:diagram::

                stack:
                - comment: "escaped literal"
                - "ESC"
                - "CHAR"


.. type:: NoBreak[T]

    Describes a sequence of elements that doesn't wrap.

    This is a shortcut for creating a `Sequence`
    with `~Sequence.linebreaks` set to `~LineBreak.NO_BREAK`.

    **Dict keys:**

    -   :python:`no_break: list[Element[T]]`, *required*

        Elements in the no-break sequence.

    **Example:**

    .. tab-set::

        .. tab-item:: YAML

            .. code-block:: yaml

                no_break:
                - comment: "escaped literal"
                - "ESC"
                - "CHAR"

        .. tab-item:: Python

            .. code-block:: python

                diagram = no_break(
                    comment("escaped literal"),
                    terminal("ESC"),
                    terminal("CHAR"),
                )

        .. tab-item:: Rendered

            .. syntax:diagram::

                no_break:
                - comment: "escaped literal"
                - "ESC"
                - "CHAR"


.. type:: Choice[T]

    Describes a choice between several elements.

    **Dict keys:**

    -   :python:`choice: list[Element[T]]`, *required*

        Elements to choose from.

    -   :python:`default: int`

        Index of item that will be placed on the main line.

        Should be less then number of choice elements.

    **Example:**

    .. tab-set::

        .. tab-item:: YAML

            .. code-block:: yaml

                choice:
                - "INT"
                - "STR"
                - sequence:
                  - "("
                  - non_terminal: "expr"
                  - ")"
                default: 1

        .. tab-item:: Python

            .. code-block:: python

                diagram = choice(
                    terminal("INT"),
                    terminal("STR"),
                    sequence(
                      terminal("("),
                      non_terminal("expr"),
                      terminal(")"),
                    ),
                    default=1,
                )

        .. tab-item:: Rendered

            .. syntax:diagram::

                choice:
                - "INT"
                - "STR"
                - sequence:
                  - "("
                  - non_terminal: "expr"
                  - ")"
                default: 1


.. type:: Optional[T]

    Describes an optional element.

    This is a shortcut for creating a `Choice`
    with a :func:`skip` and a single element.

    **Dict keys:**

    -   :python:`optional: Element[T]`, *required*

        Element that will be made optional.

    -   :python:`skip: bool`

        If set to `True`, the optional element will be rendered off the main line.

    -   :python:`skip_bottom: bool`

        If set to `True`, the skip line will be rendered below the skipped element.

    **Example:**

    .. tab-set::

        .. tab-item:: YAML

            .. code-block:: yaml

                optional:
                - non_terminal: "annotation"
                skip: true

        .. tab-item:: Python

            .. code-block:: python

                diagram = optional(
                    non_terminal("annotation"),
                    skip=True,
                )

        .. tab-item:: Rendered

            .. syntax:diagram::

                optional:
                  non_terminal: "annotation"
                skip: true


.. type:: OneOrMore[T]

    Describes a repeated element.

    **Dict keys:**

    -   :python:`one_or_more: Element[T]`, *required*

        Element that will be repeated.

    -   :python:`repeat: Element[T]`

        An element that will be placed on the backwards path.

    .. -   :python:`repeat_top: bool`

    ..     If set to `True`, the repeat element will be rendered above the repeated one.

    **Example:**

    .. tab-set::

        .. tab-item:: YAML

            .. code-block:: yaml

                one_or_more:
                  non_terminal: "expr"
                repeat: "COMMA"

        .. tab-item:: Python

            .. code-block:: python

                diagram = one_or_more(
                    non_terminal("expr"),
                    repeat=terminal("COMMA"),
                )

        .. tab-item:: Rendered

            .. syntax:diagram::

                one_or_more:
                  non_terminal: "expr"
                repeat: "COMMA"


.. type:: ZeroOrMore[T]

    Describes an optional repeated element.

    This is a shortcut for creating an `Optional` with an `OneOrMore`
    element inside.

    **Dict keys:**

    -   :python:`zero_or_more: Element[T]`, *required*

        Element that will be repeated.

    -   :python:`repeat: Element[T]`

        An element that will be placed on the backwards path.

    .. -   :python:`repeat_top: bool`

    ..     If set to `True`, the repeat element will be rendered above the repeated one.

    -   :python:`skip: bool`

        If set to `True`, the optional repeated element will be rendered off the main line.

    -   :python:`skip_bottom: bool`

        If set to `True`, the skip line will be rendered below the skipped element.

    **Example:**

    .. tab-set::

        .. tab-item:: YAML

            .. code-block:: yaml

                zero_or_more:
                  non_terminal: "expr"
                repeat: "COMMA"

        .. tab-item:: Python

            .. code-block:: python

                diagram = zero_or_more(
                    non_terminal("expr"),
                    repeat=terminal("COMMA"),
                )

        .. tab-item:: Rendered

            .. syntax:diagram::

                zero_or_more:
                  non_terminal: "expr"
                repeat: "COMMA"


.. type:: Barrier[T]

    Isolates an element and disables optimizations that merge lines between
    this element and the rest of the diagram.

    **Dict keys:**

    -   :python:`barrier: Element[T]`, *required*

        Element that will be isolated.

    **Example:**

    .. tab-set::

        .. tab-item:: YAML

            .. code-block:: yaml

                - "A"
                - optional:
                  - "B"
                  - barrier:
                    - optional:
                      - "C"

        .. tab-item:: Python

            .. code-block:: python

                diagram = sequence(
                    terminal("A"),
                    optional(
                        terminal("B"),
                        barrier(
                            optional(
                                terminal("C"),
                            )
                        )
                    )
                )

        .. tab-item:: Rendered

            .. list-table::
                :widths: 50 50
                :header-rows: 1

                * - Without barrier:
                  - With barrier:

                * -
                    .. syntax:diagram::
                        :svg-padding: 10 10 10 10

                        - "A"
                        - optional:
                          - "B"
                          - optional:
                            - "C"
                  -
                    .. syntax:diagram::
                        :svg-padding: 10 10 10 10

                        - "A"
                        - optional:
                          - "B"
                          - barrier:
                            - optional:
                              - "C"


.. type:: Group[T]

    Draws a box around some element.

    **Dict keys:**

    -   :python:`group: Element[T]`, *required*

        Element that will be placed in a group.

    -   :python:`href: text`

        Optional caption for this group.

    -   :python:`href: str`

        Makes group's caption into a hyperlink.

    -   :python:`title: str`

        Title for hyperlink.

    -   :python:`css_class: str`

        Adds CSS class to group's ``<g>`` element.

    **Example:**

    .. tab-set::

        .. tab-item:: YAML

            .. code-block:: yaml

                - "def"
                - "("
                - group:
                  - zero_or_more:
                    - non_terminal: "param"
                    - optional:
                      - ":"
                      - non_terminal: "type"
                    repeat: ","
                  - optional: ","
                  text: Function parameters
                - ")"
                - ":"

        .. tab-item:: Python

            .. code-block:: python

                diagram = sequence(
                    terminal("def"),
                    terminal("("),
                    group(
                        zero_or_more(
                            non_terminal("param"),
                            optional(
                                terminal(":"),
                                non_terminal("type"),
                            ),
                            repeat=terminal(","),
                        ),
                        optional(terminal(",")),
                        text="Function parameters",
                    ),
                    terminal(")"),
                    terminal(":"),
                )

        .. tab-item:: Rendered

            .. syntax:diagram::

                - "def"
                - "("
                - group:
                  - zero_or_more:
                    - non_terminal: "param"
                    - optional:
                      - ":"
                      - non_terminal: "type"
                    repeat: ","
                  - optional: ","
                  text: Function parameters
                - ")"
                - ":"

.. _constructors:

Using constructors
------------------

If you're building diagrams manually in python code, you can use these constructors:

.. autofunction:: skip

.. autofunction:: terminal

.. autofunction:: non_terminal

.. autofunction:: comment

.. autofunction:: sequence

.. autofunction:: stack

.. autofunction:: no_break

.. autofunction:: choice

.. autofunction:: optional

.. autofunction:: one_or_more

.. autofunction:: zero_or_more

.. autofunction:: barrier

.. autofunction:: group


Line breaks and wrapping
------------------------

You can use `Stack` and `NoBreak` to control how diagram lines are wrapped.
Additionally, you can pass a list of line breaks to a `Sequence` element.

.. autoclass:: LineBreak
    :members:
