import construct
from binascii import crc32
from construct import (
    this,
    Const,
    Rebuild,
    Hex,
    Int32ul,
    Int16ul,
    Int8ul,
    Pointer,
    FixedSized,
    Array,
    GreedyBytes,
    CString,
)


CARGO = Const(9, Int8ul)
ENVOY = Const(26, Int8ul)
Device = construct.Select(CARGO, ENVOY)

Version = construct.Struct(
    "Minor" / Int16ul,
    "Major" / Int16ul,
    "Patch" / Int32ul,
)

HeaderlessSection = construct.Struct(
    "_Data" / GreedyBytes,
)

Language = construct.Struct(
    "_Count" / Int32ul,
    "_Pointers" / Array(this._Count, Int32ul),
    "_Strings" / Array(this._Count, CString("utf_16_le")),
)

SectionHeader = construct.Struct(
    "Incantation" / Hex(Int32ul),
    "Version" / Version,
    "Base" / Hex(Int32ul),
    "Size" / Hex(Int32ul),
    "Stack" / Hex(Int32ul),
    "CRC" / Hex(Int32ul),
    "InterruptVector" / Hex(Int32ul),
    "Unk" / Hex(Int32ul),
    "Unk2" / Hex(Int32ul),
    "Unk3" / Hex(Int16ul),
    "Device" / Device,
    "Unk4" / Hex(Int8ul),
    "Unk5" / Hex(Int32ul),
)

Section = SectionHeader + HeaderlessSection
LanguageSection = SectionHeader + Language
# LanguageSection = HeaderlessSection

SectionEntry = construct.Struct(
    "Id" / Hex(Int16ul),
    "Pointer" / Hex(Int32ul),
    "Size" / Hex(Int32ul),
    "Section"
    / Pointer(
        this.Pointer,
        FixedSized(
            this.Size,
            construct.Switch(
                this.Id,
                {
                    0xC002: HeaderlessSection,
                    0x1C: LanguageSection,
                    0x1D: LanguageSection,
                    0x1E: LanguageSection,
                    0x1F: LanguageSection,
                    0x20: LanguageSection,
                    0x21: LanguageSection,
                    0x22: LanguageSection,
                    0x23: LanguageSection,
                    0x24: LanguageSection,
                    0x25: LanguageSection,
                    0x26: LanguageSection,
                    0x27: LanguageSection,
                    0x28: LanguageSection,
                    0x29: LanguageSection,
                    0x2A: LanguageSection,
                    0x2B: LanguageSection,
                    # 0x2B: HeaderlessSection,
                },
                default=Section,
            ),
        ),
    ),
)

Header = construct.Struct(
    "Magic" / Hex(Int16ul),
    "UnkB" / Hex(Int8ul),
    "Device" / Device,
    "UnkB2" / Hex(Int8ul),
    "Unk" / Hex(Int32ul),
    "Unk2" / Hex(Int32ul),
    "Unk3" / Hex(Int16ul),
    "_SectionCount" / Rebuild(Int32ul, construct.len_(this.Sections)),
    "Size" / Hex(Int32ul),
    "CRC" / Hex(Int32ul),
    "Sections" / Array(this._SectionCount, SectionEntry),
)


def sign_section(section):
    section.CRC = 0
    section.CRC = (
        crc32(SectionHeader.build(section) + section._Data, 0xFFFFFFFF) ^ 0xFFFFFFFF
    ) & 0xFFFFFFFF
    return


def split_sections(firmware_path):
    firmware = Header.parse_file(firmware_path)

    for section in firmware.Sections:
        if hasattr(section.Section, "_Strings"):
            continue
        firmware_path.with_suffix(f".{section.Id:X}.bin").write_bytes(section.Section._Data)
        if hasattr(section.Section, "Start"):
            firmware_path.with_suffix(f".{section.Id:X}.head.bin").write_bytes(
                SectionHeader.build(section.Section) + section.Section._Data
            )

    return firmware
