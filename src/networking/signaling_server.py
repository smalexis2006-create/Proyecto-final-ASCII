import asyncio
import websockets
import json

from src.networking.utils import generate_room_code

rooms = {}

async def handler(websocket):
    room_code = None

    try:
        async for message in websocket:
            data = json.loads(message)

            # Cliente crea o se une a sala
            if data["type"] == "join":
                room_code = data.get("room")

                # Si no manda código, se crea uno nuevo (HOST)
                if not room_code:
                    room_code = generate_room_code()

                if room_code not in rooms:
                    rooms[room_code] = []

                rooms[room_code].append(websocket)

                print(f"Cliente unido a sala {room_code}")

                # Le regresamos el código al cliente (importante para GUI después)
                await websocket.send(json.dumps({
                    "type": "room_assigned",
                    "room": room_code
                }))

            # Mensajes de señalización (WebRTC después)
            elif data["type"] == "signal":
                for client in rooms.get(room_code, []):
                    if client != websocket:
                        await client.send(json.dumps(data))

    except Exception as e:
        print("Error:", e)

    finally:
        if room_code and websocket in rooms.get(room_code, []):
            rooms[room_code].remove(websocket)
            print(f"Cliente salió de sala {room_code}")

async def main():
    async with websockets.serve(handler, "localhost", 8765):
        print("Servidor de signaling corriendo en ws://localhost:8765")
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())