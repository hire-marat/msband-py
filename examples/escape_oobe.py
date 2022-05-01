import datetime as dt
from msband.static.command import *
from msband.static.timezone import GMT
from msband.static.screen import Screen
from msband.static.oobe import OobeStage
from msband.protocol import ProtocolInterface
from msband.static import Profile, FirmwareApp


# Connect using your preferred interface
iband: ProtocolInterface = ...


if iband.command(CoreModuleWhoAmI) != FirmwareApp.App:
    raise NotImplementedError("This device is not running the main app")


if iband.command(SystemSettingsOobeCompleteGet):
    raise ZeroDivisionError("This device is already out of OOBE")


profile: Profile = iband.command(ProfileGetDataApp)


if iband.command(OobeGetStage) == OobeStage.PreStateCharging:
    raise NotImplementedError("In charging state, no idea what this means")


if iband.command(OobeGetStage) == OobeStage.PreStateLanguageSelect:
    raise ZeroDivisionError("Please set a language before proceeding")


iband.command(OobeSetStage, Stage=OobeStage.CheckingForUpdate)
iband.command(OobeSetStage, Stage=OobeStage.StartingUpdate)
iband.command(OobeSetStage, Stage=OobeStage.UpdateComplete)

iband.command(TimeSetUtcTime, NewTime=dt.datetime.utcnow().replace(tzinfo=dt.timezone.utc))

iband.command(FireballUINavigateToScreen, Screen=Screen.OobeBoot)

iband.command(
    SystemSettingsSetEphemerisFile,
    Data=b"\0" * 130,
)

iband.command(
    SystemSettingsSetTimeZone,
    TimeZone=GMT,
)

iband.command(OobeSetStage, Stage=OobeStage.WaitingOnPhoneToCompleteOobe)

profile.DeviceName = "Liberated Band"
profile.Telemetry = False

time_snap = dt.datetime.utcnow().replace(tzinfo=dt.timezone.utc)
profile.LastSync = time_snap
profile.HwagChangeTime = time_snap
profile.DeviceNameChangeTime = time_snap
profile.LocaleSettingsChangeTime = time_snap
profile.LanguageChangeTime = time_snap

iband.command(ProfileSetDataApp, Profile=profile)

iband.command(OobeFinalize)
