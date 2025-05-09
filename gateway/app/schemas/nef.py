from typing import Optional, Annotated

from pydantic import (
    BaseModel,
    Field,
)


class NEFQoSProfile(BaseModel):
    uplinkBitRate: Annotated[
        Optional[int], Field(description="Uplink bandwidth in bps")
    ] = None
    downlinkBitRate: Annotated[
        Optional[int], Field(description="Downlink bandwidth in bps")
    ] = None
    packetDelayBudget: Annotated[
        Optional[int], Field(description="Packet delay budget in milliseconds")
    ] = None
    packerErrRate: Annotated[
        Optional[str],
        Field(description="Packet error rate in exponential form", examples=["4E-2"]),
    ] = None


class NEFNamedQoSProfile(NEFQoSProfile):
    name: str
