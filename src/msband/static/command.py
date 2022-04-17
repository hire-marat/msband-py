import typing
import construct
import dataclasses
from msband.static.facility import Facility, FacilityAdapter
from msband.static import (
    ArgbStruct,
    TileData,
    BoolAdapter,
    Bytes,
    GUIDAdapter,
    GUIDStringAdapter,
    TileSettings,
    Version,
    FirmwareApp,
    FirmwareSdkCheckPlatform,
    BandTime,
    BandSystemTime,
    PUSH_SERVICE,
)
from construct import (
    this,
    Pass,
    Default,
    Computed,
    Enum,
    Flag,
    Int8ul,
    Int16ul,
    Int32ul,
    Int64ul,
    Array,
    Padded,
    PaddedString,
    Prefixed,
    Const,
    GreedyBytes,
    PrefixedArray,
)

COMMAND_PACKET = 12025  # F9 2E


@dataclasses.dataclass(frozen=True)
class Command:
    Facility: Facility
    Code: int
    Transferless: bool

    Name: typing.Optional[str] = None
    DataLength: typing.Optional[int] = None
    Arguments: typing.Optional[typing.Dict[str, construct.Construct]] = None
    Transfer: typing.Optional[typing.Dict[str, construct.Construct]] = None
    Response: typing.Optional[construct.Construct] = None

    from_name: typing.ClassVar = typing.cast(typing.Dict[str, "Command"], {})
    from_bytes: typing.ClassVar = typing.cast(typing.Dict[bytes, "Command"], {})
    from_int: typing.ClassVar = typing.cast(typing.Dict[int, "Command"], {})
    from_fields: typing.ClassVar = typing.cast(
        typing.Dict[typing.Tuple[Facility, int, bool], "Command"], {}
    )
    all: typing.ClassVar = typing.cast(typing.List["Command"], [])

    struct: typing.ClassVar = construct.Struct(
        "Code" / Default(Pass, 0),
        "Transferless" / Default(Pass, False),
        "_lower" / Default(Int8ul, this.Code & 0x7F | (this.Transferless & 0b1) << 7),
        "Code" / Computed(this._lower & 0x7F),
        "Transferless" / BoolAdapter(Computed((this._lower & 0x80) >> 7)),
        "Facility" / FacilityAdapter(Int8ul),
    )

    packet_struct = (
        construct.Struct(Const(COMMAND_PACKET, Int16ul))
        + struct
        + construct.Struct(
            "DataLength" / Int32ul,
            "Arguments" / GreedyBytes,
        )
    )

    @typing.overload
    @staticmethod
    def get(
        item: typing.Union[
            str, bytes, int, typing.Tuple[typing.Union[Facility, int], int, bool]
        ] = None,
        facility: typing.Literal[None] = None,
        code: typing.Literal[None] = None,
        tx: typing.Literal[None] = None,
    ) -> "Command":
        ...

    @typing.overload
    @staticmethod
    def get(
        item: typing.Literal[None] = None,
        facility: typing.Union[Facility, int] = None,
        code: int = None,
        tx: bool = None,
    ) -> "Command":
        ...

    @staticmethod
    def get(
        item: typing.Optional[
            typing.Union[str, bytes, int, typing.Tuple[typing.Union[Facility, int], int, bool]]
        ] = None,
        facility: typing.Optional[typing.Union[Facility, int]] = None,
        code: typing.Optional[int] = None,
        tx: typing.Optional[bool] = None,
    ):
        if isinstance(item, str):
            return Command.from_name[item]

        if isinstance(item, bytes):
            if len(item) != 2:
                raise ValueError(
                    f"Command length is 2 bytes, yet {item[:16]}{'...' if len(item)>16 else ''} was passed"
                )
            return Command.from_bytes[item]

        if isinstance(item, int):
            if item > 0xFFFF:
                raise ValueError(
                    f"Command length is 2 bytes, 0xFFFF/{0xFFFF} at most, yet {item} was passed"
                )
            return Command.from_int[item]

        if isinstance(item, tuple):
            if len(item) != 3:
                raise ValueError(
                    f"Command lookup is (facility, code, tx), yet a tuple of length {len(item)} was passed (instead of 3)"
                )
            facility, code, tx = item

        if facility is None:
            raise ValueError(f"facility should not be None")

        if code is None:
            raise ValueError(f"code should not be None")

        if tx is None:
            raise ValueError(f"tx should not be None")

        return Command.from_fields[facility, code, tx]

    def __str__(self):
        if self.Name:
            return self.Name
        else:
            return f"{self.Facility.name} {self.Code} (TX.{self.Transferless})"

    def __repr__(self):
        return str(self)

    def __hash__(self):
        return hash((self.Facility, self.Code, self.Transferless))

    def __post_init__(self):
        as_bytes = self.struct.build(vars(self))
        self.from_bytes[as_bytes] = self

        as_int = Int16ul.parse(as_bytes)
        self.from_int[as_int] = self

        if self.Name is not None:
            self.from_name[self.Name] = self

        key = self.Facility, self.Code, self.Transferless
        int_key = int(self.Facility), self.Code, self.Transferless
        self.from_fields[key] = self
        self.from_fields[int_key] = self

        self.all.append(self)

        if self.DataLength is None:
            if self.Transferless:
                if self.Response:
                    try:
                        object.__setattr__(self, "DataLength", self.Response.sizeof())
                    except construct.SizeofError:
                        pass
            else:
                if self.Transfer:
                    try:
                        object.__setattr__(
                            self, "DataLength", construct.Sequence(**self.Transfer).sizeof()
                        )
                    except construct.SizeofError:
                        pass

    @staticmethod
    def parse_command_packet(data: bytes):
        parsed = Command.packet_struct.parse(data)
        key = parsed.Facility, parsed.Code, parsed.Transferless
        return Command.from_fields[key], parsed.DataLength, parsed.Arguments

    def build_command_packet(
        self, **kwargs
    ) -> typing.Tuple[bytes, int, typing.Optional[bytearray]]:

        DataLength = kwargs.get("DataLength") or self.DataLength

        # Arguments
        arguments_prototype = kwargs.get("Arguments") or self.Arguments

        argument_bytes = bytearray()
        if arguments_prototype is not None:

            for argument_name, subcon in arguments_prototype.items():
                if isinstance(subcon, Const):
                    argument_bytes.extend(subcon.build(None))
                    continue

                if argument_name not in kwargs:
                    raise TypeError(f"{argument_name} must be provided as an argument for {self}")

                argument_bytes.extend(subcon.build(kwargs[argument_name]))

        # Transfer
        transfer_prototype = kwargs.get("Transfer") or self.Transfer

        if not self.Transferless:
            if transfer_prototype is None:
                raise TypeError(f"Transfer must be provided as an argument for {self}")

        transfer_bytes = None
        if transfer_prototype is not None:
            transfer_bytes = bytearray()

            for argument_name, subcon in transfer_prototype.items():
                if isinstance(subcon, Const):
                    transfer_bytes.extend(subcon.build(None))
                    continue

                if argument_name not in kwargs:
                    raise TypeError(f"{argument_name} must be provided as an argument for {self}")

                transfer_bytes.extend(subcon.build(kwargs[argument_name]))

            DataLength = DataLength or len(transfer_bytes)

        # DataLength check
        if DataLength is None:
            raise TypeError(f"DataLength must be provided as an argument for {self}")

        # Response
        response_struct = kwargs.get("Response") or self.Response

        if response_struct is None:
            raise TypeError(f"Response must be provided as an argument for {self}")

        try:
            response_length = response_struct.sizeof()
        except construct.SizeofError:
            response_length = DataLength

        return (
            self.packet_struct.build(
                dict(vars(self), DataLength=DataLength, Arguments=argument_bytes)
            ),
            response_length,
            transfer_bytes,
        )


