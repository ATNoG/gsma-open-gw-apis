import asyncio
import logging

import httpx
import paho.mqtt.client as mqtt
from paho.mqtt.enums import CallbackAPIVersion

from src.nef_auth import NEFAuth
from src.schemas import CPMMessage, MCMMessage, ReferencePositionWithConfidence
from src.settings import settings
from src.async_mqtt import Event, EventType, MessageEvent, MqttAsyncioHelper


async def handle_message(event: MessageEvent, nef_client: httpx.AsyncClient) -> None:
    parts = event.topic.rsplit("/", 2)

    type = parts[-1]
    vehicle = parts[-2]

    referencePosition: ReferencePositionWithConfidence
    match type:
        case "MCM":
            mcm_data = MCMMessage.model_validate_json(event.payload)
            referencePosition = mcm_data.payload.basicContainer.referencePosition
        case "CPM":
            cpm_data = CPMMessage.model_validate_json(event.payload)
            referencePosition = cpm_data.cpm.managementContainer.referencePosition
        case _:
            logging.warning(
                "Unknown message type (type: %s, topic: %s)", type, event.topic
            )
            return

    supi = settings.vehicle_supis.get(vehicle)

    if supi is None:
        logging.error(
            "Received message for vehicle with no associated supi (vehicle: %s)",
            vehicle,
        )
        return

    latitude = referencePosition.latitude * 10**-7
    longitude = referencePosition.longitude * 10**-7

    logging.info(
        "Position update vehicle: %s, lat: %f, lon: %f", vehicle, latitude, longitude
    )

    res = await nef_client.post(
        f"/api/v1/ue_movement/update_location/{supi}",
        json={"shape": "POINT", "point": {"lat": latitude, "lon": longitude}},
    )

    if not res.is_success:
        logging.error(
            "Error while updating location (status code: %d): %s",
            res.status_code,
            res.text,
        )


async def handle_event(event: Event, nef_client: httpx.AsyncClient) -> None:
    try:
        if event.type == EventType.Message:
            await handle_message(event, nef_client)
        elif event.type == EventType.Connect:
            logging.info("Connected to broker (reason code: %s)", event.reason_code)
        elif event.type == EventType.Disconnect:
            logging.error("Broker disconnected (reason code: %s)", event.reason_code)
    except (KeyboardInterrupt, asyncio.CancelledError) as e:
        raise e
    except Exception as e:
        logging.error("Exception while handling mqtt event", e)


async def main() -> None:
    loop = asyncio.get_event_loop()

    nef_auth = NEFAuth(
        nef_url=settings.nef.url,
        nef_username=settings.nef.username,
        nef_password=settings.nef.password,
    )
    nef_client = httpx.AsyncClient(base_url=str(settings.nef.url), auth=nef_auth)

    client = mqtt.Client(
        CallbackAPIVersion.VERSION2,
        client_id=settings.broker.client_id,
        transport=settings.broker.transport,
    )

    if settings.broker.transport == "websockets":
        client.ws_set_options(path=settings.broker.ws_path)

    client.username_pw_set(settings.broker.username, settings.broker.password)

    aioh = MqttAsyncioHelper(loop, client)

    client.connect(settings.broker.host, settings.broker.port, 60)

    topic_base_path = settings.topic_base_path.rstrip("/")
    for vehicle_id in settings.vehicle_supis.keys():
        client.subscribe(f"{topic_base_path}/{vehicle_id}/CPM")
        client.subscribe(f"{topic_base_path}/{vehicle_id}/MCM")

    try:
        last_handled = None

        async for event in aioh.get_events():
            if (
                last_handled is not None
                and (loop.time() - last_handled) < settings.event_throttling
            ):
                logging.debug("Throttling event")
                continue

            last_handled = loop.time()

            await handle_event(event, nef_client)
    except (KeyboardInterrupt, asyncio.CancelledError):
        pass

    client.disconnect()


asyncio.run(main())
