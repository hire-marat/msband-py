import enum
import itertools
import uuid
import logging
import construct
from PIL import Image
import datetime as dt
from construct import (
    this,
    Int8ul,
    Int16ul,
    Int32ul,
    Int64ul,
    Flag,
    Adapter,
    PaddedString,
    Pass,
    If,
    Padded,
    Default,
    Bytes,
)


EPOCH = dt.datetime(1601, 1, 1, tzinfo=dt.timezone.utc)


class BandTime(Adapter):
    def _decode(self, obj: int, context, path) -> dt.datetime:
        return EPOCH + dt.timedelta(microseconds=obj // 10)

    def _encode(self, date: dt.datetime, context, path) -> int:
        if date > dt.datetime.max.replace(tzinfo=dt.timezone.utc):
            raise ValueError(f"Date {date} too far in the future to be encoded")

        if date < EPOCH:
            raise ValueError(f"Date {date} too far in the past to be encoded")

        if date.year < 2012:
            logging.warning("Band doesn't like to exist before 2012, you may get an error")

        return int((date - EPOCH).total_seconds() * 10000000)


class BoolAdapter(Adapter):
    def _encode(self, obj, context, path):
        return obj

    def _decode(self, obj, context, path):
        return bool(obj)


class GUIDAdapter(Adapter):
    def _encode(self, guid: uuid.UUID, context, path):
        return guid.bytes

    def _decode(self, guid: bytes, context, path):
        return uuid.UUID(bytes=guid)  # TODO: verify this


class MeTileAdapter(Adapter):
    width: int
    height: int

    def __init__(self, subcon, width: int, height: int):
        super().__init__(subcon)
        self.width = width
        self.height = height

    def _encode(self, image: Image, context, path):
        # No packer found from RGB to BGR;16
        # return image.tobytes("raw", "BGR;16")

        rgb = image.tobytes("raw", "RGB")
        r = itertools.islice(rgb, 0, None, 3)
        g = itertools.islice(rgb, 1, None, 3)
        b = itertools.islice(rgb, 2, None, 3)

        bgr = bytearray(
            byte
            for r_value, g_value, b_value in zip(r, g, b)
            for byte in (
                ((g_value << 3) & 0b11100000) | (b_value >> 3 & 0b00011111),
                (r_value & 0b11111000) | ((g_value >> 2) >> 3 & 0b00000111),
            )
        )

        return b"" + bgr

    def _decode(self, image: bytes, context, path):
        return Image.frombytes("RGB", (self.width, self.height), image, "raw", "BGR;16")


ARGB = Int32ul

TileData = Padded(
    16 + 4 + 4 + 2 + 2 + 60,
    construct.Struct(
        "GUID" / GUIDAdapter(Bytes(16)),
        "Order" / Int32ul,
        "ThemeColor" / Int32ul,
        "NameLength" / Default(Int16ul, construct.len_(this.TileName)),
        "SettingsMask" / Int16ul,
        "TileName" / PaddedString(this.NameLength, "u16"),
        "OwnerGUID" / GUIDAdapter(Bytes(16)),
    ),
)  # TODO: verify this


BandSystemTime = construct.Struct(
    "Year" / Int16ul,
    "Month" / Int16ul,
    "DayOfWeek" / Int16ul,
    "Day" / Int16ul,
    "Hour" / Int16ul,
    "Minute" / Int16ul,
    "Second" / Int16ul,
    "Milliseconds" / Int16ul,
)


Version = construct.Struct(
    "Major" / Int16ul,
    "Minor" / Int16ul,
    "Revision" / Int32ul,
    "Build" / Int32ul,
    "Debug" / Flag,
)

PROFILE_SIZE = 397  # is it???
# UserProfile.SerializeAppDataToBand
Profile = Padded(
    PROFILE_SIZE,
    construct.Struct(
        "Header" / Pass,
        "Birthday" / BandTime(Int64ul),
        "Weight" / Int32ul,
        "Height" / Int16ul,
        "IsFemale" / Flag,
        "DeviceName" / PaddedString(32, "u16"),
        "LocaleSettings" / Pass,
        "Metric" / Flag,
        "Telemetry" / Flag,
        "HwagChangeTime" / If(this.Header.Version == 2, BandTime(Int64ul)),
        "HwagChangeAgent" / If(this.Header.Version == 2, Int8ul),
        "DeviceNameChangeTime" / If(this.Header.Version == 2, BandTime(Int64ul)),
        "DeviceNameChangeAgent" / If(this.Header.Version == 2, Int8ul),
        "LocaleSettingsChangeTime" / If(this.Header.Version == 2, BandTime(Int64ul)),
        "LocaleSettingsChangeAgent" / If(this.Header.Version == 2, Int8ul),
        "LanguageChangeTime" / If(this.Header.Version == 2, BandTime(Int64ul)),
        "LanguageChangeAgent" / If(this.Header.Version == 2, Int8ul),
    ),
)


class FirmwareApp(enum.IntEnum):
    OneBL = 1
    TwoUp = 2
    App = 3
    UpApp = 4
    Invalid = 255


class FirmwareSdkCheckPlatform(enum.IntEnum):
    WindowsPhone = 1
    Windows = 2
    Desktop = 3


class BandType(enum.IntEnum):
    Cargo = 1
    Envoy = 2
