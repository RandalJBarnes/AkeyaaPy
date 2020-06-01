"""Defines and implements the Settings class.

Classes
-------
Settings
    A dataclass for the Akeyaa analysis settings.

Raises
------
ValueError

Author
------
Dr. Randal J. Barnes
Department of Civil, Environmental, and Geo- Engineering
University of Minnesota

Version
-------
01 June 2020
"""

# -----------------------------------------------------------------------------
# These are the default settings for the Akeyaa analysis. TODO: revisit these
# default values after we have more exprience.
DEFAULT_AQUIFERS = None
DEFAULT_METHOD = "RLM"
DEFAULT_RADIUS = 3000
DEFAULT_REQUIRED = 25
DEFAULT_SPACING = 1000


# -----------------------------------------------------------------------------
# The following is a complete list of all 4-character aquifer codes used in
# the Minnesota County Well index as of 1 January 2020.
ALL_AQUIFERS = {
    "CAMB", "CECR", "CEMS", "CJDN", "CJDW", "CJMS", "CJSL", "CJTC", "CLBK",
    "CMFL", "CMRC", "CMSH", "CMTS", "CSLT", "CSLW", "CSTL", "CTCE", "CTCG",
    "CTCM", "CTCW", "CTLR", "CTMZ", "CWEC", "CWMS", "CWOC",
    "DCLP", "DCLS", "DCOG", "DCOM", "DCVA", "DCVL", "DCVU", "DEVO", "DPOG",
    "DPOM", "DSOG", "DSOM", "DSPL", "DWAP", "DWPR",
    "INDT", "KDNB", "KREG", "KRET", "MTPL",
    "ODCR", "ODGL", "ODPL", "ODUB", "OGCD", "OGCM", "OGDP", "OGPC", "OGPD",
    "OGPR", "OGSC", "OGSD", "OGSV", "OGVP", "OGWD", "OMAQ", "OMQD", "OMQG",
    "OPCJ", "OPCM", "OPCT", "OPCW", "OPDC", "OPGW", "OPNR", "OPOD", "OPSH",
    "OPSP", "OPVJ", "OPVL", "OPWR", "ORDO", "ORRV", "OSCJ", "OSCM", "OSCS",
    "OSCT", "OSPC", "OSTP", "OWIN",
    "PAAI", "PAAM", "PABD", "PABG", "PABK", "PACG", "PAEF", "PAES", "PAEY",
    "PAFL", "PAFR", "PAFV", "PAGR", "PAGU", "PAJL", "PAKG", "PALC", "PALG",
    "PALL", "PALP", "PALS", "PALT", "PALV", "PAMB", "PAMC", "PAMD", "PAMG",
    "PAML", "PAMR", "PAMS", "PAMT", "PAMU", "PAMV", "PANB", "PANL", "PANS",
    "PANU", "PAOG", "PAQF", "PASG", "PASH", "PASL", "PASM", "PASN", "PASR",
    "PAST", "PASZ", "PATL", "PAUD", "PAVC", "PAWB", "PCCR", "PCRG", "PCUU",
    "PEAG", "PEAL", "PEBC", "PEBI", "PEDN", "PEDQ", "PEFG", "PEFH", "PEFM",
    "PEGT", "PEGU", "PEHL", "PEIL", "PELF", "PELR", "PEMG", "PEML", "PEMN",
    "PEMU", "PEPG", "PEPK", "PEPP", "PEPZ", "PERB", "PERF", "PERV", "PESC",
    "PEST", "PESX", "PETR", "PEUD", "PEVT", "PEWR", "PEWT", "PEWV", "PMBB",
    "PMBE", "PMBI", "PMBL", "PMBM", "PMBO", "PMBR", "PMCV", "PMDA", "PMDC",
    "PMDE", "PMDF", "PMDL", "PMEP", "PMES", "PMFL", "PMGI", "PMGL", "PMHF",
    "PMHN", "PMHR", "PMLD", "PMMU", "PMNF", "PMNI", "PMNL", "PMNM", "PMNS",
    "PMPA", "PMRC", "PMSU", "PMTH", "PMUD", "PMUS", "PMVU", "PMWL", "PUDF",
    "QBAA", "QBUA", "QUUU", "QWTA", "RUUU", "UREG"
    }


# -----------------------------------------------------------------------------
class Settings:
    """A dataclass for the Akeyaa analysis settings.

    Attributes
    ----------
    aquifers : list, optional
        List of four-character aquifer abbreviation strings, as defined in
        Minnesota Geologic Survey"s coding system. If None, then all
        aquifers present will be included. The default is DEFAULT_AQUIFERS.

    method : str, optional
        The fitting method. This must be one of {"OLS", "RLM"}, where
            -- "OLS" ordinary least squares regression.
            -- "RLM" robust linear model regression with Tukey biweights.
        The default is DEFAULT_METHOD.

    radius : float, optional
        Search radius for neighboring wells. radius >= 1. The default is
        DEFAULT_RADIUS.

    required : int, optional
        Required number of neighboring wells. If fewer are found, the
        target location is skipped. required >= 6. The default is
        DEFAULT_REQUIRED.

    spacing : float, optional
        Grid spacing for target locations across the county. spacing >= 1.
        The default is DEFAULT_SPACING.

    Raises
    ------
    ValueError


    """

    def __init__(self,
                 aquifers: list = DEFAULT_AQUIFERS,
                 method: list = DEFAULT_METHOD,
                 radius: float = DEFAULT_RADIUS,
                 required: int = DEFAULT_REQUIRED,
                 spacing: float = DEFAULT_SPACING):
        self.aquifers = aquifers
        self.method = method
        self.radius = radius
        self.required = required
        self.spacing = spacing

    def __repr__(self):
        return ("Settings("
            "aquifers={0.aquifers!r}, "
            "method={0.method!r}, "
            "radius={0.radius!r}, "
            "required={0.required!r}, "
            "spacing={0.spacing!r})".format(self))

    def __eq__(self, other):
        return ((self.__class__ == other.__class__) and
                (self.aquifers == other.aquifers) and
                (self.method == other.method) and
                (self.radius == other.radius) and
                (self.required == other.required) and
                (self.spacing == other.spacing))

    @property
    def aquifers(self) -> list:
        return self._aquifers

    @aquifers.setter
    def aquifers(self, aquifers: list):
        if (aquifers is not None) and (not set.issubset(set(aquifers), ALL_AQUIFERS)):
            raise ValueError("Unknown aquifer code(s)")
        else:
            self._aquifers = aquifers

    @property
    def method(self) -> str:
        return self._method

    @method.setter
    def method(self, method: str):
        if method not in ["OLS", "RLM"]:
            raise ValueError("'method' must be one of {'OLS', 'RLM'}")
        else:
            self._method = method

    @property
    def radius(self) -> float:
        return self._radius

    @radius.setter
    def radius(self, radius: float):
        if radius < 1.0:
            raise ValueError("'radius' must be >= 1")
        else:
            self._radius = radius

    @property
    def required(self) -> int:
        return self._required

    @required.setter
    def required(self, required: int):
        if required < 6:
            raise ValueError("'required' must be >= 6")
        else:
            self._required = required

    @property
    def spacing(self) -> float:
        return self._spacing

    @spacing.setter
    def spacing(self, spacing: float):
        if spacing < 1.0:
            raise ValueError("'spacing' must be >= 1")
        else:
            self._spacing = spacing
