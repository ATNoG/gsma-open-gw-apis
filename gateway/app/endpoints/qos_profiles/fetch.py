from typing import List

from fastapi import APIRouter

from app.exceptions import ResourceNotFound
from app.schemas.qos_profiles import QosProfileDeviceRequest, QosProfile
from app.drivers.qos_profiles import QoSProfilesInterfaceDep


router = APIRouter()


@router.post("/retrieve-qos-profiles", response_model_exclude_unset=True)
async def retrieve_qos_profiles(
    body: QosProfileDeviceRequest, qos_profiles_interface: QoSProfilesInterfaceDep
) -> List[QosProfile]:
    return await qos_profiles_interface.get_qos_profiles(body)


@router.get("/qos-profiles/{name}", response_model_exclude_unset=True)
async def retrieve_qos_profile_by_name(
    name: str, qos_profiles_interface: QoSProfilesInterfaceDep
) -> QosProfile:
    res = await qos_profiles_interface.get_qos_profiles(
        QosProfileDeviceRequest(name=name)
    )

    if len(res) == 0:
        raise ResourceNotFound()

    return res[0]