CoreModuleGetVersion = Command(
    Facility=Facility.LibraryJutil,
    Code=1,
    Transferless=True,
    Response=Array(
        3,
        construct.Struct(
            "AppName" / PaddedString(5, "u8"),
            "PCBId" / Int8ul,
            "Version" / Version,
        ),
    ),
)

CoreModuleGetUniqueID = Command(
    Facility=Facility.LibraryJutil,
    Code=2,
    Transferless=True,
    Response=Prefixed(
        Int8ul,
        construct.Struct(
            "IdVersion" / Int8ul,
            "Id" / GUIDStringAdapter(PaddedString(32 * 2, "utf_16_le")),
        ),
        includelength=True,
    ),
)

CoreModuleWhoAmI = Command(
    Facility=Facility.LibraryJutil,
    Code=3,
    Transferless=True,
    Response=Enum(Int8ul, FirmwareApp),
)

CoreModuleGetLogVersion = Command(
    Facility=Facility.LibraryJutil,
    Code=5,
    Transferless=True,
    Response=Int16ul,
)

CoreModuleGetApiVersion = Command(
    Facility=Facility.LibraryJutil,
    Code=6,
    Transferless=True,
    Response=Int32ul,
)

CoreModuleSdkCheck = Command(
    Facility=Facility.LibraryJutil,
    Code=7,
    Transferless=False,
    Response=Pass,
    Transfer={
        "Platform": Enum(Int8ul, FirmwareSdkCheckPlatform),
        "Reserved": Int8ul,
        "Three": Const(3, Int16ul),
    },
)

