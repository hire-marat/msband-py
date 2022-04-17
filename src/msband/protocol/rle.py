import struct
import typing
import logging
import construct
import itertools
import dataclasses
from PIL import Image
from construct import this, Int16ub, Prefixed, GreedyBytes, Adapter, Default


class BandIconException(Exception):
    ...


def RleLengthCheck(image_bytes: bytearray, x: int, y: int):
    if len(image_bytes) > 1024 - 6:
        logging.debug(image_bytes)
        raise BandIconException(
            f"Run Length Encoding Failure. Length ({len(image_bytes)}) exceeded allowed bytes at {x}, {y}."
        )


RLE_COUNT_MASK: typing.Final = 0b11110000
RLE__DATA_MASK: typing.Final = 0b00001111

RLE_COUNT_BITS: typing.Final = bin(RLE_COUNT_MASK).count("1")
RLE__DATA_BITS: typing.Final = bin(RLE__DATA_MASK).count("1")

RLE_COUNT_SHIFT: typing.Final = len(bin(RLE_COUNT_MASK)[2:].lstrip("1"))
RLE__DATA_SHIFT: typing.Final = len(bin(RLE__DATA_MASK)[2:].lstrip("1"))

RLE_COUNT_MAX: typing.Final = (1 << RLE_COUNT_BITS) - 1
RLE__DATA_MAX: typing.Final = (1 << RLE__DATA_BITS) - 1


class RleInterrupt:
    __slots__ = "width", "index", "latch", "last_value", "value_count"
    width: int
    index: int
    latch: bool
    last_value: typing.Optional[int]
    value_count: int

    def __init__(self, width: int = None):
        self.width = width
        self.index = 0
        self.latch = False
        self.last_value = None
        self.value_count = 0

    def __call__(self, value: int) -> typing.Tuple[int, bool]:
        flip_latch = False

        if self.last_value == value:
            self.value_count += 1
        else:
            self.last_value = value
            self.value_count = 0

        if self.value_count == RLE_COUNT_MAX:
            self.value_count = 0
            flip_latch = True

        self.index += 1
        if self.index == self.width:
            self.index = 0
            flip_latch = True

        if flip_latch:
            self.latch = not self.latch

        return value & RLE__DATA_MASK, self.latch


class RleAdapterWide(Adapter):
    __slots__ = "width", "height"

    def __init__(self, subcon, width=None):
        super().__init__(subcon)

        self.width = width

    def _encode(self, obj: bytearray, context, path) -> bytes:
        return b"" + bytearray(
            value | (len(list(count)) << 4)
            for (value, latch), count in itertools.groupby(obj, key=RleInterrupt(self.width))
        )

    def _decode(self, obj: bytes, context, path) -> bytes:
        full_data = bytearray()
        for byte in obj:
            datum = (byte & RLE__DATA_MASK) >> RLE__DATA_SHIFT
            count = (byte & RLE_COUNT_MASK) >> RLE_COUNT_SHIFT
            full_data.extend(itertools.repeat(datum, count))

        return b"" + full_data


class BandIconPaletteAdapter(Adapter):
    __slots__ = "width", "height"

    default_palette = [
        *(255, 255, 255, 0),
        *(255, 255, 255, 16),
        *(255, 255, 255, 32),
        *(255, 255, 255, 48),
        #
        *(255, 255, 255, 64),
        *(255, 255, 255, 80),
        *(255, 255, 255, 96),
        *(255, 255, 255, 112),
        #
        *(255, 255, 255, 128),
        *(255, 255, 255, 144),
        *(255, 255, 255, 160),
        *(255, 255, 255, 176),
        #
        *(255, 255, 255, 192),
        *(255, 255, 255, 208),
        *(255, 255, 255, 224),
        *(255, 255, 255, 240),
    ]

    debug_palette = [
        # 16 colours
        *(255, 255, 255, 255),
        *(255, 0, 102, 255),
        *(255, 0, 204, 255),
        *(204, 0, 255, 255),
        *(102, 0, 255, 255),
        *(0, 0, 255, 255),
        *(0, 102, 255, 255),
        *(0, 204, 255, 255),
        *(0, 255, 204, 255),
        *(0, 255, 102, 255),
        *(0, 255, 0, 255),
        *(102, 255, 0, 255),
        *(204, 255, 0, 255),
        *(255, 204, 0, 255),
        *(255, 102, 0, 255),
        *(255, 0, 0, 255),
        # Black background
        *(0, 0, 0, 255),
    ]

    def __init__(self, subcon, width, height):
        super().__init__(subcon)

        self.width = width
        self.height = height

    def _encode(self, image: Image.Image, context, path) -> bytes:
        return image.tobytes()

    def _decode(self, image_data: bytes, context, path) -> Image.Image:
        width = self.width(context) if callable(self.width) else self.width
        height = self.height(context) if callable(self.height) else self.height

        if width == 0 or height == 0:
            return Image.new("P", (width, height))

        image = Image.frombytes("P", (width, height), image_data, "raw")

        image.putpalette(self.default_palette, rawmode="RGBA")
        return image


