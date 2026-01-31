from typing import Any, Awaitable, Callable

from rest_framework.decorators import action as _action


def action(*args, **kwargs) -> Callable[..., Any | Awaitable[Any]]:
    return _action(*args, **kwargs)