TimeGetUtcTime = Command(
    Facility=Facility.LibraryTime,
    Code=0,
    Transferless=True,
    Response=BandTime(Int64ul),
)

TimeSetUtcTime = Command(
    Facility=Facility.LibraryTime,
    Code=1,
    Transferless=False,
    Transfer={"NewTime": BandTime(Int64ul)},
    Response=Pass,
)

TimeGetLocalTime = Command(
    Facility=Facility.LibraryTime,
    Code=2,
    Transferless=True,
    Response=BandSystemTime,
)

TimeSetTimeZoneFile = Command(
    Facility=Facility.LibraryTime,
    Code=4,
    Transferless=False,
)  # TODO

TimeZoneFileGetVersion = Command(
    Facility=Facility.LibraryTime,
    Code=6,
    Transferless=True,
    Response=Int32ul,
)

LoggerGetChunkData = Command(
    Facility=Facility.LibraryLogger,
    Code=1,
    Transferless=True,
)

LoggerEnableLogging = Command(
    Facility=Facility.LibraryLogger,
    Code=3,
    Transferless=False,
)

LoggerDisableLogging = Command(
    Facility=Facility.LibraryLogger,
    Code=4,
    Transferless=False,
)

LoggerGetChunkCounts = Command(
    Facility=Facility.LibraryLogger,
    Code=9,
    Transferless=True,
    Response=construct.Struct(
        "LoggedChunkCount" / Int32ul,
        "LoggerChunkCount" / Int32ul,
    ),
)

LoggerFlush = Command(
    Facility=Facility.LibraryLogger,
    Code=13,
    Transferless=False,
    Transfer={},
    Response=Pass,
)

LoggerGetChunkRangeMetadata = Command(
    Facility=Facility.LibraryLogger,
    Code=14,
    Transferless=True,
    Arguments={
        "ChunkCount": Int32ul,
    },
    Response=construct.Struct(
        "StartingSeqNumber" / Int32ul,
        "EndingSeqNumber" / Int32ul,
        "ByteCount" / Int32ul,
    ),
)

LoggerGetChunkRangeData = Command(
    Facility=Facility.LibraryLogger,
    Code=15,
    Transferless=True,
    Arguments={
        "StartingSeqNumber": Int32ul,
        "EndingSeqNumber": Int32ul,
        "DataLength": Int32ul,
    },
    Response=GreedyBytes,
)

LoggerDeleteChunkRange = Command(
    Facility=Facility.LibraryLogger,
    Code=16,
    Transferless=False,
    DataLength=0x0C,
    Transfer={
        "StartingSeqNumber": Int32ul,
        "EndingSeqNumber": Int32ul,
        "ByteCount": Int32ul,
    },
    Response=Pass,
)

ProfileGetDataApp = Command(
    Facility=Facility.ModuleProfile,
    Code=6,
    Transferless=True,
)

ProfileSetDataApp = Command(
    Facility=Facility.ModuleProfile,
    Code=7,
    Transferless=False,
)

ProfileGetDataFW = Command(
    Facility=Facility.ModuleProfile,
    Code=8,
    Transferless=True,
)

ProfileSetDataFW = Command(
    Facility=Facility.ModuleProfile,
    Code=9,
    Transferless=False,
)

