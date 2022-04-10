import typing
import dataclasses
from msband.static import BandType


@dataclasses.dataclass(frozen=True)
class BandConstants:
    BandType: BandType
    MeTileWidth: int
    MeTileHeight: int
    TileIconPreferredSize: int
    BadgeIconPreferredSize: int
    NotificiationIconPreferredSize: int
    MaxIconsPerTile: int

    by_type: typing.ClassVar = {}  # type: typing.Dict[BandType, "BandConstants"]

    def __post_init__(self):
        self.by_type[self.BandType] = self


CARGO = BandConstants(
    BandType=BandType.Cargo,
    MeTileWidth=310,
    MeTileHeight=102,
    TileIconPreferredSize=46,
    BadgeIconPreferredSize=24,
    NotificiationIconPreferredSize=36,
    MaxIconsPerTile=10,
)

ENVOY = BandConstants(
    BandType=BandType.Envoy,
    MeTileWidth=310,
    MeTileHeight=128,
    TileIconPreferredSize=48,
    BadgeIconPreferredSize=24,
    NotificiationIconPreferredSize=36,
    MaxIconsPerTile=15,
)
