from rest_framework.fields import empty
from rest_framework.status import is_success


class TrueEmptyStr(str):
    def __bool__(self):
        return True


true_empty_str = TrueEmptyStr()


def append_to_mark_line(source: str, mark: str, target: str) -> str:
    lines = source.splitlines()
    for i, line in enumerate(lines):
        if mark in line:
            lines[i] = lines[i] + target
    return "\n".join(lines)


def is_action_view(view):
    return getattr(view, "detail", None) is not None
    # return isinstance(view.action_map, str)


def is_not_empty_none(value):
    return value is not None and value is not empty


def any_success(responses):
    return any(is_success(int(sc)) for sc in responses if sc != "default")
