Describing diagrams
===================


.. role:: python(code)
   :language: python
   :class: highlight

.. currentmodule:: syntax_diagrams


Using YAML or Python literals
-----------------------------

Diagram elements are described as simple types suitable for encoding
in JSON-like formats. The specific representation was chosen to be ergonomic
when writing diagrams in YAML syntax. All examples are thus formatted as YAML.


.. type:: Element[T]
    :canonical:
        None
        | str
        | list[Element[T]]
        | Terminal[T]
        | NonTerminal[T]
        | Comment[T]
        | Sequence[T]
        | Stack[T]
        | NoBreak[T]
        | Choice[T]
        | Optional[T]
        | OneOrMore[T]
        | ZeroOrMore[T]
        | Barrier[T]

    Describes an element of a syntax diagram.

    If element is `None`, it's rendered as a simple line with no additional content.
    This can be used to create optional elements using `Choice`.

    If element is a list, it's rendered as a `Sequence`.

    If element is a string, it's rendered as a `Terminal`.

    Otherwise, an element should be a dict containing one of the following keys:
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
    `barrier <ZeroOrMore>`.

    **Example:**

    .. tab-set::
        :sync-group: diagram-example

        .. tab-item:: YAML
            :sync: yaml

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
            :sync: python

            .. code-block:: python

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

        .. tab-item:: Rendered
            :sync: rendered

            .. code-block:: yaml

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

    Use :func:`terminal` to create this description in Python.

    **Dict keys:**

    -   :python:`terminal: str`, *required*

        Text of the terminal, required.

        .. note::

            At the moment, we don't support multiline text.

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
        :sync-group: diagram-example

        .. tab-item:: YAML
            :sync: yaml

            .. code-block:: yaml

                terminal: "INT"

        .. tab-item:: Python
            :sync: python

            .. code-block:: python

                diagram = terminal("INT")

        .. tab-item:: Rendered
            :sync: rendered

            .. code-block:: yaml

                terminal: "INT"


    Terminal nodes without settings can be encoded as simple strings:

    .. tab-set::
        :sync-group: diagram-example

        .. tab-item:: YAML
            :sync: yaml

            .. code-block:: yaml

                "INT"

        .. tab-item:: Rendered
            :sync: rendered

            .. code-block:: yaml

                "INT"


.. type:: NonTerminal[T]

    Describes a non-terminal node with optional additional settings.

    Use :func:`non_terminal` to create this description in Python.

    **Dict keys:**

    -   :python:`non_terminal: str`, *required*

        Text of the non-terminal, required.

        .. note::

            At the moment, we don't support multiline text.

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
        :sync-group: diagram-example

        .. tab-item:: YAML
            :sync: yaml

            .. code-block:: yaml

                non_terminal: "expr"

        .. tab-item:: Python
            :sync: python

            .. code-block:: python

                diagram = non_terminal("expr")

        .. tab-item:: Rendered
            :sync: rendered

            .. code-block:: yaml

                non_terminal: "expr"


.. type:: Comment[T]

    Describes a comment node with optional additional settings.

    Use :func:`comment` to create this description in Python.

    **Dict keys:**

    -   :python:`comment: str`, *required*

        Text of the terminal, required.

        .. note::

            At the moment, we don't support multiline text.

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
        :sync-group: diagram-example

        .. tab-item:: YAML
            :sync: yaml

            .. code-block:: yaml

                comment: "escaped literal"

        .. tab-item:: Python
            :sync: python

            .. code-block:: python

                diagram = comment("escaped literal")

        .. tab-item:: Rendered
            :sync: rendered

            .. code-block:: yaml

                comment: "escaped literal"



