import construct
from enum import Enum, IntEnum
from msband.static import BoolAdapter
from msband.static.facility import Facility, FacilityAdapter
from construct import this, Int16ul, Const, Default, Computed, Pass, Adapter


class StatusAdapter(Adapter):
    def _encode(self, obj, context, path):
        return obj

    def _decode(self, obj, context, path):
        return Status(
            (context.Customer, Severity(context.Severity), context.Facility, context.Code)
        )


STATUS_PACKET = 42750  # FE A6


StatusPacket = construct.Struct(
    Const(STATUS_PACKET, Int16ul),
    "Code" / Int16ul,
    "Facility" / Default(Pass, 0),
    "Reserved" / Default(Pass, 0),
    "Severity" / Default(Pass, 0),
    "_higher" / Default(Int16ul, this.Facility | this.Reserved << 11 | this.Severity << 15),
    "Facility" / FacilityAdapter(Computed((this._higher & 0x07FF))),
    "Reserved" / Computed((this._higher & 0x7800) >> 11),
    "Customer" / BoolAdapter(Computed((this.Reserved & 0b0100) >> 2)),
    "Severity" / BoolAdapter(Computed((this._higher & 0x8000) >> 15)),
    "Status" / StatusAdapter(Pass),
)


class Severity(IntEnum):
    Null = 0
    Error = 1


