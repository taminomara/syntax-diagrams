from __future__ import annotations

import typing as _t

__all__ = [
    "HrefResolver",
]

T = _t.TypeVar("T")


class HrefResolver(_t.Generic[T]):
    """
    An interface that allows pre-processing all hyperlinks in nodes.

    """

    def resolve(
        self, text: str, href: str | None, title: str | None, resolver_data: T | None
    ):
        """
        Called before rendering a node.

        Should return a tuple ``(text, href, title)``, possibly modified.

        :param text:
            text of the node.
        :param href:
            hyperlink attached to the node.
        :param title:
            title for hyperlink.

        """

        return text, href, title
