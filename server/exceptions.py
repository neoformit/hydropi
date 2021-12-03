"""Custom exceptions."""


class Http400(Exception):
    """Bad request."""

    pass


class Http401(Exception):
    """Unauthorized."""

    pass


class Http404(Exception):
    """Not found."""

    pass