.. type:: Sequence[T]

    Describes an automatically wrapped sequence of elements.

    Use :func:`sequence` to create this description in Python.

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
        :sync-group: diagram-example

        .. tab-item:: YAML
            :sync: yaml

            .. code-block:: yaml

                sequence:
                - comment: "escaped literal"
                - "ESC"
                - "CHAR"
                linebreaks: "SOFT"

        .. tab-item:: Python
            :sync: python

            .. code-block:: python

                diagram = sequence(
                    comment("escaped literal"),
                    terminal("ESC"),
                    terminal("CHAR"),
                    linebreaks: LineBreak.SOFT,
                )

        .. tab-item:: Rendered
            :sync: rendered

            .. code-block:: yaml

                sequence:
                - comment: "escaped literal"
                - "ESC"
                - "CHAR"
                linebreaks: "SOFT"

    Sequences without settings can also be encoded as simple lists:

    .. tab-set::
        :sync-group: diagram-example

        .. tab-item:: YAML
            :sync: yaml

            .. code-block:: yaml

                - comment: "escaped literal"
                - "ESC"
                - "CHAR"

        .. tab-item:: Rendered
            :sync: rendered

            .. code-block:: yaml

                - comment: "escaped literal"
                - "ESC"
                - "CHAR"


.. type:: Stack[T]

    Describes a sequence of elements that wraps after each element.

    This is a shortcut for creating a `Sequence`
    with `~Sequence.linebreaks` set to `~LineBreak.HARD`.

    Use :func:`stack` to create this description in Python.

    **Dict keys:**

    -   :python:`stack: list[Element[T]]`, *required*

        Elements in the stack.

    **Example:**

    .. tab-set::
        :sync-group: diagram-example

        .. tab-item:: YAML
            :sync: yaml

            .. code-block:: yaml

                stack:
                - comment: "escaped literal"
                - "ESC"
                - "CHAR"

        .. tab-item:: Python
            :sync: python

            .. code-block:: python

                diagram = stack(
                    comment("escaped literal"),
                    terminal("ESC"),
                    terminal("CHAR"),
                )

        .. tab-item:: Rendered
            :sync: rendered

            .. code-block:: yaml

                stack:
                - comment: "escaped literal"
                - "ESC"
                - "CHAR"


.. type:: NoBreak[T]

    Describes a sequence of elements that doesn't wrap.

    This is a shortcut for creating a `Sequence`
    with `~Sequence.linebreaks` set to `~LineBreak.NO_BREAK`.

    Use :func:`no_break` to create this description in Python.

    **Dict keys:**

    -   :python:`no_break: list[Element[T]]`, *required*

        Elements in the no-break sequence.

    **Example:**

    .. tab-set::
        :sync-group: diagram-example

        .. tab-item:: YAML
            :sync: yaml

            .. code-block:: yaml

                no_break:
                - comment: "escaped literal"
                - "ESC"
                - "CHAR"

        .. tab-item:: Python
            :sync: python

            .. code-block:: python

                diagram = no_break(
                    comment("escaped literal"),
                    terminal("ESC"),
                    terminal("CHAR"),
                )

        .. tab-item:: Rendered
            :sync: rendered

            .. code-block:: yaml

                no_break:
                - comment: "escaped literal"
                - "ESC"
                - "CHAR"


.. type:: Choice[T]

    Describes a choice between several elements.

    Use :func:`choice` to create this description in Python.

    **Dict keys:**

    -   :python:`choice: list[Element[T]]`, *required*

        Elements to choose from.

    -   :python:`default: int`

        Index of item that will be placed on the main line.

        Should be less then number of choice elements.

    **Example:**

    .. tab-set::
        :sync-group: diagram-example

        .. tab-item:: YAML
            :sync: yaml

            .. code-block:: yaml

                choice:
                - "INT"
                - "STR"
                - sequence:
                  - "("
                  - non_terminal: "expr"
                  - ")"

        .. tab-item:: Python
            :sync: python

            .. code-block:: python

                diagram = choice(
                    terminal("INT"),
                    terminal("STR"),
                    sequence(
                      terminal("("),
                      non_terminal("expr"),
                      terminal(")"),
                    )
                )

        .. tab-item:: Rendered
            :sync: rendered

            .. code-block:: yaml

                choice:
                - "INT"
                - "STR"
                - sequence:
                  - "("
                  - non_terminal: "expr"
                  - ")"


