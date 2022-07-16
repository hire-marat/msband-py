from msband.sugar import EnumBase, IntEnumAdapter


"""
case VibrationType.NotificationOneTone:
    return BandVibrationType.ToastTextMessage;
case VibrationType.NotificationTwoTone:
    return BandVibrationType.AlertIncomingCall;
case VibrationType.NotificationAlarm:
    return BandVibrationType.AlertAlarm;
case VibrationType.NotificationTimer:
    return BandVibrationType.AlertTimer;
case VibrationType.OneToneHigh:
    return BandVibrationType.ExerciseGuidedWorkoutTimer;
case VibrationType.TwoToneHigh:
    return BandVibrationType.ExerciseGuidedWorkoutCircuitComplete;
case VibrationType.ThreeToneHigh:
    return BandVibrationType.ExerciseGuidedWorkoutComplete;
case VibrationType.RampUp:
    return BandVibrationType.SystemStartUp;
case VibrationType.RampDown:
    return BandVibrationType.SystemShutDown;
"""


class VibrationPattern(EnumBase):
    SystemBatteryCharging = 0x00
    SystemBatteryFull = 0x01
    SystemBatteryLow = 0x02
    SystemBatteryCritical = 0x03
    SystemShutDown = 0x04
    SystemStartUp = 0x05
    SystemButtonFeedback = 0x06
    ToastTextMessage = 0x07
    ToastMissedCall = 0x08
    ToastVoiceMail = 0x09
    ToastFacebook = 0x0A
    ToastTwitter = 0x0B
    ToastMeInsights = 0x0C
    ToastWeather = 0x0D
    ToastFinance = 0x0E
    ToastSports = 0x0F
    AlertIncomingCall = 0x10
    AlertAlarm = 0x11
    AlertTimer = 0x12
    AlertCalendar = 0x13
    VoiceListen = 0x14
    VoiceDone = 0x15
    VoiceAlert = 0x16
    ExerciseRunLap = 0x17
    ExerciseRunGpsLock = 0x18
    ExerciseRunGpsError = 0x19
    ExerciseWorkoutTimer = 0x1A
    ExerciseGuidedWorkoutTimer = 0x1B
    ExerciseGuidedWorkoutComplete = 0x1C
    ExerciseGuidedWorkoutCircuitComplete = 0x1D
    Pulses = 0x1E
    SuddenBuzz = 0x1F
    VoiceAlert2 = 0x20
    SnapBack = 0x21
    Fanfare = 0x22


VibrationPatternAdapter = IntEnumAdapter(VibrationPattern)
