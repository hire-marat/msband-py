from PIL import Image
from msband.static.command import *
from msband.static import MeTileAdapter
from msband.protocol import ProtocolInterface


# Connect using your preferred interface
iband: ProtocolInterface = ...


# Get and show current MeTile image
image = iband.command(
    FireballUIReadMeTileImage,
    DataLength=iband.constants.MeTileWidth * iband.constants.MeTileHeight * 2,
    Response=MeTileAdapter(GreedyBytes, iband.constants.MeTileWidth, iband.constants.MeTileHeight),
)
image.show()


# Set an image to open, must be sized correctly (see constants above)
image_path = ...
image = Image.open(image_path)

iband.command(InstalledAppListStartStripSyncStart)

iband.command(
    FireballUIWriteMeTileImageWithID,
    ImageId=(1 << 32) - 1,
    ImageBytes=MeTileAdapter(
        GreedyBytes, iband.constants.MeTileWidth, iband.constants.MeTileHeight
    ).build(image),
    Response=Pass,
)

iband.command(InstalledAppListStartStripSyncEnd)
