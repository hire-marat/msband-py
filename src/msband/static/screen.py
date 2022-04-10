import enum
from construct import Adapter


class ScreenAdapter(Adapter):
    def _encode(self, obj, context, path):
        return obj

    def _decode(self, obj, context, path):
        return Screen(obj)


class Screen(enum.IntEnum):
    Settings = 0x00
    Home = 0x01
    Me = 0x02
    Timer = 0x03
    Exercise = 0x04

    RawData = 0x05
    DebugControl = 0x06
    DebugInfo = 0x07
    InteractiveTouch = 0x08
    SimpleTouch = 0x09
    TestWidget = 0x0A

    Oobe = 0x0B
    OobeBoot = 0x0C
    OobeCharging = 0x0D
    OobeChargedBoot = 0x0E
    OobeLanguageSelect = 0x0F
    OobeWelcome = 0x10
    OobeBtPreSync = 0x11
    OobeBtSync = 0x12
    OobeBtPaired = 0x13
    OobeUpdates = 0x14
    OobeAlmostThere = 0x15
    OobePresButtonToStart = 0x16

    DebugStrip = 0x17

    SettingPower = 0x18
    SettingBiosensors = 0x19
    SettingConnection = 0x1A
    SettingAccessability = 0x1B
    SettingGlance = 0x1C
    SettingGeneral = 0x1D
    SettingUtilities = 0x1E
    SettingDND = 0x1F
    SettingAirplane = 0x20
    TextMessage = 0x21

    FontTest = 0x22

    RunStart = 0x23
    RunGpsChoice = 0x24
    RunGpsSearch = 0x25
    RunReadyToStart = 0x26
    RunInProgress = 0x27
    RunPaused = 0x28
    RunCompleted = 0x29
    Calendar = 0x2A
    Sleep = 0x2B
    SleepTrack = 0x2C
    SleepInProgress = 0x2D
    SleepPaused = 0x2E
    SleepCompleted = 0x2F
    SleepReadyToSleep = 0x30
    Call = 0x31

    BatteryDie = 0x32
    DebugDayClassification = 0x33
    DebugLogFile = 0x34
    TouchSensor = 0x35

    Syncing = 0x36
    SyncingAutoDismiss = 0x37
    Workout = 0x38
    WorkoutStart = 0x39
    WorkoutReadyToStart = 0x3A
    WorkoutInProgress = 0x3B
    WorkoutPaused = 0x3C
    WorkoutCompleted = 0x3D
    DebugGsrContact = 0x3E
    GuidedWorkout = 0x3F
    GuidedWorkoutLoad = 0x40
    GuidedWorkoutStart = 0x41
    GuidedWorkoutCurrentExercise = 0x42
    GuidedWorkoutIntersitial = 0x43
    GuidedWorkoutPaused = 0x44
    GuidedWorkoutCompleted = 0x45
    TimerTile = 0x46
    StopwatchRunning = 0x47
    StopwatchPaused = 0x48
    AlarmSetScreen = 0x49
    RunHowYouFelt = 0x4A
    RunHowYouFeltConfirmation = 0x4B
    DebugGps = 0x4C
    WorkoutHowYouFelt = 0x4D
    SleepHowYouFelt = 0x4E
    RunCountdown = 0x4F
    SettingsFromSubscreen = 0x50
    TimerTileFromSubscreen = 0x51
    DebugStripFromSubscreen = 0x52
    DebugBtConfig = 0x53
    HomeResetScroll = 0x54
    Resetting = 0x55
    Goodbye = 0x56
    Keyboard = 0x57
    NotificationDataView = 0x58
    NumScreenIds = 0x59

    IdUnknown = 0xFFFE
    Null = 0xFFFF