RemoteSubscriptionSubscribe = Command(
    Facility=Facility.LibraryRemoteSubscription,
    Code=0,
    Transferless=False,
    Transfer={
        "Type": Int8ul,
        "Flag": Const(False, Padded(4, Flag)),
    },
    Response=Pass,
)

RemoteSubscriptionUnsubscribe = Command(
    Facility=Facility.LibraryRemoteSubscription,
    Code=1,
    Transferless=False,
    Transfer={
        "Type": Int8ul,
        "Flag": Const(False, Padded(4, Flag)),
    },
    Response=Pass,
)

RemoteSubscriptionGetDataLength = Command(
    Facility=Facility.LibraryRemoteSubscription,
    Code=2,
    Transferless=True,
)

RemoteSubscriptionGetData = Command(
    Facility=Facility.LibraryRemoteSubscription,
    Code=3,
    Transferless=True,
)

RemoteSubscriptionSubscribeId = Command(
    Facility=Facility.LibraryRemoteSubscription,
    Code=7,
    Transferless=False,
    Transfer={
        "Type": Int8ul,
        "Flag": Const(False, Padded(4, Flag)),
        "GUID": Const(PUSH_SERVICE, GUIDAdapter(Bytes(16))),
    },
    Response=Pass,
)

RemoteSubscriptionUnsubscribeId = Command(
    Facility=Facility.LibraryRemoteSubscription,
    Code=8,
    Transferless=False,
    Transfer={
        "Type": Int8ul,
        "GUID": Const(PUSH_SERVICE, GUIDAdapter(Bytes(16))),
    },
    Response=Pass,
)

Notification = Command(
    Facility=Facility.ModuleNotification,
    Code=0,
    Transferless=False,
)

NotificationProtoBuf = Command(
    Facility=Facility.ModuleNotification,
    Code=5,
    Transferless=False,
)

DynamicAppRegisterApp = Command(
    Facility=Facility.ModuleFireballAppsManagement,
    Code=0,
    Transferless=False,
)

DynamicAppRemoveApp = Command(
    Facility=Facility.ModuleFireballAppsManagement,
    Code=1,
    Transferless=False,
)

DynamicAppRegisterAppIcons = Command(
    Facility=Facility.ModuleFireballAppsManagement,
    Code=2,
    Transferless=False,
)

DynamicAppSetAppTileIndex = Command(
    Facility=Facility.ModuleFireballAppsManagement,
    Code=3,
    Transferless=False,
)

DynamicAppSetAppBadgeTileIndex = Command(
    Facility=Facility.ModuleFireballAppsManagement,
    Code=5,
    Transferless=False,
)

DynamicAppSetAppNotificationTileIndex = Command(
    Facility=Facility.ModuleFireballAppsManagement,
    Code=11,
    Transferless=False,
)

DynamicPageLayoutSet = Command(
    Facility=Facility.ModuleFireballPageManagement,
    Code=0,
    Transferless=False,
)

DynamicPageLayoutRemove = Command(
    Facility=Facility.ModuleFireballPageManagement,
    Code=1,
    Transferless=False,
)

DynamicPageLayoutGet = Command(
    Facility=Facility.ModuleFireballPageManagement,
    Code=2,
    Transferless=True,
)

InstalledAppListGet = Command(
    Facility=Facility.ModuleInstalledAppList,
    Code=0,
    Transferless=True,
)

InstalledAppListSet = Command(
    Facility=Facility.ModuleInstalledAppList,
    Code=1,
    Transferless=False,
    Arguments={
        "Count": Int32ul,
    },
    Transfer={
        "Tiles": PrefixedArray(Int32ul, TileData),
    },
    Response=Pass,
)

InstalledAppListStartStripSyncStart = Command(
    Facility=Facility.ModuleInstalledAppList,
    Code=2,
    Transferless=False,
    Transfer={},
    Response=Pass,
)

InstalledAppListStartStripSyncEnd = Command(
    Facility=Facility.ModuleInstalledAppList,
    Code=3,
    Transferless=False,
    Transfer={},
    Response=Pass,
)  # TODO: verify

InstalledAppListGetDefaults = Command(
    Facility=Facility.ModuleInstalledAppList,
    Code=4,
    Transferless=True,
)

