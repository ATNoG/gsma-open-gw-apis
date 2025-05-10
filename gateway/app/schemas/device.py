from typing import Annotated, Optional, Union
from ipaddress import IPv4Address, IPv6Address
from pydantic import BaseModel, Field

PhoneNumber = Annotated[
    str,
    Field(
        pattern=r"^\+[1-9][0-9]{4,14}$",
        description="A public identifier addressing a telephone subscription. In mobile networks it corresponds to the MSISDN (Mobile Station International Subscriber Directory Number). In order to be globally unique it has to be formatted in international format, according to E.164 standard, prefixed with '+'.",
        examples=["+123456789"],
    ),
]

NetworkAccessIdentifier = Annotated[
    str,
    Field(
        description="A public identifier addressing a subscription in a mobile network. In 3GPP terminology, it corresponds to the GPSI formatted with the External Identifier ({Local Identifier}@{Domain Identifier}). Unlike the telephone number, the network access identifier is not subjected to portability ruling in force, and is individually managed by each operator.",
        examples=["123456789@domain.com"],
    ),
]

Port = Annotated[int, Field(description="TCP or UDP port number", ge=0, le=65535)]

SingleIpv4Addr = Annotated[
    IPv4Address,
    Field(
        description="A single IPv4 address with no subnet mask",
        examples=["84.125.93.10"],
    ),
]


class DeviceIpv4Addr(BaseModel):
    publicAddress: SingleIpv4Addr
    privateAddress: SingleIpv4Addr
    publicPort: Optional[Port] = None


DeviceIpv6Addr = Annotated[
    IPv6Address,
    Field(
        ...,
        description="The device should be identified by the observed IPv6 address, or by any single IPv6 address from within the subnet allocated to the device (e.g. adding ::0 to the /64 prefix).\n",
        example="2001:db8:85a3:8d3:1319:8a2e:370:7344",
    ),
]


class Device(BaseModel):
    phoneNumber: Optional[PhoneNumber] = None
    networkAccessIdentifier: Optional[NetworkAccessIdentifier] = None
    ipv4Address: Optional[DeviceIpv4Addr] = None
    ipv6Address: Optional[DeviceIpv6Addr] = None
