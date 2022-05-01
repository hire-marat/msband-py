from msband.sugar import IntEnumAdapter, EnumBase


class Facility(EnumBase):
    Mystery = 0xA4

    Null = Min = Invalid = 0x00

    ReservedBase = 0x01
    ReservedEnd = 0x1F

    DriverDma = DriversBase = 0x20
    DriverBtle = 0x21
    DriverPdb = 0x22
    DriverI2c = 0x23
    DriverAdc = 0x24
    DriverGpio = 0x25
    DriverDac = 0x26
    DriverAnalogMgr = 0x27
    DriverRtc = 0x28
    DriverMotor = 0x29
    DriverDisplay = 0x2B
    DriverUartAsync = 0x2C
    DriverPmu = 0x2D
    DriverExternalRam = 0x2E
    DriverAls = 0x2F
    DriverTimers = 0x30
    DriverFlexBus = 0x31
    DriverSpi = 0x32
    DriverEFlash = 0x33
    DriverPwm = 0x34
    DriverCrc = 0x35
    DriverPFlash = 0x36
    DriverFpu = 0x37
    DriverWatchDog = 0x38
    DriverCoreModule = 0x39
    DriverCrashDump = 0x3A
    DriverUsb = 0x3B
    DriverMmcau = 0x3C
    DriversEnd = 0x6F

    LibraryDebug = LibrariesBase = 0x70
    LibraryRuntime = 0x71
    LibraryUsbCmdProtocol = 0x72
    LibraryBTPS = 0x73
    LibraryTouch = 0x74
    LibraryTime = 0x75
    LibraryJutil = 0x76
    LibraryHRManager = 0x77
    LibraryConfiguration = 0x78
    LibraryButton = 0x79
    LibraryBacklight = 0x7A
    LibraryMotion = 0x7B
    LibraryActMon = 0x7C
    LibraryBattery = 0x7D
    LibraryGps = 0x7E
    LibraryHRLed = 0x7F
    LibraryDfu = 0x80
    LibraryHeartRate = 0x81
    LibraryMicrophone = 0x83
    LibraryGsr = 0x84
    LibraryUV = 0x85
    LibrarySkinTemp = 0x86
    LibraryAmbTemp = 0x87
    LibraryPedometer = 0x88
    LibraryCalories = 0x89
    LibraryDistance = 0x8A
    LibraryAlgoMath = 0x8B
    LibraryLogger = 0x8C
    LibraryPeg = 0x8D
    LibraryFile = 0x8E
    LibraryRemoteSubscription = 0x8F
    LibraryPower = 0x90
    LibraryUVExposure = 0x91
    LibraryMinuteTimer = 0x92
    LibraryRecovery = 0x93
    LibrarySubscriptionBase = 0x94
    LibraryDateChangeSubscription = 0x95
    LibraryHREstimator = 0x96
    LibraryUSBConnection = 0x97
    LibrarySRAMFWUpdate = 0x98
    LibraryAutoBrightness = 0x99
    LibraryHaptic = 0x9A
    LibraryFitnessPlans = 0x9B
    LibrarySleepRecovery = 0x9C
    LibraryFirstBeat = 0x9D
    LibraryAncsNotificationCache = 0x9E
    LibraryKeyboard = 0x9F
    LibraryHrAccelSync = 0xA0
    LibraryGolf = 0xA1
    ModuleOobe = 0xAD
    LibrariesEnd = 0xBF

    ModuleMain = ModulesBase = 0xC0
    ModuleBehavior = 0xC1
    ModuleFireballTransportLayer = 0xC2
    ModuleFireballUI = 0xC3
    ModuleFireballUtilities = 0xC4
    ModuleProfile = 0xC5
    ModuleLoggerSubscriptions = 0xC6
    ModuleFireballTilesModels = 0xC7
    ModulePowerManager = 0xC8
    ModuleHrPowerManager = 0xC9
    ModuleSystemSettings = 0xCA
    ModuleFireballHardwareManager = 0xCB
    ModuleNotification = 0xCC
    ModuleFtlTouchManager = 0xCD
    ModulePersistedStatistics = 0xCE
    ModuleAlgorithms = 0xCF
    ModulePersistedApplicationData = 0xD0
    ModuleDeviceContact = 0xD1
    ModuleInstrumentation = 0xD2
    ModuleFireballAppsManagement = 0xD3
    ModuleInstalledAppList = 0xD4
    ModuleFireballPageManagement = 0xD5
    ModuleUnitTests = 0xD6
    ModuleBatteryGauge = 0xD7
    ModuleThemeColor = 0xD8
    ModuleGoalTracker = 0xD9
    ModuleKfrost = 0xDA
    ModulePal = 0xDB
    ModuleGestures = 0xDC
    ModuleCortana = 0xDD
    ModuleVoicePush = 0xDE
    ModulesEnd = 0xDF

    ApplicationMain = ApplicationsBase = 0xE0
    Application1BL = 0xE1
    Application2UP = 0xE2
    ApplicationsEnd = 0xEF

    Reserved2Base = 0xF0
    Reserved2End = Max = 0xFF


FacilityAdapter = IntEnumAdapter(Facility)