InstalledAppListSetTile = Command(
    Facility=Facility.ModuleInstalledAppList,
    Code=6,
    Transferless=False,
    Transfer={
        "TileData": TileData,
    },
    Response=Pass,
)

InstalledAppListGetTile = Command(
    Facility=Facility.ModuleInstalledAppList,
    Code=7,
    Transferless=True,
)

InstalledAppListGetSettingsMask = Command(
    Facility=Facility.ModuleInstalledAppList,
    Code=13,
    Transferless=True,
)

InstalledAppListSetSettingsMask = Command(
    Facility=Facility.ModuleInstalledAppList,
    Code=14,
    Transferless=False,
    Transfer={
        "GUID": GUIDAdapter(Bytes(16)),
        "SettingsMask": Enum(Int16ul, TileSettings),
    },
    Response=Pass,
)

InstalledAppListEnableSetting = Command(
    Facility=Facility.ModuleInstalledAppList,
    Code=15,
    Transferless=False,
)

InstalledAppListDisableSetting = Command(
    Facility=Facility.ModuleInstalledAppList,
    Code=16,
    Transferless=False,
)

InstalledAppListGetNoImages = Command(
    Facility=Facility.ModuleInstalledAppList,
    Code=18,
    Transferless=True,
)

InstalledAppListGetDefaultsNoImages = Command(
    Facility=Facility.ModuleInstalledAppList,
    Code=19,
    Transferless=True,
)

InstalledAppListGetMaxTileCount = Command(
    Facility=Facility.ModuleInstalledAppList,
    Code=21,
    Transferless=True,
    Response=Int32ul,
)

InstalledAppListGetMaxTileAllocatedCount = Command(
    Facility=Facility.ModuleInstalledAppList,
    Code=22,
    Transferless=True,
    Response=Int32ul,
)

SystemSettingsOobeCompleteClear = Command(
    Facility=Facility.ModuleSystemSettings,
    Code=0,
    Transferless=False,
    Transfer={},
    Response=Pass,
)

SystemSettingsOobeCompleteSet = Command(
    Facility=Facility.ModuleSystemSettings,
    Code=1,
    Transferless=False,
    Transfer={},
    Response=Pass,
)

SystemSettingsFactoryReset = Command(
    Facility=Facility.ModuleSystemSettings,
    Code=7,
    Transferless=True,
)

SystemSettingsGetTimeZone = Command(
    Facility=Facility.ModuleSystemSettings,
    Code=10,
    Transferless=True,
)

SystemSettingsSetTimeZone = Command(
    Facility=Facility.ModuleSystemSettings,
    Code=11,
    Transferless=False,
)

SystemSettingsSetEphemerisFile = Command(
    Facility=Facility.ModuleSystemSettings,
    Code=15,
    Transferless=False,
)

SystemSettingsGetMeTileImageID = Command(
    Facility=Facility.ModuleSystemSettings,
    Code=18,
    Transferless=True,
)

SystemSettingsOobeCompleteGet = Command(
    Facility=Facility.ModuleSystemSettings,
    Code=19,
    Transferless=True,
    Response=Padded(4, Flag),
)

SystemSettingsEnableDemoMode = Command(
    Facility=Facility.ModuleSystemSettings,
    Code=25,
    Transferless=False,
    Transfer={},
    Response=Pass,
)

SystemSettingsDisableDemoMode = Command(
    Facility=Facility.ModuleSystemSettings,
    Code=26,
    Transferless=False,
    Transfer={},
    Response=Pass,
)

SRAMFWUpdateLoadData = Command(
    Facility=Facility.LibrarySRAMFWUpdate,
    Code=0,
    Transferless=False,
    Transfer={
        "UpdateFileStream": GreedyBytes,
    },
)

SRAMFWUpdateBootIntoUpdateMode = Command(
    Facility=Facility.LibrarySRAMFWUpdate,
    Code=1,
    Transferless=False,
    Transfer={},
    Response=Pass,
)

SRAMFWUpdateValidateAssets = Command(
    Facility=Facility.LibrarySRAMFWUpdate,
    Code=2,
    Transferless=True,
)

EFlashRead = Command(
    Facility=Facility.DriverEFlash,
    Code=1,
    Transferless=True,
    Arguments={
        "Address": Int32ul,
        "DataLength": Int32ul,
    },
    Response=GreedyBytes,
)  # TODO: investigate

