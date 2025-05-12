from enum import Enum
from typing import Optional, List, Annotated
from typing_extensions import TypeAlias
from pydantic import BaseModel, Field, AnyHttpUrl


Link: TypeAlias = AnyHttpUrl


# TS 29.571
SupportedFeatures: TypeAlias = Annotated[
    str,
    Field(
        pattern=r"^[A-Fa-f0-9]*$",
        description='A string used to indicate the features supported by an API that is used as defined in clause  6.6 in 3GPP TS 29.500. The string shall contain a bitmask indicating supported features in  hexadecimal representation Each character in the string shall take a value of "0" to "9",  "a" to "f" or "A" to "F" and shall represent the support of 4 features as described in  table\xa05.2.2-3. The most significant character representing the highest-numbered features shall  appear first in the string, and the character representing features 1 to 4 shall appear last  in the string. The list of features and their numbering (starting with 1) are defined  separately for each API. If the string contains a lower number of characters than there are  defined features for an API, all features that would be represented by characters that are not  present in the string are not supported.',
    ),
]


# TS 29.571
Gpsi: TypeAlias = Annotated[
    str,
    Field(
        pattern=r"^(msisdn-[0-9]{5,15}|extid-[^@]+@[^@]+|.+)$",
        description="String identifying a Gpsi shall contain either an External Id or an MSISDN.  It shall be formatted as follows -External Identifier= \"extid-'extid', where 'extid'  shall be formatted according to clause 19.7.2 of 3GPP TS 23.003 that describes an  External Identifier.",
    ),
]


# TS 29.122
class FlowInfo(BaseModel):
    """Represents IP flow information."""

    flowId: Annotated[int, Field(description="Indicates the IP flow identifier.")]
    flowDescriptions: Annotated[
        Optional[List[str]],
        Field(
            description="Indicates the packet filters of the IP flow. Refer to clause 5.3.8 of 3GPP TS 29.214 for encoding. It shall contain UL and/or DL IP flow description.",
            min_length=1,
            max_length=2,
        ),
    ] = None


# TS 29.122
class UserPlaneEvent(str, Enum):
    SESSION_TERMINATION = "SESSION_TERMINATION"
    LOSS_OF_BEARER = "LOSS_OF_BEARER"  # 4G Only
    RECOVERY_OF_BEARER = "RECOVERY_OF_BEARER"  # 4G Only
    RELEASE_OF_BEARER = "RELEASE_OF_BEARER"  # 4G Only
    USAGE_REPORT = "USAGE_REPORT"
    FAILED_RESOURCES_ALLOCATION = "FAILED_RESOURCES_ALLOCATION"
    QOS_GUARANTEED = "QOS_GUARANTEED"
    QOS_NOT_GUARANTEED = "QOS_NOT_GUARANTEED"
    QOS_MONITORING = "QOS_MONITORING"
    SUCCESSFUL_RESOURCES_ALLOCATION = "SUCCESSFUL_RESOURCES_ALLOCATION"
    ACCESS_TYPE_CHANGE = "ACCESS_TYPE_CHANGE"
    PLMN_CHG = "PLMN_CHG"
    L4S_NOT_AVAILABLE = "L4S_NOT_AVAILABLE"
    L4S_AVAILABLE = "L4S_AVAILABLE"
    BAT_OFFSET_INFO = "BAT_OFFSET_INFO"
    RT_DELAY_TWO_QOS_FLOWS = "RT_DELAY_TWO_QOS_FLOWS"
    PACK_DELAY_VAR = "PACK_DELAY_VAR"
