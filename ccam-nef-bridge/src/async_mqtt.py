import enum
import asyncio
from dataclasses import dataclass
from typing import Any, AsyncIterator, Literal

import paho.mqtt.client as mqtt
from paho.mqtt.properties import Properties
from paho.mqtt.reasoncodes import ReasonCode


class EventType(enum.Enum):
    Connect = enum.auto()
    Disconnect = enum.auto()
    Message = enum.auto()


@dataclass
class MessageEvent:
    topic: str
    payload: bytes
    type: Literal[EventType.Message] = EventType.Message


@dataclass
class ConnectEvent:
    reason_code: ReasonCode

    type: Literal[EventType.Connect] = EventType.Connect


@dataclass
class DisconnectEvent:
    reason_code: ReasonCode

    type: Literal[EventType.Disconnect] = EventType.Disconnect


type Event = MessageEvent | ConnectEvent | DisconnectEvent


class MqttAsyncioHelper:
    def __init__(self, loop: asyncio.AbstractEventLoop, client: mqtt.Client) -> None:
        self.loop = loop

        self.event_queue: asyncio.Queue[Event] = asyncio.Queue()

        self.client = client

        self.client.on_message = self.on_message
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect

        self.client.on_socket_open = self.on_socket_open
        self.client.on_socket_close = self.on_socket_close
        self.client.on_socket_register_write = self.on_socket_register_write
        self.client.on_socket_unregister_write = self.on_socket_unregister_write

    def on_message(
        self, client: mqtt.Client, userdata: Any, msg: mqtt.MQTTMessage
    ) -> None:
        event = MessageEvent(topic=msg.topic, payload=msg.payload)
        self.loop.call_soon_threadsafe(self.event_queue.put_nowait, event)

    def on_connect(
        self,
        client: mqtt.Client,
        userdata: Any,
        flags: mqtt.ConnectFlags,
        reason_code: ReasonCode,
        properties: Properties | None,
    ) -> None:
        event = ConnectEvent(reason_code=reason_code)
        self.loop.call_soon_threadsafe(self.event_queue.put_nowait, event)

    def on_disconnect(
        self,
        client: mqtt.Client,
        userdata: Any,
        flags: mqtt.DisconnectFlags,
        reason_code: ReasonCode,
        properties: Properties | None,
    ) -> None:
        event = DisconnectEvent(reason_code=reason_code)
        self.loop.call_soon_threadsafe(self.event_queue.put_nowait, event)

    async def get_events(self) -> AsyncIterator[Event]:
        while True:
            yield await self.event_queue.get()

    def on_socket_open(
        self, client: mqtt.Client, userdata: Any, sock: "mqtt.SocketLike"
    ) -> None:
        def cb() -> None:
            client.loop_read()

        self.loop.add_reader(sock, cb)
        self.misc = self.loop.create_task(self.misc_loop())

    def on_socket_close(
        self, client: mqtt.Client, userdata: Any, sock: "mqtt.SocketLike"
    ) -> None:
        self.loop.remove_reader(sock)
        self.misc.cancel()

    def on_socket_register_write(
        self, client: mqtt.Client, userdata: Any, sock: "mqtt.SocketLike"
    ) -> None:
        def cb() -> None:
            client.loop_write()

        self.loop.add_writer(sock, cb)

    def on_socket_unregister_write(
        self, client: mqtt.Client, userdata: Any, sock: "mqtt.SocketLike"
    ) -> None:
        self.loop.remove_writer(sock)

    async def misc_loop(self) -> None:
        while self.client.loop_misc() == mqtt.MQTT_ERR_SUCCESS:
            try:
                await asyncio.sleep(1)
            except asyncio.CancelledError:
                break
