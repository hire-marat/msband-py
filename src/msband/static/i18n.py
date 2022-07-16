from msband.sugar import EnumBase, IntEnumAdapter


class LocaleId(EnumBase):
    XX = 0x00
    US = 0x01
    GB = 0x02
    CA = 0x03
    FR = 0x04
    DE = 0x05
    IT = 0x06
    MX = 0x07
    ES = 0x08
    AU = 0x09
    NZ = 0x0A
    DK = 0x0B
    FI = 0x0C
    NO = 0x0D
    NL = 0x0E
    PT = 0x0F
    SE = 0x10
    PL = 0x11
    CN = 0x12
    TW = 0x13
    JP = 0x14
    KR = 0x15
    AT = 0x16
    BE = 0x17
    HK = 0x18
    IE = 0x19
    SG = 0x1A
    CH = 0x1B
    ZA = 0x1C
    SA = 0x1D
    AE = 0x1E


LocaleIdAdapter = IntEnumAdapter(LocaleId)


class Language(EnumBase):
    xx_XX = 0x00
    en_US = 0x01
    en_GB = 0x02
    fr_CA = 0x03
    fr_FR = 0x04
    de_DE = 0x05
    it_IT = 0x06
    es_MX = 0x07
    es_ES = 0x08
    es_US = 0x09
    da_DK = 0x0A
    fi_FI = 0x0B
    nb_NO = 0x0C
    nl_NL = 0x0D
    pt_PT = 0x0E
    sv_SE = 0x0F
    pl_PL = 0x10
    zn_CN = 0x11
    zn_TW = 0x12
    ja_JP = 0x13
    ko_KR = 0x14


LanguageAdapter = IntEnumAdapter(Language)


class DisplayTimeFormat(EnumBase):
    Null = 0
    HHmmss = 1
    Hmmss = 2
    hhmmss = 3
    hmmss = 4


DisplayTimeFormatAdapter = IntEnumAdapter(DisplayTimeFormat)


class DisplayDateFormat(EnumBase):
    Null = 0
    yyyyMMdd = 1
    ddMMyyyy = 2
    dMMyyyy = 3
    MMddyyyy = 4
    Mdyyyy = 5


DisplayDateFormatAdapter = IntEnumAdapter(DisplayDateFormat)


class UnitType(EnumBase):
    Null = 0
    Imperial = 1
    Metric = 2


UnitTypeAdapter = IntEnumAdapter(UnitType)