GpsIsEnabled = Command(
    Facility=Facility.LibraryGps,
    Code=6,
    Transferless=True,
)

GpsEphemerisCoverageDates = Command(
    Facility=Facility.LibraryGps,
    Code=13,
    Transferless=True,
    Response=construct.Struct(
        "From" / BandTime(Int64ul),
        "Until" / BandTime(Int64ul),
    ),
)

FireballUINavigateToScreen = Command(
    Facility=Facility.ModuleFireballUI,
    Code=0,
    Transferless=False,
    Response=Pass,
    Transfer={
        "Screen": Int16ul,
    },
)

FireballUIClearMeTileImage = Command(
    Facility=Facility.ModuleFireballUI,
    Code=6,
    Transferless=False,
)

FireballUISetSmsResponse = Command(
    Facility=Facility.ModuleFireballUI,
    Code=7,
    Transferless=False,
)

FireballUIGetAllSmsResponse = Command(
    Facility=Facility.ModuleFireballUI,
    Code=11,
    Transferless=True,
)

FireballUIReadMeTileImage = Command(
    Facility=Facility.ModuleFireballUI,
    Code=14,
    Transferless=True,
)

FireballUIWriteMeTileImageWithID = Command(
    Facility=Facility.ModuleFireballUI,
    Code=17,
    Transferless=False,
    Arguments={
        "ImageId": Int32ul,
    },
    Transfer={
        "ImageBytes": GreedyBytes,
    },
)

ThemeColorSetFirstPartyTheme = Command(
    Facility=Facility.ModuleThemeColor,
    Code=0,
    Transferless=False,
)

ThemeColorGetFirstPartyTheme = Command(
    Facility=Facility.ModuleThemeColor,
    Code=1,
    Transferless=True,
)

ThemeColorSetCustomTheme = Command(
    Facility=Facility.ModuleThemeColor,
    Code=2,
    Transferless=False,
    Transfer={
        "Base": ArgbStruct,
        "Highlight": ArgbStruct,
        "Lowlight": ArgbStruct,
        "SecondaryText": ArgbStruct,
        "HighContrast": ArgbStruct,
        "Muted": ArgbStruct,
        "GUID": PaddedString(16, "u8"),
    },
)

ThemeColorReset = Command(
    Facility=Facility.ModuleThemeColor,
    Code=4,
    Transferless=False,
    Transfer={},
    Response=Pass,
)

HapticPlayVibrationStream = Command(
    Facility=Facility.LibraryHaptic,
    Code=0,
    Transferless=False,
)

GoalTrackerSet = Command(
    Facility=Facility.ModuleGoalTracker,
    Code=0,
    Transferless=False,
)

FitnessPlansWriteFile = Command(
    Facility=Facility.LibraryFitnessPlans,
    Code=4,
    Transferless=False,
)

GolfCourseFileWrite = Command(
    Facility=Facility.LibraryGolf,
    Code=0,
    Transferless=False,
)

GolfCourseFileGetMaxSize = Command(
    Facility=Facility.LibraryGolf,
    Code=1,
    Transferless=True,
)

OobeSetStage = Command(
    Facility=Facility.ModuleOobe,
    Code=0,
    Transferless=False,
    Transfer={
        "Stage": Int16ul,
    },
)

OobeGetStage = Command(
    Facility=Facility.ModuleOobe,
    Code=1,
    Transferless=True,
    Response=construct.Struct(
        "Stage" / Int16ul,
    ),
)

OobeFinalize = Command(
    Facility=Facility.ModuleOobe,
    Code=2,
    Transferless=False,
    Transfer={},
    Response=Pass,
)

CortanaNotification = Command(
    Facility=Facility.ModuleCortana,
    Code=0,
    Transferless=False,
)

CortanaStart = Command(
    Facility=Facility.ModuleCortana,
    Code=1,
    Transferless=False,
)

CortanaStop = Command(
    Facility=Facility.ModuleCortana,
    Code=2,
    Transferless=False,
)

CortanaCancel = Command(
    Facility=Facility.ModuleCortana,
    Code=3,
    Transferless=False,
)

PersistedAppDataSetRunMetrics = Command(
    Facility=Facility.ModulePersistedApplicationData,
    Code=0,
    Transferless=False,
)

