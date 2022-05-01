import enum
import typing
import itertools
from construct import Adapter, Default
from construct_typed import EnumBase as _EnumBase, csfield as _csfield
from construct_typed.dataclass_struct import Construct, ParsedType, Context

K = typing.TypeVar("K")
V = typing.TypeVar("V")
E = typing.TypeVar("E", bound=enum.EnumMeta)


class EnumBase(_EnumBase):
    @classmethod
    def _missing_(cls, value) -> None:
        return None


def IntEnumAdapter(base_enum: E) -> typing.Type[Adapter]:
    def _encode(self, obj: E, context, path) -> int:
        return obj

    def _decode(self, obj: int, context, path) -> E:
        return base_enum(obj)

    return type(
        f"{base_enum.__name__}Adapter",
        (Adapter,),
        {
            "__slots__": tuple(),
            "_encode": _encode,
            "_decode": _decode,
        },
    )


t = typing


def csfield(
    subcon: Construct[ParsedType, t.Any],
    doc: t.Optional[str] = None,
    parsed: t.Optional[t.Callable[[t.Any, Context], None]] = None,
    init: typing.Optional[bool] = None,
) -> ParsedType:
    field = _csfield(subcon=subcon, doc=doc, parsed=parsed)

    if isinstance(subcon, Default):
        field.init = True

    if init is not None:
        field.init = init

    return field


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
