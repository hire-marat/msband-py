from msband.sugar import IntEnumAdapter, EnumBase


class OobeStage(EnumBase):
    AskPhoneType = 0
    DownloadMessage = 1
    WaitingOnPhoneToEnterCode = 2
    WaitingOnPhoneToAcceptPairing = 3
    PairingSuccess = 4
    CheckingForUpdate = 5
    StartingUpdate = 6
    UpdateComplete = 7
    WaitingOnPhoneToCompleteOobe = 8
    PressActionButton = 9

    ErrorState = 10
    PairMessage = 11

    PreStateCharging = 100
    PreStateLanguageSelect = 101


OobeStageAdapter = IntEnumAdapter(OobeStage)
