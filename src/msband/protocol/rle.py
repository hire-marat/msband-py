import struct
import typing
import logging
import dataclasses


class BandIconException(Exception):
    ...


def RleLengthCheck(image_bytes: bytearray, x: int, y: int):
    if len(image_bytes) > 1024 - 6:
        logging.debug(image_bytes)
        raise BandIconException(
            f"Run Length Encoding Failure. Length ({len(image_bytes)}) exceeded allowed bytes at {x}, {y}."
        )


@dataclasses.dataclass
class BandIcon:
    Width: int
    Height: int
    IconData: bytes

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


color0_icon = BandIcon(Width=48, Height=48, IconData=b"\x00" * (48 * 48 // 2))
color0_icon.EncodeTileIconRle()

color1_icon = BandIcon(Width=48, Height=48, IconData=b"\x11" * (48 * 48 // 2))
color1_icon.EncodeTileIconRle()

color01010101_icon = BandIcon(Width=48, Height=48, IconData=b"\x01" * (48 * 48 // 2))
try:
    color01010101_icon.EncodeTileIconRle()
except BandIconException:
    logging.warning("Too much entropy in alternating image 01")

color00110011_icon = BandIcon(Width=48, Height=48, IconData=b"\x00\x11" * (48 * 48 // 4))
try:
    color00110011_icon.EncodeTileIconRle()
except BandIconException:
    logging.warning("Too much entropy in alternating image 00 11")

color000111_icon = BandIcon(Width=48, Height=48, IconData=b"\x00\x01\x11" * (48 * 48 // 6))
color000111_icon.EncodeTileIconRle()
