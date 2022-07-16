import typing
import dataclasses
from msband.sugar import EnumBase, IntEnumAdapter


class BandType(EnumBase):
    Null = 0
    Cargo = 1
    Envoy = 2


BandTypeAdapter = IntEnumAdapter(BandType)


def pcb_id_to_type(pcb_id: int) -> BandType:
    if pcb_id < 20:
        return BandType.Cargo
    else:
        return BandType.Envoy


@dataclasses.dataclass(frozen=True, kw_only=True)
class BandConstants:
    BandType: BandType
    UsbVendorId: int
    UsbProductId: int
    UsbRevision: typing.Optional[int]
    MeTileWidth: int
    MeTileHeight: int
    TileIconPreferredSize: int
    BadgeIconPreferredSize: int
    NotificiationIconPreferredSize: int
    MaxIconsPerTile: int
    ProfileVersion: int
    ProfileSize: int
    RunMetricsDisplaySlotCount: int
    BikeMetricsDisplaySlotCount: int
    UserProfileReservedSize: int
    BandGoalsSerializedVersion: int

    by_type: typing.ClassVar = typing.cast(typing.Dict[BandType, "BandConstants"], {})

    def __post_init__(self):
        self.by_type[self.BandType] = self


CARGO = BandConstants(
    BandType=BandType.Cargo,
    UsbVendorId=0x045E,
    UsbProductId=0x02D7,
    UsbRevision=None,
    MeTileWidth=310,
    MeTileHeight=102,
    TileIconPreferredSize=46,
    BadgeIconPreferredSize=24,
    NotificiationIconPreferredSize=36,
    MaxIconsPerTile=10,
    ProfileVersion=1,
    ProfileSize=128,
    RunMetricsDisplaySlotCount=5,
    BikeMetricsDisplaySlotCount=6,
    UserProfileReservedSize=23,
    BandGoalsSerializedVersion=0,
)

ENVOY = BandConstants(
    BandType=BandType.Envoy,
    UsbVendorId=0x045E,
    UsbProductId=0x02D6,
    UsbRevision=0x0001,
    MeTileWidth=310,
    MeTileHeight=128,
    TileIconPreferredSize=48,
    BadgeIconPreferredSize=24,
    NotificiationIconPreferredSize=36,
    MaxIconsPerTile=15,
    ProfileVersion=2,
    ProfileSize=397,
    RunMetricsDisplaySlotCount=7,
    BikeMetricsDisplaySlotCount=7,
    UserProfileReservedSize=256,
    BandGoalsSerializedVersion=1,
)