class Status(Enum):
    OobeError0 = (True, Severity.Error, Facility.ModuleOobe, 0)
    OobeError8 = (True, Severity.Error, Facility.ModuleOobe, 8)

    BadDataLength = (True, Severity.Error, Facility.Mystery, 1)

    # bool Customer
    # bool Severe
    # int Facility
    # int Code

    Success = (False, Severity.Null, Facility.Null, 0)

    DmaPending = (True, Severity.Null, Facility.DriverDma, 0)

    DmaChannelBusy = (True, Severity.Error, Facility.DriverDma, 0)

    DmaNoChanInit = (True, Severity.Error, Facility.DriverDma, 1)

    DmaOddSourceAddr = (True, Severity.Error, Facility.DriverDma, 2)

    DmaOddDestAddr = (True, Severity.Error, Facility.DriverDma, 3)

    DmaOddByteCount = (True, Severity.Error, Facility.DriverDma, 4)

    DmaDestBusErr = (True, Severity.Error, Facility.DriverDma, 5)

    DmaSourceBusErr = (True, Severity.Error, Facility.DriverDma, 6)

    DmaOddSgaAddr = (True, Severity.Error, Facility.DriverDma, 7)

    DmaCiterErr = (True, Severity.Error, Facility.DriverDma, 8)

    DmaDoffErr = (True, Severity.Error, Facility.DriverDma, 9)

    DmaSoffErr = (True, Severity.Error, Facility.DriverDma, 10)

    DmaCancelled = (True, Severity.Error, Facility.DriverDma, 11)

    DmaUnknown = (True, Severity.Error, Facility.DriverDma, 12)

    DmaBadChannel = (True, Severity.Error, Facility.DriverDma, 13)

    DmaBadMuxIndex = (True, Severity.Error, Facility.DriverDma, 14)

    DmaBadSourceType = (True, Severity.Error, Facility.DriverDma, 15)

    DmaBadDestType = (True, Severity.Error, Facility.DriverDma, 16)

    DmaByteCountTooHigh = (True, Severity.Error, Facility.DriverDma, 17)

    DisplayMissingDisplay = (True, Severity.Error, Facility.DriverDisplay, 0)

    DisplayAlreadyInitialized = (True, Severity.Error, Facility.DriverDisplay, 1)

    DisplayInvalidPowerTransition = (True, Severity.Error, Facility.DriverDisplay, 2)

    DisplayIsOff = (True, Severity.Error, Facility.DriverDisplay, 3)

    DisplayBltPending = (True, Severity.Error, Facility.DriverDisplay, 4)

    DisplayDmaInProgress = (True, Severity.Error, Facility.DriverDisplay, 5)

    DisplayTearingEffectIsrWithBlt = (True, Severity.Null, Facility.DriverDisplay, 6)

    DisplayTearingEffectIsrWithoutBlt = (True, Severity.Null, Facility.DriverDisplay, 7)

    BtleResetFailed = (True, Severity.Error, Facility.DriverBtle, 0)

    BtleGpioInitFailed = (True, Severity.Error, Facility.DriverBtle, 1)

    BtleInvalidArg = (True, Severity.Error, Facility.DriverBtle, 2)

    BtleSetRftx = (True, Severity.Error, Facility.DriverBtle, 3)

    BtleNoResponse = (True, Severity.Error, Facility.DriverBtle, 4)

    BtleUartTxTimeout = (True, Severity.Error, Facility.DriverBtle, 5)

    BtleUartRxTimeout = (True, Severity.Error, Facility.DriverBtle, 6)

    BtleStackInitFailed = (True, Severity.Error, Facility.DriverBtle, 7)

    PdbInvalidParam = (True, Severity.Error, Facility.DriverPdb, 0)

    PdbNotInitialized = (True, Severity.Error, Facility.DriverPdb, 1)

    PdbAlreadyInitialized = (True, Severity.Error, Facility.DriverPdb, 2)

    PdbNotEnabled = (True, Severity.Error, Facility.DriverPdb, 3)

    PdbSequenceError = (True, Severity.Error, Facility.DriverPdb, 4)

    AdcCalibrationError = (True, Severity.Error, Facility.DriverAdc, 0)

    AdcModuleBusy = (True, Severity.Error, Facility.DriverAdc, 1)

    AdcConversationStarted = (True, Severity.Null, Facility.DriverAdc, 2)

    AdcReadyForTrigger = (True, Severity.Null, Facility.DriverAdc, 3)

    AdcConversationComplete = (True, Severity.Null, Facility.DriverAdc, 4)

    AdcInitComplete = (True, Severity.Null, Facility.DriverAdc, 5)

    I2cTransactionPending = (False, Severity.Null, Facility.DriverI2c, 0)

    I2cNackReceived = (False, Severity.Error, Facility.DriverI2c, 1)

    I2cArbitrationLost = (False, Severity.Error, Facility.DriverI2c, 2)

    I2cClockHoldTimeout = (False, Severity.Error, Facility.DriverI2c, 3)

    I2cEnqueueBadModule = (False, Severity.Error, Facility.DriverI2c, 4)

    I2cEnqueueUninitialized = (False, Severity.Error, Facility.DriverI2c, 5)

    I2cEnqueueNullBuffer = (False, Severity.Error, Facility.DriverI2c, 6)

    I2cEnqueueReadHasZeroSize = (False, Severity.Error, Facility.DriverI2c, 7)

    I2cEnqueueDuplicateTransaction = (False, Severity.Error, Facility.DriverI2c, 8)

    I2cTransactionTimeout = (False, Severity.Error, Facility.DriverI2c, 9)

    I2cNotSupported = (False, Severity.Error, Facility.DriverI2c, 10)

    I2cNullTransaction = (False, Severity.Error, Facility.DriverI2c, 11)

    I2cEnqueueNullTransaction = (False, Severity.Error, Facility.DriverI2c, 12)

    I2cTransactionCorrupted = (False, Severity.Error, Facility.DriverI2c, 13)

    I2cBusUnrecoverable = (False, Severity.Error, Facility.DriverI2c, 14)

    GpioInvalidSignal = (True, Severity.Error, Facility.DriverGpio, 0)

    GpioInvalidAlternate = (True, Severity.Error, Facility.DriverGpio, 1)

    GpioTooManyInterrupts = (True, Severity.Error, Facility.DriverGpio, 2)

    GpioInvalidInterruptFlag = (True, Severity.Error, Facility.DriverGpio, 3)

    GpioPortFilterConflict = (True, Severity.Error, Facility.DriverGpio, 4)

    GpioSignalFilterUnavailable = (True, Severity.Error, Facility.DriverGpio, 5)

    MotorModuleBusy = (True, Severity.Error, Facility.DriverMotor, 0)

    MotorPowerLevelLow = (True, Severity.Null, Facility.DriverMotor, 1)

    DacNotInitialized = (True, Severity.Error, Facility.DriverDac, 1)

    DacAlreadyInitialized = (True, Severity.Error, Facility.DriverDac, 2)

    DacVrefError = (True, Severity.Error, Facility.DriverDac, 3)

    RtcNullArgument = (True, Severity.Error, Facility.DriverRtc, 0)

    RtcInvalidTime = (True, Severity.Error, Facility.DriverRtc, 1)

    RtcTimeSyncDisabled = (True, Severity.Error, Facility.DriverRtc, 2)

    AnalogMgrModuleBusy = (True, Severity.Error, Facility.DriverAnalogMgr, 0)

    AnalogMgrInitialized = (True, Severity.Null, Facility.DriverAnalogMgr, 1)

    AnalogMgrInitializationStarted = (True, Severity.Null, Facility.DriverAnalogMgr, 2)

    AnalogMgrDeinitialized = (True, Severity.Null, Facility.DriverAnalogMgr, 3)

    AnalogMgrNotInitialized = (True, Severity.Error, Facility.DriverAnalogMgr, 4)

    AnalogMgrWriteCountInvalid = (True, Severity.Error, Facility.DriverAnalogMgr, 5)

    AnalogMgrReadCountInvalid = (True, Severity.Error, Facility.DriverAnalogMgr, 6)

    AnalogMgrWriteStarted = (True, Severity.Null, Facility.DriverAnalogMgr, 7)

    AnalogMgrWriteSuccessful = (True, Severity.Null, Facility.DriverAnalogMgr, 8)

    AnalogMgrReadStarted = (True, Severity.Null, Facility.DriverAnalogMgr, 9)

    AnalogMgrReadSuccessful = (True, Severity.Null, Facility.DriverAnalogMgr, 10)

    AnalogMgrSubscribed = (True, Severity.Null, Facility.DriverAnalogMgr, 11)

    AnalogMgrSubscriptionDataValid = (True, Severity.Null, Facility.DriverAnalogMgr, 12)

    AnalogMgrResetAlert = (True, Severity.Error, Facility.DriverAnalogMgr, 13)

    AnalogMgrBootloaderModeAlert = (True, Severity.Error, Facility.DriverAnalogMgr, 14)

    AnalogMgrNullParameter = (True, Severity.Error, Facility.DriverAnalogMgr, 15)

    AnalogMgrWriteFailed = (True, Severity.Error, Facility.DriverAnalogMgr, 16)

    AnalogMgrReadFailed = (True, Severity.Error, Facility.DriverAnalogMgr, 17)

    AnalogMgrResetReasonUpdateSuccess = (True, Severity.Null, Facility.DriverAnalogMgr, 18)

    AnalogMgrResetReasonUpdateFailure = (True, Severity.Null, Facility.DriverAnalogMgr, 19)

    AnalogMgrBootloaderCommandWriteStageFailed = (
        True,
        Severity.Error,
        Facility.DriverAnalogMgr,
        20,
    )

    AnalogMgrBootloaderCommandReadStageFailed = (
        True,
        Severity.Error,
        Facility.DriverAnalogMgr,
        21,
    )

    AnalogMgrProgramFlashRowWriteStageFailed = (True, Severity.Error, Facility.DriverAnalogMgr, 22)

    AnalogMgrProgramFlashRowReadStageFailed = (True, Severity.Error, Facility.DriverAnalogMgr, 23)

    AnalogMgrVerifyFlashRowWriteStageFailed = (True, Severity.Error, Facility.DriverAnalogMgr, 24)

    AnalogMgrVerifyFlashRowReadStageFailed = (True, Severity.Error, Facility.DriverAnalogMgr, 25)

    AnalogMgrVerifyApplicationWriteStageFailed = (
        True,
        Severity.Error,
        Facility.DriverAnalogMgr,
        26,
    )

    AnalogMgrVerifyApplicationReadStageFailed = (
        True,
        Severity.Error,
        Facility.DriverAnalogMgr,
        27,
    )

    PmuInitialized = (True, Severity.Null, Facility.DriverPmu, 0)

    PmuInitializationFailed = (True, Severity.Error, Facility.DriverPmu, 1)

    PmuWriteSynchronousCompleted = (True, Severity.Null, Facility.DriverPmu, 2)

    PmuWriteSynchronousFailed = (True, Severity.Error, Facility.DriverPmu, 3)

    PmuReadSynchronousCompleted = (True, Severity.Null, Facility.DriverPmu, 4)

    PmuReadSynchronousFailed = (True, Severity.Error, Facility.DriverPmu, 5)

    PmuNotInitialized = (True, Severity.Error, Facility.DriverPmu, 6)

    PmuUnitialized = (True, Severity.Null, Facility.DriverPmu, 7)

    PmuSetGpioCompleted = (True, Severity.Null, Facility.DriverPmu, 8)

    PmuSetCpioFailed = (True, Severity.Error, Facility.DriverPmu, 9)

    PmuWriteAsynchronousCompleted = (True, Severity.Null, Facility.DriverPmu, 10)

    PmuWriteAsynchronousFailed = (True, Severity.Error, Facility.DriverPmu, 11)

    PmuReadAsynchronousCompleted = (True, Severity.Null, Facility.DriverPmu, 12)

    PmuReadAsynchronousFailed = (True, Severity.Error, Facility.DriverPmu, 13)

    PmuTransactionsLocked = (True, Severity.Error, Facility.DriverPmu, 14)

    PmuPowerLatchSucceeded = (True, Severity.Null, Facility.DriverPmu, 15)

    PmuPowerUnlatchSucceeded = (True, Severity.Null, Facility.DriverPmu, 16)

    PmuUnitTestPassed = (True, Severity.Null, Facility.DriverPmu, 17)

    PmuUnitTestFailed = (True, Severity.Error, Facility.DriverPmu, 18)

    PmuSetGpioStarted = (True, Severity.Null, Facility.DriverPmu, 19)

    PmuSetChargeStateFailed = (True, Severity.Error, Facility.DriverPmu, 20)

    AlsInitialized = (True, Severity.Null, Facility.DriverAls, 0)

    AlsInitializationFailed = (True, Severity.Error, Facility.DriverAls, 1)

    AlsWriteSynchronousCompleted = (True, Severity.Null, Facility.DriverAls, 2)

    AlsWriteSynchronousFailed = (True, Severity.Error, Facility.DriverAls, 3)

    AlsReadSynchrounousCompleted = (True, Severity.Null, Facility.DriverAls, 4)

    AlsReadSynchrounousFailed = (True, Severity.Error, Facility.DriverAls, 5)

    AlsAlreadyInitialized = (True, Severity.Error, Facility.DriverAls, 6)

    AlsUnitialized = (True, Severity.Null, Facility.DriverAls, 7)

    AlsWriteAsynchronousCompleted = (True, Severity.Null, Facility.DriverAls, 8)

    AlsWriteAsynchronousFailed = (True, Severity.Error, Facility.DriverAls, 9)

    AlsReadAsynchronousCompleted = (True, Severity.Null, Facility.DriverAls, 10)

    AlsReadAsynchronousFailed = (True, Severity.Error, Facility.DriverAls, 11)

    AlsTransactionsLocked = (True, Severity.Error, Facility.DriverAls, 12)

    AlsUnitTestPassed = (True, Severity.Null, Facility.DriverAls, 13)

    AlsUnitTestFailed = (True, Severity.Error, Facility.DriverAls, 14)

    AlsNotPresent = (True, Severity.Error, Facility.DriverAls, 15)

    AlsNotConfigured = (True, Severity.Error, Facility.DriverAls, 16)

    AlsQueueFull = (True, Severity.Error, Facility.DriverAls, 17)

    AlsWriteStarted = (True, Severity.Null, Facility.DriverAls, 18)

    AlsWriteEnqueued = (True, Severity.Null, Facility.DriverAls, 19)

    AlsReadBusy = (True, Severity.Error, Facility.DriverAls, 20)

    AlsReadEnqueued = (True, Severity.Null, Facility.DriverAls, 21)

    AlsDeprecatedRegister = (True, Severity.Error, Facility.DriverAls, 22)

    UartAsyncWritePending = (True, Severity.Null, Facility.DriverUartAsync, 0)

    UartAsyncWriteBusy = (True, Severity.Error, Facility.DriverUartAsync, 1)

    UartAsyncBadBaudRate = (True, Severity.Error, Facility.DriverUartAsync, 2)

    UartAsyncZeroLength = (True, Severity.Error, Facility.DriverUartAsync, 3)

    UartAsyncDmaUnavailable = (True, Severity.Error, Facility.DriverUartAsync, 4)

    UartAsyncDmaTxIsrMiscall = (True, Severity.Error, Facility.DriverUartAsync, 5)

    UartAsyncTxChannelNotInit = (True, Severity.Error, Facility.DriverUartAsync, 6)

    UartAsyncTxDmaError = (True, Severity.Error, Facility.DriverUartAsync, 7)

    ExternalRamFailedVerification = (True, Severity.Error, Facility.DriverExternalRam, 0)

    FlexBusNullArgument = (True, Severity.Error, Facility.DriverFlexBus, 0)

    FlexBusBadCsRequested = (True, Severity.Error, Facility.DriverFlexBus, 1)

    FlexBusBadAddressRangeForAddress = (True, Severity.Error, Facility.DriverFlexBus, 2)

    FlexBusNotFlexBusAddress = (True, Severity.Error, Facility.DriverFlexBus, 3)

    FlexBusBusWidthNotAvailable = (True, Severity.Error, Facility.DriverFlexBus, 4)

    FlexBusWaitStatesTooLarge = (True, Severity.Error, Facility.DriverFlexBus, 5)

    FlexBusAddressSetupTimeTooLarge = (True, Severity.Error, Facility.DriverFlexBus, 6)

    FlexBusHoldTimeTooLarge = (True, Severity.Error, Facility.DriverFlexBus, 7)

    SpiOperationPending = (True, Severity.Null, Facility.DriverSpi, 0)

    SpiStructOverwritten = (True, Severity.Error, Facility.DriverSpi, 1)

    SpiMicTransactionInProgress = (True, Severity.Error, Facility.DriverSpi, 2)

    SpiMicNoTransactionInProgress = (True, Severity.Error, Facility.DriverSpi, 3)

    SpiMicTimeoutStop = (True, Severity.Error, Facility.DriverSpi, 4)

    EFlashPending = (True, Severity.Null, Facility.DriverEFlash, 0)

    EFlashSpiError0 = (True, Severity.Error, Facility.DriverEFlash, 1)

    EFlashBadJedecId0 = (True, Severity.Error, Facility.DriverEFlash, 2)

    EFlashBadJedecId1 = (True, Severity.Error, Facility.DriverEFlash, 3)

    EFlashBadJedecId2 = (True, Severity.Error, Facility.DriverEFlash, 4)

    EFlashTimeout = (True, Severity.Error, Facility.DriverEFlash, 5)

    EFlashBusy = (True, Severity.Error, Facility.DriverEFlash, 6)

    EFlashUnableToWrite = (True, Severity.Error, Facility.DriverEFlash, 7)

    EFlashBadAddress = (True, Severity.Error, Facility.DriverEFlash, 8)

    EFlashBadSize = (True, Severity.Error, Facility.DriverEFlash, 9)

    EFlashWrError = (True, Severity.Error, Facility.DriverEFlash, 10)

    EFlashBadOperation = (True, Severity.Error, Facility.DriverEFlash, 11)

    EFlashSpiInitFail = (True, Severity.Error, Facility.DriverEFlash, 20)

    EFlashEraseCheckFail = (True, Severity.Error, Facility.DriverEFlash, 21)

    EFlashAddressConflict = (True, Severity.Error, Facility.DriverEFlash, 22)

    EFlashQueueEmpty = (True, Severity.Error, Facility.DriverEFlash, 23)

    EFlashStructAlreadyQueued = (True, Severity.Error, Facility.DriverEFlash, 24)

    EFlashNullStruct = (True, Severity.Error, Facility.DriverEFlash, 25)

    EFlashPageStraddled = (True, Severity.Error, Facility.DriverEFlash, 26)

    EFlashNullCallback = (True, Severity.Error, Facility.DriverEFlash, 27)

    EFlashNullBuffer = (True, Severity.Error, Facility.DriverEFlash, 28)

    EFlashPowerUpFail = (True, Severity.Error, Facility.DriverEFlash, 29)

    CrcPending = (True, Severity.Null, Facility.DriverCrc, 0)

    CrcNotReady = (True, Severity.Error, Facility.DriverCrc, 1)

    CrcNullPointer = (True, Severity.Error, Facility.DriverCrc, 2)

    CrcZeroSize = (True, Severity.Error, Facility.DriverCrc, 3)

    PFlashProgramFailed = (True, Severity.Error, Facility.DriverPFlash, 0)

    PFlashSectionProgramFailed = (True, Severity.Error, Facility.DriverPFlash, 1)

    PFlashSectionEraseFailed = (True, Severity.Error, Facility.DriverPFlash, 2)

    PFlashWriteFailed = (True, Severity.Error, Facility.DriverPFlash, 3)

    PFlashAddressInvalid = (True, Severity.Error, Facility.DriverPFlash, 4)

    PFlashInvalid2Up = (True, Severity.Error, Facility.DriverPFlash, 5)

    PFlashResetReasonWriteComplete = (True, Severity.Null, Facility.DriverPFlash, 6)

    FpuInvalid = (True, Severity.Null, Facility.DriverFpu, 0)

    FpuInitialized = (True, Severity.Null, Facility.DriverFpu, 1)

    FpuInitializedFailed = (True, Severity.Error, Facility.DriverFpu, 1)

    FpuUnitialized = (True, Severity.Null, Facility.DriverFpu, 2)

    FpuUnitializationFailed = (True, Severity.Error, Facility.DriverFpu, 2)

    FpuEnabled = (True, Severity.Null, Facility.DriverFpu, 3)

    FpuNotEnabled = (True, Severity.Error, Facility.DriverFpu, 3)

    FpuDisabled = (True, Severity.Null, Facility.DriverFpu, 4)

    FpuNotDisabled = (True, Severity.Error, Facility.DriverFpu, 4)

    FpuCommandHandlersRegistered = (True, Severity.Null, Facility.DriverFpu, 5)

    TimeTimerNotGreaterThan = (True, Severity.Null, Facility.DriverTimers, 0)

    WatchdogInvalidTimeout = (True, Severity.Error, Facility.DriverWatchDog, 0)

    WatchdogDisabled = (True, Severity.Error, Facility.DriverWatchDog, 1)

    CoreModuleResetReasonUsbCommand = (True, Severity.Null, Facility.DriverCoreModule, 0)

    CoreModuleResetReasonSystemCrash = (True, Severity.Error, Facility.DriverCrashDump, 0)

    MmcauInvalidBufferSize = (True, Severity.Null, Facility.DriverMmcau, 0)

    BacklightDisabled = (True, Severity.Null, Facility.LibraryBacklight, 0)

    BacklightPending = (True, Severity.Null, Facility.LibraryBacklight, 1)

    BacklightBusy = (True, Severity.Error, Facility.LibraryBacklight, 2)

    BatteryNotInitialized = (True, Severity.Error, Facility.LibraryBattery, 0)

    BatteryNotConfigured = (True, Severity.Error, Facility.LibraryBattery, 1)

    BatteryQueueFull = (True, Severity.Error, Facility.LibraryBattery, 2)

    BatteryWriteStarted = (True, Severity.Null, Facility.LibraryBattery, 3)

    BatteryWriteSuccessful = (True, Severity.Null, Facility.LibraryBattery, 4)

    BatterySubscriptionDataValid = (True, Severity.Null, Facility.LibraryBattery, 5)

    BatteryWriteEnqueued = (True, Severity.Null, Facility.LibraryBattery, 6)

    BatteryReadBusy = (True, Severity.Error, Facility.LibraryBattery, 7)

    BatteryReadEnqueued = (True, Severity.Null, Facility.LibraryBattery, 8)

    BatteryAlreadyInitialized = (True, Severity.Error, Facility.LibraryBattery, 9)

    #    private static ushort DebugBase = 0
    #
    # DebugInitializeSucceeded = (True, Severity.Null, Facility.LibrariesBase, DeviceStatusCodes.DebugBase)
    #
    # DebugInitializeFailed = (True, Severity.Error, Facility.LibrariesBase, DeviceStatusCodes.DebugBase)
    #
    # DebugInitializeNoPrintProviders = (True, Severity.Error, Facility.LibrariesBase, DeviceStatusCodes.DebugBase + 1)
    #
    # DebugInitialized = (True, Severity.Null, Facility.LibrariesBase, DeviceStatusCodes.DebugBase + 2)
    #
    # DebugNotInitialized = (True, Severity.Error, Facility.LibrariesBase, DeviceStatusCodes.DebugBase + 2)
    #
    #    private static ushort DebugOpBase = DeviceStatusCodes.DebugBase + 256
    #
    #    private static ushort DebugOpUartAsyncBase = DeviceStatusCodes.DebugOpBase + 16
    #
    #    private static ushort DebugOpItmBase = DeviceStatusCodes.DebugOpBase + 32
    #
    # DebugOpItmQueueApc = (True, Severity.Error, Facility.LibrariesBase, DeviceStatusCodes.DebugBase)
    #
    #    private static ushort DebugOpSubBase = DeviceStatusCodes.DebugOpBase + 48
    #
    # DebugOpSubQueueApc = (True, Severity.Error, Facility.LibrariesBase, DeviceStatusCodes.DebugBase)
    #
    #    private static ushort RuntimeBase = 0
    #
    # RuntimeInitializeSucceeded = (True, Severity.Null, Facility.LibraryRuntime, DeviceStatusCodes.RuntimeBase)
    #
    # RuntimeInitializeFailed = (True, Severity.Error, Facility.LibraryRuntime, DeviceStatusCodes.RuntimeBase + 1)
    #
    #    private static ushort RuntimeKapcBase = 256
    #
    # RuntimeKapcNoNodes = (True, Severity.Error, Facility.LibraryRuntime, DeviceStatusCodes.RuntimeKapcBase)
    #
    #    private static ushort RuntimeRingbufferBase = 512
    #
    # RuntimeRingbufferBytesNotPowerOfTwo = (True, Severity.Error, Facility.LibraryRuntime, DeviceStatusCodes.RuntimeRingbufferBase)
    #
    # RuntimeRingbufferWriteOverflow = (True, Severity.Error, Facility.LibraryRuntime, DeviceStatusCodes.RuntimeRingbufferBase + 1)
    #
    # RuntimeRingbufferReadOverflow = (True, Severity.Error, Facility.LibraryRuntime, DeviceStatusCodes.RuntimeRingbufferBase + 2)

    UsbCmdProtocolSuccess = (True, Severity.Null, Facility.LibraryUsbCmdProtocol, 0)

    UsbCmdProtocolBadCommand = (True, Severity.Error, Facility.LibraryUsbCmdProtocol, 1)

    UsbCmdProtocolUnknownCommand = (True, Severity.Error, Facility.LibraryUsbCmdProtocol, 2)

    UsbCmdProtocolFailed = (True, Severity.Error, Facility.LibraryUsbCmdProtocol, 3)

    UsbCmdProtocolBusy = (True, Severity.Error, Facility.LibraryUsbCmdProtocol, 4)

    UsbCmdProtocolOpenPipeInFailed = (True, Severity.Error, Facility.LibraryUsbCmdProtocol, 5)

    UsbCmdProtocolOpenPipeOutFailed = (True, Severity.Error, Facility.LibraryUsbCmdProtocol, 6)

    UsbCmdProtocolSendFailed = (True, Severity.Error, Facility.LibraryUsbCmdProtocol, 7)

    UsbCmdProtocolReceiveFailed = (True, Severity.Error, Facility.LibraryUsbCmdProtocol, 8)

    UsbCmdProtocolInvalidDevice = (True, Severity.Error, Facility.LibraryUsbCmdProtocol, 9)

    UsbCmdProtocolExceededListSize = (True, Severity.Error, Facility.LibraryUsbCmdProtocol, 10)

    UsbCmdProtocolInvalidBuffer = (True, Severity.Error, Facility.LibraryUsbCmdProtocol, 11)

    UsbCmdProtocolNoData = (True, Severity.Error, Facility.LibraryUsbCmdProtocol, 12)

    UsbCmdProtocolPendingWait = (True, Severity.Error, Facility.LibraryUsbCmdProtocol, 13)

    UsbCmdProtocolSendIncomplete = (True, Severity.Error, Facility.LibraryUsbCmdProtocol, 14)

    UsbCmdProtocolHandlerInProgress = (True, Severity.Error, Facility.LibraryUsbCmdProtocol, 15)

    UsbCmdProtocolTimeout = (True, Severity.Error, Facility.LibraryUsbCmdProtocol, 16)

    UsbCmdProtocolCmdDoesNotExist = (True, Severity.Error, Facility.LibraryUsbCmdProtocol, 17)

    UsbCmdProtocolCmdIsTimedOut = (True, Severity.Error, Facility.LibraryUsbCmdProtocol, 18)

    UsbCmdProtocolIsNotAValidCmdPacket = (True, Severity.Error, Facility.LibraryUsbCmdProtocol, 19)

    JutilSuccess = (True, Severity.Null, Facility.LibraryJutil, 0)

    JutilFailedInternalMemoryAllocation = (True, Severity.Error, Facility.LibraryJutil, 1)

    JutilNoConnectedDevices = (True, Severity.Null, Facility.LibraryJutil, 2)

    JutilFailedToGetDevicePath = (True, Severity.Error, Facility.LibraryJutil, 3)

    JutilNoMoreDevicesDetected = (True, Severity.Error, Facility.LibraryJutil, 4)

    JutilInvalidDevicePathFromInternalBuffer = (True, Severity.Error, Facility.LibraryJutil, 5)

    JutilCorruptedInternalList = (True, Severity.Error, Facility.LibraryJutil, 6)

    JutilFailedCallbackInvocation = (True, Severity.Error, Facility.LibraryJutil, 7)

    JutilCommunicationFailure = (True, Severity.Error, Facility.LibraryJutil, 8)

    JutilInvalidHandle = (True, Severity.Error, Facility.LibraryJutil, 9)

    JutilNullHandle = (True, Severity.Error, Facility.LibraryJutil, 10)

    JutilInsufficientBufferAlloc = (True, Severity.Error, Facility.LibraryJutil, 11)

    JutilNoDeviceSelected = (True, Severity.Error, Facility.LibraryJutil, 12)

    JutilDeprecatedCommand = (True, Severity.Error, Facility.LibraryJutil, 13)

    JutilMultipleInstances = (True, Severity.Error, Facility.LibraryJutil, 14)

    JutilBtedrTransportNotInitialized = (True, Severity.Error, Facility.LibraryJutil, 15)

    JutilBtedrDiscoveryTimerNotInitialized = (True, Severity.Error, Facility.LibraryJutil, 16)

    TimeNullArgument = (True, Severity.Error, Facility.LibraryTime, 0)

    TimeInvalidArgument = (True, Severity.Error, Facility.LibraryTime, 1)

    TimeTzInvalidBias = (True, Severity.Error, Facility.LibraryTime, 2)

    TimeTzInvalidStandardDate = (True, Severity.Error, Facility.LibraryTime, 3)

    TimeTzInvalidDaylightDate = (True, Severity.Error, Facility.LibraryTime, 4)

    TimeSetDaylightAmbiguity = (True, Severity.Error, Facility.LibraryTime, 5)

    TimeBadCategoryIndex = (True, Severity.Error, Facility.LibraryTime, 6)

    TimeBadTimeZoneIndex = (True, Severity.Error, Facility.LibraryTime, 7)

    TimeTzFileOperationInProgress = (True, Severity.Error, Facility.LibraryTime, 8)

    TimeTzFileNameNotFound = (True, Severity.Error, Facility.LibraryTime, 9)

    HRManagerSucceeded = (True, Severity.Null, Facility.LibraryHRManager, 0)

    HRManagerNotInitialized = (True, Severity.Error, Facility.LibraryHRManager, 1)

    HRManagerAlreadyInitialized = (True, Severity.Error, Facility.LibraryHRManager, 2)

    HRManagerUnsupportedConfig = (True, Severity.Error, Facility.LibraryHRManager, 3)

    HRManagerFifoOverflow = (True, Severity.Error, Facility.LibraryHRManager, 4)

    ConfigurationSucceeded = (True, Severity.Null, Facility.LibraryConfiguration, 0)

    ConfigurationFailed = (True, Severity.Error, Facility.LibraryConfiguration, 1)

    ConfigurationPflashReadOtpFailed = (True, Severity.Error, Facility.LibraryConfiguration, 2)

    ConfigurationPflashWriteOtpfailed = (True, Severity.Error, Facility.LibraryConfiguration, 3)

    ConfigurationEflashInvalidHeader = (True, Severity.Error, Facility.LibraryConfiguration, 4)

    ConfigurationEflashReadFailed = (True, Severity.Error, Facility.LibraryConfiguration, 5)

    ConfigurationEflashWriteFailed = (True, Severity.Error, Facility.LibraryConfiguration, 6)

    ConfigurationEraseFailed = (True, Severity.Error, Facility.LibraryConfiguration, 7)

    ConfigurationVerifyFailed = (True, Severity.Error, Facility.LibraryConfiguration, 8)

    ConfigurationModuleBusy = (True, Severity.Error, Facility.LibraryConfiguration, 9)

    ConfigurationInvalidKey = (True, Severity.Error, Facility.LibraryConfiguration, 10)

    ConfigurationInvalidVersion = (True, Severity.Error, Facility.LibraryConfiguration, 11)

    ConfigurationInvalidModule = (True, Severity.Error, Facility.LibraryConfiguration, 12)

    ConfigurationInvalidRegister = (True, Severity.Error, Facility.LibraryConfiguration, 13)

    ConfigurationInvalidRegisterSize = (True, Severity.Error, Facility.LibraryConfiguration, 14)

    MotionTooFewSamplesAvailable = (True, Severity.Error, Facility.LibraryMotion, 0)

    MotionNullSubscription = (True, Severity.Error, Facility.LibraryMotion, 1)

    MotionBadSampleRate = (True, Severity.Error, Facility.LibraryMotion, 2)

    MotionNullFifoStorage = (True, Severity.Error, Facility.LibraryMotion, 3)

    MotionNullCallback = (True, Severity.Error, Facility.LibraryMotion, 4)

    MotionInsufficientFifoStorage = (True, Severity.Error, Facility.LibraryMotion, 5)

    MotionAlreadySubscribed = (True, Severity.Error, Facility.LibraryMotion, 6)

    MotionSubscriptionNotFound = (True, Severity.Error, Facility.LibraryMotion, 7)

    MotionReusingFifoStorage = (True, Severity.Error, Facility.LibraryMotion, 8)

    MotionDeviceUnavailable = (True, Severity.Error, Facility.LibraryMotion, 9)

    MotionBadFifoElementSize = (True, Severity.Error, Facility.LibraryMotion, 10)

    MotionDeviceNotReady = (True, Severity.Error, Facility.LibraryMotion, 11)

    MotionPending = (True, Severity.Null, Facility.LibraryMotion, 12)

    MotionDisabled = (True, Severity.Error, Facility.LibraryMotion, 13)

    MotionBadSampleType = (True, Severity.Error, Facility.LibraryMotion, 14)

    PegAlreadyEnabled = (True, Severity.Null, Facility.LibraryPeg, 0)

    PegNotInitialized = (True, Severity.Error, Facility.LibraryPeg, 1)

    PegCurrentlyEnabled = (True, Severity.Error, Facility.LibraryPeg, 2)

    TouchNotInitialized = (True, Severity.Error, Facility.LibraryTouch, 0)

    TouchNotConfigured = (True, Severity.Error, Facility.LibraryTouch, 1)

    TouchBusy = (True, Severity.Error, Facility.LibraryTouch, 2)

    TouchWriteStarted = (True, Severity.Null, Facility.LibraryTouch, 3)

    TouchWriteSuccessful = (True, Severity.Null, Facility.LibraryTouch, 4)

    TouchSubscriptionDataValid = (True, Severity.Null, Facility.LibraryTouch, 5)

    TouchQueueFull = (True, Severity.Error, Facility.LibraryTouch, 6)

    TouchWriteEnqueued = (True, Severity.Null, Facility.LibraryTouch, 7)

    TouchReadBusy = (True, Severity.Error, Facility.LibraryTouch, 8)

    TouchReadEnqueued = (True, Severity.Null, Facility.LibraryTouch, 9)

    TouchAlreadyInitialized = (True, Severity.Error, Facility.LibraryTouch, 10)

    MicrophonePending = (True, Severity.Null, Facility.LibraryMicrophone, 0)

    MicrophoneEnabled = (True, Severity.Null, Facility.LibraryMicrophone, 1)

    MicrophoneDisabled = (True, Severity.Null, Facility.LibraryMicrophone, 2)

    MicrophoneNotInitialized = (True, Severity.Error, Facility.LibraryMicrophone, 3)

    MicrophoneBusy = (True, Severity.Error, Facility.LibraryMicrophone, 4)

    MicrophoneAlreadyEnabled = (True, Severity.Error, Facility.LibraryMicrophone, 5)

    MicrophoneIllegalBuffer = (True, Severity.Error, Facility.LibraryMicrophone, 6)

    MicrophoneInsufficientSamples = (True, Severity.Error, Facility.LibraryMicrophone, 7)

    MicrophoneNotStopping = (True, Severity.Error, Facility.LibraryMicrophone, 8)

    MicrophoneBadBufferSize = (True, Severity.Error, Facility.LibraryMicrophone, 9)

    MicrophoneBadGainValue = (True, Severity.Error, Facility.LibraryMicrophone, 10)

    HrLedNotInitialized = (True, Severity.Error, Facility.LibraryHRLed, 0)

    HrLedNotConfigured = (True, Severity.Error, Facility.LibraryHRLed, 1)

    HrLedQueueFull = (True, Severity.Error, Facility.LibraryHRLed, 2)

    HrLedWriteStarted = (True, Severity.Null, Facility.LibraryHRLed, 3)

    HrLedSuccessful = (True, Severity.Null, Facility.LibraryHRLed, 4)

    HrLedSubscriptionDataValid = (True, Severity.Null, Facility.LibraryHRLed, 5)

    HrLedWriteEnqueued = (True, Severity.Null, Facility.LibraryHRLed, 6)

    HrLedReadBusy = (True, Severity.Error, Facility.LibraryHRLed, 7)

    HrLedReadEnqueued = (True, Severity.Null, Facility.LibraryHRLed, 8)

    HrLedWriteBusy = (True, Severity.Error, Facility.LibraryHRLed, 9)

    HrLedAlreadyInitialized = (True, Severity.Error, Facility.LibraryHRLed, 10)

    GsrNotInitialized = (True, Severity.Error, Facility.LibraryGsr, 0)

    GsrNotConfigured = (True, Severity.Error, Facility.LibraryGsr, 1)

    GsrQueueFull = (True, Severity.Error, Facility.LibraryGsr, 2)

    GsrWriteStarted = (True, Severity.Null, Facility.LibraryGsr, 3)

    GsrSuccessful = (True, Severity.Null, Facility.LibraryGsr, 4)

    GsrSubscriptionDataValid = (True, Severity.Null, Facility.LibraryGsr, 5)

    GsrWriteEnqueued = (True, Severity.Null, Facility.LibraryGsr, 6)

    GsrReadBusy = (True, Severity.Error, Facility.LibraryGsr, 7)

    GsrReadEnqueued = (True, Severity.Null, Facility.LibraryGsr, 8)

    GsrAlreadyInitialized = (True, Severity.Error, Facility.LibraryGsr, 9)

    UvNotInitialized = (True, Severity.Error, Facility.LibraryUV, 0)

    UvNotConfigured = (True, Severity.Error, Facility.LibraryUV, 1)

    UvQueueFull = (True, Severity.Error, Facility.LibraryUV, 2)

    UvWriteStarted = (True, Severity.Null, Facility.LibraryUV, 3)

    UvSuccessful = (True, Severity.Null, Facility.LibraryUV, 4)

    UvSubscriptionDataValid = (True, Severity.Null, Facility.LibraryUV, 5)

    UvWriteEnqueued = (True, Severity.Null, Facility.LibraryUV, 6)

    UvReadBusy = (True, Severity.Error, Facility.LibraryUV, 7)

    UvReadEnqueued = (True, Severity.Null, Facility.LibraryUV, 8)

    UvAlreadyInitialized = (True, Severity.Error, Facility.LibraryUV, 9)

    SkinTempNotInitialized = (True, Severity.Error, Facility.LibrarySkinTemp, 0)

    SkinTempNotConfigured = (True, Severity.Error, Facility.LibrarySkinTemp, 1)

    SkinTempQueueFull = (True, Severity.Error, Facility.LibrarySkinTemp, 2)

    SkinTempWriteStarted = (True, Severity.Null, Facility.LibrarySkinTemp, 3)

    SkinTempSuccessful = (True, Severity.Null, Facility.LibrarySkinTemp, 4)

    SkinTempSubscriptionDataValid = (True, Severity.Null, Facility.LibrarySkinTemp, 5)

    SkinTempWriteEnqueued = (True, Severity.Null, Facility.LibrarySkinTemp, 6)

    SkinTempReadBusy = (True, Severity.Error, Facility.LibrarySkinTemp, 7)

    SkinTempReadEnqueued = (True, Severity.Null, Facility.LibrarySkinTemp, 8)

    SkinTempAlreadyInitialized = (True, Severity.Error, Facility.LibrarySkinTemp, 9)

    AmbTempNotInitialized = (True, Severity.Error, Facility.LibraryAmbTemp, 0)

    AmbTempNotConfigured = (True, Severity.Error, Facility.LibraryAmbTemp, 1)

    AmbTempQueueFull = (True, Severity.Error, Facility.LibraryAmbTemp, 2)

    AmbTempWriteStarted = (True, Severity.Null, Facility.LibraryAmbTemp, 3)

    AmbTempSuccessful = (True, Severity.Null, Facility.LibraryAmbTemp, 4)

    AmbTempSubscriptionDataValid = (True, Severity.Null, Facility.LibraryAmbTemp, 5)

    AmbTempWriteEnqueued = (True, Severity.Null, Facility.LibraryAmbTemp, 6)

    AmbTempReadBusy = (True, Severity.Error, Facility.LibraryAmbTemp, 7)

    AmbTempReadEnqueued = (True, Severity.Null, Facility.LibraryAmbTemp, 8)

    AmbTempAlreadyInitialized = (True, Severity.Error, Facility.LibraryAmbTemp, 9)

    PedometerFifoOverflow = (True, Severity.Error, Facility.LibraryPedometer, 0)

    AlgoMathInitializeSucceeded = (True, Severity.Null, Facility.LibraryAlgoMath, 0)

    AlgoMathInitializeFailed = (True, Severity.Error, Facility.LibraryAlgoMath, 1)

    AlgoMathBadMatrix = (True, Severity.Error, Facility.LibraryAlgoMath, 2)

    AlgoMathMathError = (True, Severity.Error, Facility.LibraryAlgoMath, 3)

    DataLoggerPending = (True, Severity.Null, Facility.LibraryLogger, 0)

    DataLoggerEndOfLog = (True, Severity.Null, Facility.LibraryLogger, 1)

    DataLoggerBusy = (True, Severity.Error, Facility.LibraryLogger, 2)

    DataLoggerRecordTooLarge = (True, Severity.Error, Facility.LibraryLogger, 3)

    DataLoggerIsDisabled = (True, Severity.Error, Facility.LibraryLogger, 4)

    DataLoggerIsActive = (True, Severity.Error, Facility.LibraryLogger, 5)

    DataLoggerIsCorrupt = (True, Severity.Error, Facility.LibraryLogger, 6)

    DataLoggerPastLogEnd = (True, Severity.Error, Facility.LibraryLogger, 7)

    DataLoggerReadPastChunkEnd = (True, Severity.Error, Facility.LibraryLogger, 8)

    DataLoggerChunkNotRead = (True, Severity.Error, Facility.LibraryLogger, 9)

    DataLoggerFlashOpInProgress = (True, Severity.Error, Facility.LibraryLogger, 10)

    DataLoggerBadChunkCount = (True, Severity.Error, Facility.LibraryLogger, 11)

    DataLoggerBadGetMetadataState = (True, Severity.Error, Facility.LibraryLogger, 12)

    DataLoggerBadChunkDeleteState = (True, Severity.Error, Facility.LibraryLogger, 13)

    DataLoggerBadBufferWriteCount = (True, Severity.Error, Facility.LibraryLogger, 14)

    DataLoggerBadWriteBufferAvailable = (True, Severity.Error, Facility.LibraryLogger, 15)

    DataLoggerBadBufferBusyState = (True, Severity.Error, Facility.LibraryLogger, 16)

    DataLoggerBadWriteBufferState = (True, Severity.Error, Facility.LibraryLogger, 17)

    DataLoggerTooManyCallbacks = (True, Severity.Error, Facility.LibraryLogger, 18)

    DataLoggerCrcFail = (True, Severity.Error, Facility.LibraryLogger, 19)

    DataLoggerDupFlashOpStruct = (True, Severity.Error, Facility.LibraryLogger, 20)

    DataLoggerBadFlashOp = (True, Severity.Error, Facility.LibraryLogger, 21)

    DataLoggerFlashGeometryBad = (True, Severity.Error, Facility.LibraryLogger, 22)

    DataLoggerBadChunkAddress = (True, Severity.Error, Facility.LibraryLogger, 23)

    GpsHibernating = (True, Severity.Error, Facility.LibraryGps, 0)

    GpsNotPatched = (True, Severity.Error, Facility.LibraryGps, 1)

    GpsCommandArgumentLengthError = (True, Severity.Error, Facility.LibraryGps, 2)

    GpsInvalidSatelliteId = (True, Severity.Error, Facility.LibraryGps, 3)

    GpsInvalidTestMode = (True, Severity.Error, Facility.LibraryGps, 4)

    GpsBusy = (True, Severity.Error, Facility.LibraryGps, 5)

    GpsUnableToEnableOrDisable = (True, Severity.Error, Facility.LibraryGps, 6)

    GpsIsEnabled = (True, Severity.Null, Facility.LibraryGps, 7)

    GpsIsDisabled = (True, Severity.Null, Facility.LibraryGps, 8)

    FilePending = (True, Severity.Null, Facility.LibraryFile, 0)

    FileFileStructInUse = (True, Severity.Error, Facility.LibraryFile, 1)

    FileFileAlreadyOpen = (True, Severity.Error, Facility.LibraryFile, 2)

    FileFileNotOpen = (True, Severity.Error, Facility.LibraryFile, 3)

    FileOperationPending = (True, Severity.Error, Facility.LibraryFile, 4)

    FileSizeBeyondMaxForFile = (True, Severity.Error, Facility.LibraryFile, 5)

    FileSeekError = (True, Severity.Error, Facility.LibraryFile, 6)

    FileNotOpenForWrite = (True, Severity.Error, Facility.LibraryFile, 7)

    FileInvalidFile = (True, Severity.Error, Facility.LibraryFile, 8)

    FileSizeMismatch = (True, Severity.Error, Facility.LibraryFile, 9)

    FileBacklogOverflow = (True, Severity.Error, Facility.LibraryFile, 10)

    FileBadFileAdress = (True, Severity.Error, Facility.LibraryFile, 11)

    FileFatTableMismatch = (True, Severity.Error, Facility.LibraryFile, 12)

    FileBadFileSizeSpecified = (True, Severity.Error, Facility.LibraryFile, 13)

    FileTooLittleFlashLeft = (True, Severity.Error, Facility.LibraryFile, 14)

    FileTooManyFilesDefined = (True, Severity.Error, Facility.LibraryFile, 15)

    FileNumberOfFilesDecreased = (True, Severity.Error, Facility.LibraryFile, 16)

    FileNullStructurePointer = (True, Severity.Error, Facility.LibraryFile, 17)

    FileBadFileIndex = (True, Severity.Error, Facility.LibraryFile, 18)

    FileStructOnStack = (True, Severity.Error, Facility.LibraryFile, 19)

    FileBadFileType = (True, Severity.Error, Facility.LibraryFile, 20)

    FileNullBufferPointer = (True, Severity.Error, Facility.LibraryFile, 21)

    FileBadSeekOrigin = (True, Severity.Error, Facility.LibraryFile, 22)

    RemoteSubscriptionInvalidArg = (True, Severity.Error, Facility.LibraryRemoteSubscription, 0)

    RemoteSubscriptionPushServiceInUse = (
        True,
        Severity.Error,
        Facility.LibraryRemoteSubscription,
        1,
    )

    BluetoothInvalidArg = (True, Severity.Error, Facility.LibraryBTPS, 756)

    BluetoothSendFailed = (True, Severity.Error, Facility.LibraryBTPS, 757)

    BluetoothSendPending = (True, Severity.Null, Facility.LibraryBTPS, 758)

    BluetoothHciRawCommandFailed = (True, Severity.Error, Facility.LibraryBTPS, 759)

    BluetoothBusy = (True, Severity.Error, Facility.LibraryBTPS, 760)

    BluetoothExitSleepPending = (True, Severity.Null, Facility.LibraryBTPS, 761)

    BluetoothChipAsleep = (True, Severity.Error, Facility.LibraryBTPS, 762)

    BluetoothDisabled = (True, Severity.Error, Facility.LibraryBTPS, 763)

    BluetoothHwIncompatible = (True, Severity.Error, Facility.LibraryBTPS, 764)

    BluetoothAlreadyInState = (True, Severity.Null, Facility.LibraryBTPS, 765)

    BluetoothLinkKeyNotFound = (True, Severity.Error, Facility.LibraryBTPS, 766)

    BluetoothDisconnectPending = (True, Severity.Null, Facility.LibraryBTPS, 767)

    BluetoothDisconnetAlreadyInProgress = (True, Severity.Error, Facility.LibraryBTPS, 768)

    BluetoothNotConnected = (True, Severity.Error, Facility.LibraryBTPS, 769)

    BluetoothDisconnectTimedOut = (True, Severity.Error, Facility.LibraryBTPS, 770)

    BluetoothBandwidthExceeded = (True, Severity.Error, Facility.LibraryBTPS, 771)

    BluetoothRetryPending = (True, Severity.Null, Facility.LibraryBTPS, 772)

    BluetoothWpnsPerformingOverflow = (True, Severity.Error, Facility.LibraryBTPS, 1024)

    BluetoothWpnsInvalidPacket = (True, Severity.Error, Facility.LibraryBTPS, 1025)

    BluetoothSdpuInvalidSize = (True, Severity.Error, Facility.LibraryBTPS, 1792)

    BluetoothSdpuInvalidSequHeader = (True, Severity.Error, Facility.LibraryBTPS, 1793)

    BluetoothSdpuInvalidElinoNotFound = (True, Severity.Error, Facility.LibraryBTPS, 1794)

    BluetoothSdpuInvalidPidNotFound = (True, Severity.Error, Facility.LibraryBTPS, 1795)

    BluetoothSdpuPidTooLong = (True, Severity.Error, Facility.LibraryBTPS, 1796)

    BluetoothUnitTestFailed = (True, Severity.Error, Facility.LibraryBTPS, 2048)

    BluetoothEnableNotAllowed = (True, Severity.Error, Facility.LibraryBTPS, 2304)

    MinuteTimerAlreadySubscribed = (True, Severity.Error, Facility.LibraryMinuteTimer, 0)

    MinuteTimerSubscriptionNotFound = (True, Severity.Error, Facility.LibraryMinuteTimer, 1)

    MinuteTimerSubscriptionRemoveFail = (True, Severity.Error, Facility.LibraryMinuteTimer, 2)

    SubscriptionBaseListRemovalError = (True, Severity.Error, Facility.LibrarySubscriptionBase, 0)

    SubscriptionBaseRecursiveNotification = (
        True,
        Severity.Error,
        Facility.LibrarySubscriptionBase,
        1,
    )

    SubscriptionBaseInvalidRemovedNotification = (
        True,
        Severity.Error,
        Facility.LibrarySubscriptionBase,
        2,
    )

    SubscriptionBaseBadPointer = (True, Severity.Error, Facility.LibrarySubscriptionBase, 3)

    SubscriptionBaseNullPointer = (True, Severity.Error, Facility.LibrarySubscriptionBase, 4)

    SubscriptionBaseSubscriptionNotInitialized = (
        True,
        Severity.Error,
        Facility.LibrarySubscriptionBase,
        5,
    )

    AlgorithmsRecoveryProfileInvalidInput = (True, Severity.Error, Facility.LibraryRecovery, 0)

    AlgorithmsRecoveryProfileInvalidMaxHrOrMaxMet = (
        True,
        Severity.Error,
        Facility.LibraryRecovery,
        1,
    )

    USBConnectionReinitialization = (True, Severity.Error, Facility.LibraryUSBConnection, 0)

    USBConnectionAlreadyStarted = (True, Severity.Error, Facility.LibraryUSBConnection, 1)

    SramFwUpdateBootIntoUpdateMode = (True, Severity.Null, Facility.LibrarySRAMFWUpdate, 0)

    SramFwUpdateResetReasonSRAMUpdateSuccess = (
        True,
        Severity.Null,
        Facility.LibrarySRAMFWUpdate,
        1,
    )

    SramFwUpdateResetReasonSRAMTimeout = (True, Severity.Error, Facility.LibrarySRAMFWUpdate, 2)

    SramFwUpdateBatteryTooLow = (True, Severity.Error, Facility.LibrarySRAMFWUpdate, 3)

    SramFwUpdateFileWriteFailure = (True, Severity.Error, Facility.LibrarySRAMFWUpdate, 4)

    SramFwUpdateFileWriteRequestFailure = (True, Severity.Error, Facility.LibrarySRAMFWUpdate, 5)

    SramFwUpdateFileCrcMismatch = (True, Severity.Error, Facility.LibrarySRAMFWUpdate, 6)

    SramFwUpdateFileVersionReadFailure = (True, Severity.Error, Facility.LibrarySRAMFWUpdate, 7)

    SramFwUpdateFileVersionRequestFailure = (True, Severity.Error, Facility.LibrarySRAMFWUpdate, 8)

    SramFwUpdate2upCrcMismatch = (True, Severity.Error, Facility.LibrarySRAMFWUpdate, 9)

    SramFwUpdateAppCrcMismatch = (True, Severity.Error, Facility.LibrarySRAMFWUpdate, 10)

    SramFwUpdateBlobCrcMismatch = (True, Severity.Error, Facility.LibrarySRAMFWUpdate, 11)

    SramFwUpdateAppNotFound = (True, Severity.Error, Facility.LibrarySRAMFWUpdate, 12)

    SramFwUpdateFileOpenRequestFailure = (True, Severity.Error, Facility.LibrarySRAMFWUpdate, 13)

    SramFwUpdateFileOpenFailure = (True, Severity.Error, Facility.LibrarySRAMFWUpdate, 14)

    SramFwUpdateFileCloseRequestFailed = (True, Severity.Error, Facility.LibrarySRAMFWUpdate, 15)

    SramFwUpdateFileCloseFailure = (True, Severity.Error, Facility.LibrarySRAMFWUpdate, 16)

    SramFwUpdateBlobPcbIdMismatch = (True, Severity.Error, Facility.LibrarySRAMFWUpdate, 17)

    DateChangeSubscriptionAlreadyInitialized = (
        True,
        Severity.Error,
        Facility.LibraryDateChangeSubscription,
        0,
    )

    DateChangeSubscriptionNotInitialized = (
        True,
        Severity.Error,
        Facility.LibraryDateChangeSubscription,
        1,
    )

    HapticInvalidStreamId = (True, Severity.Error, Facility.LibraryHaptic, 0)

    FitnessPlansUnableToOpenFile = (True, Severity.Error, Facility.LibraryFitnessPlans, 0)

    FitnessPlansFileReadError = (True, Severity.Error, Facility.LibraryFitnessPlans, 1)

    FitnessPlansCorruptFile = (True, Severity.Error, Facility.LibraryFitnessPlans, 2)

    FitnessPlansVersionMismatch = (True, Severity.Error, Facility.LibraryFitnessPlans, 3)

    FitnessPlansCrcAssumptionBroken = (True, Severity.Error, Facility.LibraryFitnessPlans, 4)

    FitnessPlansOutOfMemory = (True, Severity.Error, Facility.LibraryFitnessPlans, 5)

    FitnessPlansInvalidFileFormat = (True, Severity.Error, Facility.LibraryFitnessPlans, 6)

    FitnessPlansBadArgument = (True, Severity.Error, Facility.LibraryFitnessPlans, 7)

    FitnessPlansNoElementsAvailable = (True, Severity.Error, Facility.LibraryFitnessPlans, 8)

    FitnessPlansEndOfData = (True, Severity.Error, Facility.LibraryFitnessPlans, 9)

    FitnessPlansWorkoutAlreadyStored = (True, Severity.Error, Facility.LibraryFitnessPlans, 10)

    FitnessPlansWorkoutNotStarted = (True, Severity.Error, Facility.LibraryFitnessPlans, 11)

    FitnessPlansPreviousRequestStillActive = (
        True,
        Severity.Error,
        Facility.LibraryFitnessPlans,
        12,
    )

    FitnessPlansWorkoutAlreadyLoaded = (True, Severity.Error, Facility.LibraryFitnessPlans, 13)

    FitnessPlansWorkoutNotLoaded = (True, Severity.Error, Facility.LibraryFitnessPlans, 14)

    FitnessPlanInvalidCompletionType = (True, Severity.Error, Facility.LibraryFitnessPlans, 15)

    FitnessPlanExerciseTimeTooShort = (True, Severity.Error, Facility.LibraryFitnessPlans, 16)

    AncsNotificationCacheUnitTestFailed = (
        True,
        Severity.Error,
        Facility.LibraryAncsNotificationCache,
        0,
    )

    AncsNotificationCacheAlreadyInCache = (
        True,
        Severity.Error,
        Facility.LibraryAncsNotificationCache,
        1,
    )

    FireballUiInvalidParameterSize = (True, Severity.Error, Facility.ModuleFireballUI, 0)

    FireballUiInvalidScreenId = (True, Severity.Error, Facility.ModuleFireballUI, 1)

    FireballUiNavigationDisabled = (True, Severity.Error, Facility.ModuleFireballUI, 2)

    FireballUiInvalidBufferSize = (True, Severity.Error, Facility.ModuleFireballUI, 3)

    FireballUiNoMeTileImage = (True, Severity.Error, Facility.ModuleFireballUI, 4)

    FireballUiMeTileImageNotAvailable = (True, Severity.Error, Facility.ModuleFireballUI, 5)

    FireballUiMeTileWriteInProgress = (True, Severity.Error, Facility.ModuleFireballUI, 6)

    FireballUiSyncInProgress = (True, Severity.Error, Facility.ModuleFireballUI, 7)

    FireballListTailNoHead = (True, Severity.Error, Facility.ModuleFireballUtilities, 0)

    FireballListHeadNoTail = (True, Severity.Error, Facility.ModuleFireballUtilities, 1)

    FireballListTailHasNext = (True, Severity.Error, Facility.ModuleFireballUtilities, 2)

    FireballListParamNull = (True, Severity.Error, Facility.ModuleFireballUtilities, 3)

    FireballListListEmpty = (True, Severity.Null, Facility.ModuleFireballUtilities, 4)

    FireballListElementNotPresent = (True, Severity.Error, Facility.ModuleFireballUtilities, 5)

    ProfileNotInitialized = (True, Severity.Error, Facility.ModuleProfile, 0)

    ProfileReinitialization = (True, Severity.Error, Facility.ModuleProfile, 1)

    ProfileFileSizeMismatch = (True, Severity.Error, Facility.ModuleProfile, 2)

    ProfileFileBusy = (True, Severity.Error, Facility.ModuleProfile, 3)

    ProfileUnsupportedVersion = (True, Severity.Error, Facility.ModuleProfile, 4)

    ProfileInvalidValue = (True, Severity.Error, Facility.ModuleProfile, 5)

    ProfileTelemetryDisallowed = (True, Severity.Error, Facility.ModuleProfile, 6)

    LoggerSubscriptionsInvalidArg = (True, Severity.Error, Facility.ModuleLoggerSubscriptions, 0)

    PowerManagerReinitialization = (True, Severity.Error, Facility.ModulePowerManager, 0)

    PowerManagerPowerOffDisallowed = (True, Severity.Error, Facility.ModulePowerManager, 1)

    PowerManagerAlreadyEnteredRunMode = (True, Severity.Error, Facility.ModulePowerManager, 2)

    PowerManagerAlreadyExitedRunMode = (True, Severity.Error, Facility.ModulePowerManager, 3)

    PowerManagerAlreadyEnabled = (True, Severity.Error, Facility.ModulePowerManager, 4)

    PowerManagerAlreadyDisabled = (True, Severity.Error, Facility.ModulePowerManager, 5)

    PowerManagerDisabled = (True, Severity.Error, Facility.ModulePowerManager, 6)

    PowerManagerEnabled = (True, Severity.Error, Facility.ModulePowerManager, 7)

    PowerManagerDisplayMgmtDisabled = (True, Severity.Error, Facility.ModulePowerManager, 8)

    PowerManagerDisplayMgmtEnabled = (True, Severity.Error, Facility.ModulePowerManager, 9)

    PowerManagerBacklightMgmtDisabled = (True, Severity.Error, Facility.ModulePowerManager, 10)

    PowerManagerBacklightMgmtEnabled = (True, Severity.Error, Facility.ModulePowerManager, 11)

    PowerManagerTouchMgmtDisabled = (True, Severity.Error, Facility.ModulePowerManager, 12)

    PowerManagerTouchMgmtEnabled = (True, Severity.Error, Facility.ModulePowerManager, 13)

    PowerManagerHrMgmtDisabled = (True, Severity.Error, Facility.ModulePowerManager, 14)

    PowerManagerHrMgmtEnabled = (True, Severity.Error, Facility.ModulePowerManager, 15)

    PowerManagerAlreadyEnteredOobeMode = (True, Severity.Error, Facility.ModulePowerManager, 16)

    PowerManagerAlreadyExitedOobeMode = (True, Severity.Error, Facility.ModulePowerManager, 17)

    PowerManagerAlreadyEnteredSleepMode = (True, Severity.Error, Facility.ModulePowerManager, 18)

    PowerManagerAlreadyExitedSleepMode = (True, Severity.Error, Facility.ModulePowerManager, 19)

    PowerManagerInvalidModuleId = (True, Severity.Error, Facility.ModulePowerManager, 20)

    PowerManagerInvalidModuleState = (True, Severity.Error, Facility.ModulePowerManager, 21)

    PowerManagerInvalidPowerMode = (True, Severity.Error, Facility.ModulePowerManager, 22)

    PowerManagerInvalidTransition = (True, Severity.Error, Facility.ModulePowerManager, 23)

    PowerManagerShutdownAlreadyInProgress = (True, Severity.Error, Facility.ModulePowerManager, 24)

    PowerManagerDimmingDisabled = (True, Severity.Error, Facility.ModulePowerManager, 25)

    PowerManagerDimmingEnabled = (True, Severity.Error, Facility.ModulePowerManager, 26)

    PowerManagerResetReasonFailedBatteryKill = (
        True,
        Severity.Error,
        Facility.ModulePowerManager,
        27,
    )

    PowerManagerUnitTestFailed = (True, Severity.Error, Facility.ModulePowerManager, 28)

    PowerManagerBiometricSensorsAlreadyOn = (True, Severity.Error, Facility.ModulePowerManager, 29)

    PowerManagerBiometricSensorsAlreadyOff = (
        True,
        Severity.Error,
        Facility.ModulePowerManager,
        30,
    )

    PowerManagerGenericCleanReset = (True, Severity.Error, Facility.ModulePowerManager, 31)

    PowerManagerHardRequirementsStackFull = (True, Severity.Error, Facility.ModulePowerManager, 50)

    HrPowerManagerReinitialization = (True, Severity.Error, Facility.ModuleHrPowerManager, 0)

    HrPowerManagerUnitTestFailure = (True, Severity.Error, Facility.ModuleHrPowerManager, 1)

    FireballHardwareManagerBtAlreadySubscribed = (
        True,
        Severity.Error,
        Facility.ModuleFireballTilesModels,
        0,
    )

    FireballHardwareManagerBtNotSubscribed = (
        True,
        Severity.Error,
        Facility.ModuleFireballTilesModels,
        1,
    )

    SystemSettingsOperationNotImplemented = (
        True,
        Severity.Error,
        Facility.ModuleSystemSettings,
        0,
    )

    SystemSettingsOperationNotStarted = (True, Severity.Error, Facility.ModuleSystemSettings, 1)

    SystemSettingsOperationBusy = (True, Severity.Error, Facility.ModuleSystemSettings, 2)

    SystemSettingsOperationRetrying = (True, Severity.Null, Facility.ModuleSystemSettings, 0)

    SystemSettingsResetReasonFactoryReset = (True, Severity.Null, Facility.ModuleSystemSettings, 1)

    SystemSettingsStageSkipped = (True, Severity.Null, Facility.ModuleSystemSettings, 2)

    NotificationInvalidNotificationType = (True, Severity.Error, Facility.ModuleNotification, 0)

    NotificationAddFailed = (True, Severity.Error, Facility.ModuleNotification, 1)

    NotificationRemoveFailed = (True, Severity.Error, Facility.ModuleNotification, 2)

    NotificationRemoveAllFailed = (True, Severity.Error, Facility.ModuleNotification, 3)

    NotificationInitializationFailed = (True, Severity.Error, Facility.ModuleNotification, 4)

    NotificationCleanUpFailed = (True, Severity.Error, Facility.ModuleNotification, 5)

    NotificationUnitTestAppNotInstalled = (True, Severity.Error, Facility.ModuleNotification, 6)

    NotificationUnitTestFailed = (True, Severity.Error, Facility.ModuleNotification, 7)

    NotificationUnitTestDialogFailed = (True, Severity.Error, Facility.ModuleNotification, 8)

    NotificationUnitTestBadgeFailed = (True, Severity.Error, Facility.ModuleNotification, 9)

    NotificationGenericBadData = (True, Severity.Error, Facility.ModuleNotification, 100)

    NotificationGenericBufferReadPosition = (
        True,
        Severity.Error,
        Facility.ModuleNotification,
        101,
    )

    NotificationGenericDataBadType = (True, Severity.Error, Facility.ModuleNotification, 102)

    NotificationGenericDataBadId = (True, Severity.Error, Facility.ModuleNotification, 103)

    NotificationGenericDataBadValue = (True, Severity.Error, Facility.ModuleNotification, 104)

    NotificationMultipleSubscribersNotSupported = (
        True,
        Severity.Error,
        Facility.ModuleNotification,
        65533,
    )

    NotificationNotSupported = (True, Severity.Error, Facility.ModuleNotification, 65534)

    NotificationError = (True, Severity.Error, Facility.ModuleNotification, 65535)

    InstrumentationInvalidIndex = (True, Severity.Error, Facility.ModuleInstrumentation, 0)

    InstrumentationModuleUnintialized = (True, Severity.Error, Facility.ModuleInstrumentation, 1)

    InstrumentationModuleIsBusy = (True, Severity.Error, Facility.ModuleInstrumentation, 2)

    InstrumentationUnusedIndex = (True, Severity.Error, Facility.ModuleInstrumentation, 3)

    PalInvalidServiceIndex = (True, Severity.Error, Facility.ModulePal, 1)

    FtlTouchManagerGestureSubscriberNotFound = (
        True,
        Severity.Error,
        Facility.ModuleFtlTouchManager,
        0,
    )

    FtlTouchManagerGestureSubscriberRemovalError = (
        True,
        Severity.Error,
        Facility.ModuleFtlTouchManager,
        1,
    )

    PersistedStatisticsNotInitialized = (
        True,
        Severity.Error,
        Facility.ModulePersistedStatistics,
        0,
    )

    PersistedStatisticsFileIoBusy = (True, Severity.Error, Facility.ModulePersistedStatistics, 1)

    PersistedStatisticsInvalidFileSize = (
        True,
        Severity.Error,
        Facility.ModulePersistedStatistics,
        2,
    )

    PersistedStatisticsInvalidBufferSize = (
        True,
        Severity.Error,
        Facility.ModulePersistedStatistics,
        3,
    )

    PersistedApplicationDataFileIoBusy = (
        True,
        Severity.Error,
        Facility.ModulePersistedApplicationData,
        0,
    )

    PersistedApplicationDataInvalidMetricData = (
        True,
        Severity.Error,
        Facility.ModulePersistedApplicationData,
        1,
    )

    CortanaNotImplemented = (True, Severity.Error, Facility.ModuleCortana, 0)

    CortanaInvalidParameter = (True, Severity.Error, Facility.ModuleCortana, 1)

    CortanaNotAvailable = (True, Severity.Error, Facility.ModuleCortana, 2)

    CortanaNotRunning = (True, Severity.Error, Facility.ModuleCortana, 3)

    CortanaButtonActivated = (True, Severity.Null, Facility.ModuleCortana, 4)

    CortanaButtonRelease = (True, Severity.Null, Facility.ModuleCortana, 5)

    CortanaNotificationSuccess = (True, Severity.Null, Facility.ModuleCortana, 6)

    CortanaNotificationError = (True, Severity.Error, Facility.ModuleCortana, 7)

    CortanaNotificationMore = (True, Severity.Null, Facility.ModuleCortana, 8)

    CortanaVoicePushStarted = (True, Severity.Null, Facility.ModuleCortana, 9)

    CortanaNotificationTimeout = (True, Severity.Null, Facility.ModuleCortana, 10)

    CortanaNotificationMessage = (True, Severity.Null, Facility.ModuleCortana, 11)

    FireballAppsManagementInvalidOrCorruptAsset = (
        True,
        Severity.Error,
        Facility.ModuleFireballAppsManagement,
        0,
    )

    FireballAppsManagementCorruptLayout = (
        True,
        Severity.Error,
        Facility.ModuleFireballAppsManagement,
        1,
    )

    FireballAppsManagementTooManyApps = (
        True,
        Severity.Error,
        Facility.ModuleFireballAppsManagement,
        2,
    )

    FireballAppsManagementAppIdNotFound = (
        True,
        Severity.Error,
        Facility.ModuleFireballAppsManagement,
        3,
    )

    FireballAppsManagementNoResourcesProvided = (
        True,
        Severity.Error,
        Facility.ModuleFireballAppsManagement,
        4,
    )

    FireballAppsManagementWriteAlreadyExists = (
        True,
        Severity.Error,
        Facility.ModuleFireballAppsManagement,
        5,
    )

    FireballAppsManagementAppAlreadyExists = (
        True,
        Severity.Error,
        Facility.ModuleFireballAppsManagement,
        6,
    )

    FireballAppsManagementCannotModifyNativeIcons = (
        True,
        Severity.Error,
        Facility.ModuleFireballAppsManagement,
        7,
    )

    FireballAppsManagementInvalidTileIconIndex = (
        True,
        Severity.Error,
        Facility.ModuleFireballAppsManagement,
        8,
    )

    FireballAppsManagementTilesNotYetLoaded = (
        True,
        Severity.Error,
        Facility.ModuleFireballAppsManagement,
        9,
    )

    BatteryGaugeAlreadyInstalled = (True, Severity.Error, Facility.ModuleBatteryGauge, 0)

    UnitTestsInvalidTestId = (True, Severity.Error, Facility.ModuleUnitTests, 0)

    InstalledAncsAppListFull = (True, Severity.Error, Facility.ModuleInstalledAppList, 0)

    InstalledAncsAppNameLengthIllegal = (True, Severity.Error, Facility.ModuleInstalledAppList, 1)

    InstalledAncsAppNotRegistered = (True, Severity.Error, Facility.ModuleInstalledAppList, 2)

    InstalledAncsAppListEmpty = (True, Severity.Error, Facility.ModuleInstalledAppList, 3)

    InstalledAncsFreshListInitialization = (
        True,
        Severity.Null,
        Facility.ModuleInstalledAppList,
        4,
    )

    InstalledAncsDuplicateNameEntry = (True, Severity.Error, Facility.ModuleInstalledAppList, 5)

    InstalledAncsDuplicateGuidEntry = (True, Severity.Error, Facility.ModuleInstalledAppList, 6)

    InstalledAncsAppListUnitTestFailed = (True, Severity.Error, Facility.ModuleInstalledAppList, 7)

    InstalledAncsAppListUninitialized = (True, Severity.Error, Facility.ModuleInstalledAppList, 8)

    InstalledAppListInvalidParameter = (True, Severity.Error, Facility.ModuleInstalledAppList, 9)

    InstalledAppListAppNotFound = (True, Severity.Error, Facility.ModuleInstalledAppList, 10)

    InstalledAppListListFull = (True, Severity.Error, Facility.ModuleInstalledAppList, 11)

    InstalledAppListAppIdNotFound = (True, Severity.Error, Facility.ModuleInstalledAppList, 12)

    InstalledAppListPageIndexInvalid = (True, Severity.Error, Facility.ModuleInstalledAppList, 13)

    InstalledAppListPageLayoutFormatInvalid = (
        True,
        Severity.Error,
        Facility.ModuleInstalledAppList,
        14,
    )

    KFrostSessionAlreadyRunning = (True, Severity.Error, Facility.ModuleKfrost, 0)

    KFrostTestNotRunning = (True, Severity.Error, Facility.ModuleKfrost, 1)

    KFrostInvalidArgs = (True, Severity.Error, Facility.ModuleKfrost, 2)

    KFrostUsbParamsNotLoaded = (True, Severity.Error, Facility.ModuleKfrost, 3)

    KFrostUsbNoRunFlags = (True, Severity.Error, Facility.ModuleKfrost, 4)

    KFrostUsbParamInvalidFile = (True, Severity.Error, Facility.ModuleKfrost, 5)

    KFrostUsbAllocFail = (True, Severity.Error, Facility.ModuleKfrost, 6)

    KFrostNotPresent = (True, Severity.Error, Facility.ModuleKfrost, 7)

    KFrostInvalidId = (True, Severity.Error, Facility.ModuleKfrost, 8)

    KFrostOutOfBounds = (True, Severity.Error, Facility.ModuleKfrost, 9)

    VoicePushMic = (True, Severity.Null, Facility.ModuleVoicePush, 0)

    VoicePushMicOffPushInProgress = (True, Severity.Null, Facility.ModuleVoicePush, 1)

    VoicePushPushComplete = (True, Severity.Null, Facility.ModuleVoicePush, 2)

    VoicePushCancelled = (True, Severity.Error, Facility.ModuleVoicePush, 3)

    VoicePushAlreadyInProgress = (True, Severity.Error, Facility.ModuleVoicePush, 4)

    VoicePushNotInProgress = (True, Severity.Error, Facility.ModuleVoicePush, 5)

    VoicePushServiceNotAvailable = (True, Severity.Error, Facility.ModuleVoicePush, 6)

    VoicePushAirplaneMode = (True, Severity.Error, Facility.ModuleVoicePush, 7)

    VoicePushStopInProgress = (True, Severity.Error, Facility.ModuleVoicePush, 8)

    VoicePushCancelInProgress = (True, Severity.Error, Facility.ModuleVoicePush, 9)

    AppMainResetReasonFailedInitialization = (True, Severity.Error, Facility.ApplicationsBase, 0)

    App2UpResetReasonSramUpdateComplete = (True, Severity.Error, Facility.Application2UP, 0)