@dataclasses.dataclass
class BandIcon:
    Width: int
    Height: int
    IconData: bytes

    struct: typing.ClassVar = construct.Struct(
        "Width" / Default(Int16ub, lambda ctx: ctx["Image"].width),
        "Height" / Default(Int16ub, lambda ctx: ctx["Image"].height),
        "Image"
        / Prefixed(
            Int16ub, BandIconPaletteAdapter(RleAdapterWide(GreedyBytes), this.Width, this.Height)
        ),
    )

    def __post_init__(self):
        if len(self.IconData) * 2 != self.Width * self.Height:
            raise ValueError("Badly sized image data")

    def take_sample(self: "BandIcon", counter: int) -> typing.Tuple[int, int]:
        if counter % 2 == 0:
            return self.IconData[counter // 2] >> 4 & 15, counter + 1
        else:
            return self.IconData[counter // 2] & 15, counter + 1

    def EncodeTileIconRle(self: "BandIcon"):
        if self.Width * self.Height > 15270:
            raise BandIconException("Input icon has too many pixels for Run Length Encoding.")

        image_bytes = bytearray()
        image_index = 0

        for y in range(self.Height):
            first_sample, image_index = self.take_sample(image_index)
            streak_count = 1  # Guaranteed run of at least 1

            for x in range(1, self.Width):
                RleLengthCheck(image_bytes, x, y)

                running_sample, image_index = self.take_sample(image_index)

                if first_sample != running_sample:  # Broken streak
                    if streak_count > 0:
                        image_bytes.append((streak_count << 4) | first_sample)

                    # Reset streak count
                    first_sample, streak_count = running_sample, 1

                else:
                    streak_count += 1

                if streak_count == 15:  # Maximum run-length representable in 4 bits
                    RleLengthCheck(image_bytes, x, y)

                    image_bytes.append((streak_count << 4) | first_sample)
                    streak_count = 0

            # About to switch lines
            if streak_count > 0:
                RleLengthCheck(image_bytes, self.Height - 1, y)

                image_bytes.append((streak_count << 4) | first_sample)

        return struct.pack("!HHH", self.Width, self.Height, len(image_bytes)) + image_bytes


# TODO: move to tests/

color0_icon = BandIcon(Width=48, Height=48, IconData=b"\x00" * (48 * 48 // 2))
color0_icon.EncodeTileIconRle()

color1_icon = BandIcon(Width=48, Height=48, IconData=b"\x11" * (48 * 48 // 2))
color1_icon.EncodeTileIconRle()

color01010101_icon = BandIcon(Width=48, Height=48, IconData=b"\x01" * (48 * 48 // 2))
try:
    color01010101_icon.EncodeTileIconRle()
except BandIconException:
    logging.debug("Too much entropy in alternating image 01")

color00110011_icon = BandIcon(Width=48, Height=48, IconData=b"\x00\x11" * (48 * 48 // 4))
try:
    color00110011_icon.EncodeTileIconRle()
except BandIconException:
    logging.debug("Too much entropy in alternating image 00 11")

color000111_icon = BandIcon(Width=48, Height=48, IconData=b"\x00\x01\x11" * (48 * 48 // 6))
color000111_icon.EncodeTileIconRle()
