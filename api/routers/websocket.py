import json
from fastapi import APIRouter, FastAPI, WebSocket, Request
from fastapi.responses import HTMLResponse
from fastapi.concurrency import run_until_first_complete
from broadcaster import Broadcast

broadcast = Broadcast("redis://localhost:6379")
router = APIRouter(prefix="/websocket", tags=["Web_socket"], on_startup=[broadcast.connect], on_shutdown=[broadcast.disconnect])

async def chatroom_ws_receiver(websocket: WebSocket, room_id: str):
    async for message in websocket.iter_text():
        await broadcast.publish(channel=f"chatroom_{room_id}", message=message)


async def chatroom_ws_sender(websocket: WebSocket, room_id: str):
    async with broadcast.subscribe(channel=f"chatroom_{room_id}") as subscriber:
        async for event in subscriber:
            await websocket.send_text(event.message)


@router.websocket("/algorithm_search/{room_id}")
async def websocket_chat(websocket: WebSocket, room_id: str):
    await websocket.accept()
    await run_until_first_complete(
        (chatroom_ws_receiver, {"websocket": websocket, "room_id":room_id}),
        (chatroom_ws_sender, {"websocket": websocket, "room_id":room_id}),
    )
    
async def send_message(room_id:str, json_point):
    await broadcast.publish(channel=f"chatroom_{room_id}", message=json_point)
    return None