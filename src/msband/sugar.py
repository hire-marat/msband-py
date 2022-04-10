import typing

K = typing.TypeVar("K")
V = typing.TypeVar("V")


def or_strict(*args: V) -> typing.Optional[V]:
    for non_none_result in args:
        if non_none_result is not None:
            return non_none_result
    else:
        return None  # not strictly needed, here for readability


def or_strict_get(key: K, *args: typing.Dict[K, V]) -> typing.Optional[V]:
    for potential_dict in args:
        potential_result = potential_dict.get(key)
        if potential_result is not None:
            return potential_result
    else:
        return None  # not strictly needed, here for readability