.. type:: Optional[T]

    Describes an optional element.

    This is a shortcut for creating a `Choice`
    with a :func:`skip` and a single element.

    Use :func:`optional` to create this description in Python.

    **Dict keys:**

    -   :python:`optional: Element[T]`, *required*

        Element that will be made optional.

    -   :python:`skip: bool`

        If set to `True`, the optional element will be rendered off the main line.

    -   :python:`skip_bottom: bool`

        If set to `True`, the skip line will be rendered below the skipped element.

    **Example:**

    .. tab-set::
        :sync-group: diagram-example

        .. tab-item:: YAML
            :sync: yaml

            .. code-block:: yaml

                optional:
                - non_terminal: "annotation"

        .. tab-item:: Python
            :sync: python

            .. code-block:: python

                diagram = optional(
                    non_terminal("annotation"),
                )

        .. tab-item:: Rendered
            :sync: rendered

            .. code-block:: yaml

                optional:
                - non_terminal: "annotation"


.. type:: OneOrMore[T]

    Describes a repeated element.

    Use :func:`one_or_more` to create this description in Python.

    **Dict keys:**

    -   :python:`one_or_more: Element[T]`, *required*

        Element that will be repeated.

    -   :python:`repeat: Element[T]`

        An element that will be placed on the backwards path.

    -   :python:`repeat_top: bool`

        If set to `True`, the repeat element will be rendered above the repeated one.

    **Example:**

    .. tab-set::
        :sync-group: diagram-example

        .. tab-item:: YAML
            :sync: yaml

            .. code-block:: yaml

                one_or_more:
                - non_terminal: "expr"
                repeat: "COMMA"

        .. tab-item:: Python
            :sync: python

            .. code-block:: python

                diagram = one_or_more(
                    non_terminal("expr"),
                    repeat=terminal("COMMA"),
                )

        .. tab-item:: Rendered
            :sync: rendered

            .. code-block:: yaml

                one_or_more:
                - non_terminal: "expr"
                repeat: "COMMA"


.. type:: ZeroOrMore[T]

    Describes an optional repeated element.

    This is a shortcut for creating an `Optional` with an `OneOrMore`
    element inside.

    Use :func:`zero_or_more` to create this description in Python.

    **Dict keys:**

    -   :python:`zero_or_more: Element[T]`, *required*

        Element that will be repeated.

    -   :python:`repeat: Element[T]`

        An element that will be placed on the backwards path.

    -   :python:`repeat_top: bool`

        If set to `True`, the repeat element will be rendered above the repeated one.

    -   :python:`skip: bool`

        If set to `True`, the optional repeated element will be rendered off the main line.

    -   :python:`skip_bottom: bool`

        If set to `True`, the skip line will be rendered below the skipped element.

    **Example:**

    .. tab-set::
        :sync-group: diagram-example

        .. tab-item:: YAML
            :sync: yaml

            .. code-block:: yaml

                zero_or_more:
                - non_terminal: "expr"
                repeat: "COMMA"

        .. tab-item:: Python
            :sync: python

            .. code-block:: python

                diagram = zero_or_more(
                    non_terminal("expr"),
                    repeat=terminal("COMMA"),
                )

        .. tab-item:: Rendered
            :sync: rendered

            .. code-block:: yaml

                zero_or_more:
                - non_terminal: "expr"
                repeat: "COMMA"


.. type:: Barrier[T]

    Isolates an element and disables optimizations that merge lines between
    this element and the rest of the diagram.

    Use :func:`barrier` to create this description in Python.

    **Dict keys:**

    -   :python:`barrier: Element[T]`, *required*

        Element that will be isolated.

    **Example:**

    .. tab-set::
        :sync-group: diagram-example

        .. tab-item:: YAML
            :sync: yaml

            .. code-block:: yaml

                - "A"
                - optional:
                  - "B"
                  - barrier:
                    - optional:
                      - "C"

        .. tab-item:: Python
            :sync: python

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
            :sync: rendered

            .. list-table::
                :widths: 50 50
                :header-rows: 1

                * - Without barrier:
                  -
                    .. code-block:: yaml

                        - "A"
                        - optional:
                          - "B"
                          - optional:
                            - "C"

                * - With barrier:
                  -
                    .. code-block:: yaml

                        - "A"
                        - optional:
                          - "B"
                          - barrier:
                            - optional:
                            - "C"


.. type:: Group[T]

    Draws a box around some element.

    Use :func:`group` to create this description in Python.

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
        :sync-group: diagram-example

        .. tab-item:: YAML
            :sync: yaml

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
            :sync: python

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
            :sync: rendered

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
