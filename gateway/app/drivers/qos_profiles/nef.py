from typing import List

import math
import httpx
from pydantic import TypeAdapter

from app.drivers.nef_auth import NEFAuth
from app.interfaces.qos_profiles import QoSProfilesInterface
from app.schemas.nef import NEFNamedQoSProfile, NEFQoSProfile
from app.schemas.qos_profiles import (
    Duration,
    QosProfile,
    QosProfileDeviceRequest,
    QosProfileStatus,
    Rate,
    RateUnitEnum,
    TimeUnitEnum,
)
from app.settings import NEFSettings


def _calculate_rates_table() -> List[tuple[int, RateUnitEnum]]:
    table = []
    current_multiplier = 1

    for unit in RateUnitEnum:
        table.append((current_multiplier, unit))
        current_multiplier *= 1000

    return table


_rates_table = _calculate_rates_table()


def _calculate_rate_from_bps(value: int) -> Rate:
    multiplier, unit = next(
        ((m, u) for m, u in reversed(_rates_table) if value > m), (1, RateUnitEnum.bps)
    )
    return Rate(value=value // multiplier, unit=unit)


def _convert_nef_profile(name: str, nef_profile: NEFQoSProfile) -> QosProfile:
    profile = QosProfile(name=name, status=QosProfileStatus.ACTIVE)

    if nef_profile.uplinkBitRate is not None:
        profile.maxUpstreamRate = _calculate_rate_from_bps(nef_profile.uplinkBitRate)

    if nef_profile.downlinkBitRate is not None:
        profile.maxDownstreamRate = _calculate_rate_from_bps(
            nef_profile.downlinkBitRate
        )

    if nef_profile.packetDelayBudget is not None:
        profile.packetDelayBudget = Duration(
            value=nef_profile.packetDelayBudget, unit=TimeUnitEnum.Milliseconds
        )

    if nef_profile.packerErrRate is not None:
        parsedErrRate = float(nef_profile.packerErrRate)
        profile.packetErrorLossRate = math.ceil(-math.log10(parsedErrRate))

    return profile


class NefQoSProfilesInterface(QoSProfilesInterface):
    def __init__(self, nef_settings: NEFSettings) -> None:
        super().__init__()

        nef_auth = NEFAuth(
            nef_settings.url, nef_settings.username, nef_settings.password
        )
        self.httpx_client = httpx.AsyncClient(
            base_url=str(nef_settings.url), auth=nef_auth
        )

    async def get_qos_profiles(self, req: QosProfileDeviceRequest) -> List[QosProfile]:
        if req.name is not None:
            res = await self.httpx_client.get(
                f"/api/v1/qosInfo/qosCharacteristics/{req.name}"
            )

            if res.status_code == 404:
                return []

            if not res.is_success:
                raise Exception(
                    f"Expected succesful response, got {res.status_code}: {res.text}"
                )

            nef_profile = NEFQoSProfile.model_validate_json(res.content)
            return [_convert_nef_profile(req.name, nef_profile)]
        else:
            res = await self.httpx_client.get("/api/v1/qosInfo/qosCharacteristics")

            if not res.is_success:
                raise Exception(
                    f"Expected succesful response, got {res.status_code}: {res.text}"
                )

            profiles = TypeAdapter(List[NEFNamedQoSProfile]).validate_json(res.content)
            return list(
                map(lambda prof: _convert_nef_profile(prof.name, prof), profiles)
            )