PersistedAppDataGetRunMetrics = Command(
    Facility=Facility.ModulePersistedApplicationData,
    Code=1,
    Transferless=True,
)

PersistedAppDataSetBikeMetrics = Command(
    Facility=Facility.ModulePersistedApplicationData,
    Code=2,
    Transferless=False,
)

PersistedAppDataGetBikeMetrics = Command(
    Facility=Facility.ModulePersistedApplicationData,
    Code=3,
    Transferless=True,
)

PersistedAppDataSetBikeSplitMult = Command(
    Facility=Facility.ModulePersistedApplicationData,
    Code=4,
    Transferless=False,
)

PersistedAppDataGetBikeSplitMult = Command(
    Facility=Facility.ModulePersistedApplicationData,
    Code=5,
    Transferless=True,
)

PersistedAppDataSetWorkoutActivities = Command(
    Facility=Facility.ModulePersistedApplicationData,
    Code=9,
    Transferless=False,
)

PersistedAppDataGetWorkoutActivities = Command(
    Facility=Facility.ModulePersistedApplicationData,
    Code=16,
    Transferless=True,
)

PersistedAppDataSetSleepNotification = Command(
    Facility=Facility.ModulePersistedApplicationData,
    Code=17,
    Transferless=False,
)

PersistedAppDataGetSleepNotification = Command(
    Facility=Facility.ModulePersistedApplicationData,
    Code=18,
    Transferless=True,
)

PersistedAppDataDisableSleepNotification = Command(
    Facility=Facility.ModulePersistedApplicationData,
    Code=19,
    Transferless=False,
)

PersistedAppDataSetLightExposureNotification = Command(
    Facility=Facility.ModulePersistedApplicationData,
    Code=21,
    Transferless=False,
)

PersistedAppDataGetLightExposureNotification = Command(
    Facility=Facility.ModulePersistedApplicationData,
    Code=22,
    Transferless=True,
)

PersistedAppDataDisableLightExposureNotification = Command(
    Facility=Facility.ModulePersistedApplicationData,
    Code=23,
    Transferless=False,
)

GetProductSerialNumber = Command(
    Facility=Facility.LibraryConfiguration,
    Code=8,
    Transferless=True,
    Response=PaddedString(12, "u8"),
)

KeyboardCmd = Command(
    Facility=Facility.LibraryKeyboard,
    Code=0,
    Transferless=False,
)

SubscriptionLoggerSubscribe = Command(
    Facility=Facility.ModuleLoggerSubscriptions,
    Code=0,
    Transferless=False,
)

SubscriptionLoggerUnsubscribe = Command(
    Facility=Facility.ModuleLoggerSubscriptions,
    Code=1,
    Transferless=False,
)

CrashDumpGetFileSize = Command(
    Facility=Facility.DriverCrashDump,
    Code=1,
    Transferless=True,
    Response=Int32ul,
)

CrashDumpGetAndDeleteFile = Command(
    Facility=Facility.DriverCrashDump,
    Code=2,
    Transferless=True,
)

InstrumentationGetFileSize = Command(
    Facility=Facility.ModuleInstrumentation,
    Code=4,
    Transferless=True,
    Arguments={},
    Response=Int32ul,
)

InstrumentationGetFile = Command(
    Facility=Facility.ModuleInstrumentation,
    Code=5,
    Transferless=True,
    Arguments={
        "DataLength": Int32ul,
    },
    Response=GreedyBytes,
)

PersistedStatisticsRunGet = Command(
    Facility=Facility.ModulePersistedStatistics,
    Code=2,
    Transferless=True,
)

PersistedStatisticsWorkoutGet = Command(
    Facility=Facility.ModulePersistedStatistics,
    Code=3,
    Transferless=True,
)

PersistedStatisticsSleepGet = Command(
    Facility=Facility.ModulePersistedStatistics,
    Code=4,
    Transferless=True,
)

PersistedStatisticsGuidedWorkoutGet = Command(
    Facility=Facility.ModulePersistedStatistics,
    Code=5,
    Transferless=True,
)


for name, _command in locals().copy().items():
    if isinstance(_command, Command):
        object.__setattr__(_command, "Name", name)
        Command.from_name[name] = _command
