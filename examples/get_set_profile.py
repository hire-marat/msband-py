from msband.static.command import *
from msband.protocol import ProtocolInterface
from msband.static import Profile, LocaleId, Language, DisplayDateFormat


# Connect using your preferred interface
iband: ProtocolInterface = ...


profile: Profile = iband.command(ProfileGetDataApp)

profile.DeviceName = "i" * 14 + "ab"  # the b won't be displayed in (i)
profile.LocaleName = "Custom"

profile.LocaleId = LocaleId.GB
profile.Language = Language.en_GB

profile.DateFormat = DisplayDateFormat.yyyyMMdd
profile.DateSeparator = "/"
profile.DecimalSeparator = "."

iband.command(ProfileSetDataApp, Profile=profile)
