from typing import Annotated

import socketio
from fastapi import Depends

sio = socketio.AsyncServer(cors_allowed_origins="*", async_mode="asgi")


def get_socketio():
    return sio


SocketIODep = Annotated[socketio.AsyncServer, Depends(get_socketio)]
