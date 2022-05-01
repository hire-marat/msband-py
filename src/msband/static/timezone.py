import dataclasses
from msband.sugar import csfield
from construct import PaddedString, Int16ul
from construct_typed import DataclassMixin, DataclassStruct
from msband.static import BandSystemTime, BandSystemTimeStruct


@dataclasses.dataclass(kw_only=True)
class TimeZone(DataclassMixin):

    Name: str = csfield(PaddedString(30 * 2, "utf_16_le"))
    MinutesOffset: int = csfield(Int16ul)
    DaylightMinutesOffset: int = csfield(Int16ul)
    StandardDate: BandSystemTime = csfield(BandSystemTimeStruct, init=True)
    DaylightDate: BandSystemTime = csfield(BandSystemTimeStruct, init=True)


TimeZoneStruct = DataclassStruct(TimeZone)


UTC = TimeZone(
    Name="Default (UTC)",
    MinutesOffset=0,
    DaylightMinutesOffset=0,
    StandardDate=BandSystemTime(),
    DaylightDate=BandSystemTime(),
)

GMT = TimeZone(
    Name="GMT Standard Time",
    MinutesOffset=0,
    DaylightMinutesOffset=60,
    StandardDate=BandSystemTime(Month=10, DayOfWeek=1, Hour=2),
    DaylightDate=BandSystemTime(Month=3, DayOfWeek=1, Hour=1),
)
