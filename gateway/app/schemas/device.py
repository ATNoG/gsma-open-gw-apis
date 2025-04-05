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


class DeviceIpv4Addr1(BaseModel):
    publicAddress: SingleIpv4Addr
    privateAddress: SingleIpv4Addr
    publicPort: Optional[Port] = None


class DeviceIpv4Addr2(BaseModel):
    publicAddress: SingleIpv4Addr
    privateAddress: Optional[SingleIpv4Addr] = None
    publicPort: Port


DeviceIpv4Addr = Annotated[
    Union[DeviceIpv4Addr1, DeviceIpv4Addr2],
    Field(
        ...,
        description="The device should be identified by either the public (observed) IP address and port as seen by the application server, or the private (local) and any public (observed) IP addresses in use by the device (this information can be obtained by various means, for example from some DNS servers).\n\nIf the allocated and observed IP addresses are the same (i.e. NAT is not in use) then  the same address should be specified for both publicAddress and privateAddress.\n\nIf NAT64 is in use, the device should be identified by its publicAddress and publicPort, or separately by its allocated IPv6 address (field ipv6Address of the Device object)\n\nIn all cases, publicAddress must be specified, along with at least one of either privateAddress or publicPort, dependent upon which is known. In general, mobile devices cannot be identified by their public IPv4 address alone.\n",
        example={"publicAddress": "84.125.93.10", "publicPort": 59765},
    ),
]

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
