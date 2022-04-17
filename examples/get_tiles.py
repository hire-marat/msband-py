from construct import FixedSized
from msband.static.command import *
from msband.protocol.rle import BandIcon
from msband.protocol import ProtocolInterface


# Connect using your preferred interface
iband: ProtocolInterface = ...


max_tiles = iband.command(InstalledAppListGetMaxTileAllocatedCount)

installed_tiles = iband.command(
    InstalledAppListGet,
    DataLength=4 + max_tiles * (1024 + TileData.sizeof()),
    Response=construct.Struct(
        "Icons" / Array(max_tiles, FixedSized(1024, BandIcon.struct)),
        "ActiveTiles" / Int32ul,
        "TileData" / Array(max_tiles, TileData),
    ),
)

print(installed_tiles)

default_tiles = iband.command(
    InstalledAppListGetDefaults,
    DataLength=4 + max_tiles * (1024 + TileData.sizeof()),
    Response=construct.Struct(
        "Icons" / Array(max_tiles, FixedSized(1024, BandIcon.struct)),
        "ActiveTiles" / Int32ul,
        "TileData" / Array(max_tiles, TileData),
    ),
)

installed_tiles.Icons[0].Image.show()