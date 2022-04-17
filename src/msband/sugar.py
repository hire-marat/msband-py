import typing
import itertools

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


def bites(
    iterable_thing: typing.Iterable[V], max_len: int, remainder: bool = True
) -> typing.Generator[V, None, None]:
    iterable = iter(iterable_thing)
    while 1:
        next = tuple(itertools.islice(iterable, max_len))
        if (not remainder) and (len(next) != max_len):
            break
        if not next:
            break
        yield next
