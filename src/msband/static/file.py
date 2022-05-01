from msband.sugar import IntEnumAdapter, EnumBase


class FileIndex(EnumBase):
    Config = 0x01
    Ephemeris = 0x02
    UnitTest = 0x03
    Profile = 0x04
    SystemSettings = 0x05
    Instrumentation = 0x0C
    TimeZones = 0x35
    WorkoutPlan = 0x47
    CrashDump = 0x48
    EndOfList = 0x49


FileIndexAdapter = IntEnumAdapter(FileIndex)
