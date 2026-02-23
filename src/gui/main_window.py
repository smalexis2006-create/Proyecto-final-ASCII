import tkinter as tk
import asyncio
import websockets
import json
import threading

SERVER_URL = "ws://localhost:8765"


class App:
    def __init__(self, root):
        self.root = root
        self.root.title("ASCII P2P")
        self.root.geometry("400x300")

        self.label = tk.Label(root, text="ASCII P2P")
        self.label.pack(pady=10)

        self.room_label = tk.Label(root, text="")
        self.room_label.pack(pady=10)

        self.entry = tk.Entry(root)
        self.entry.pack(pady=5)

        self.host_btn = tk.Button(root, text="Host", command=self.host)
        self.host_btn.pack(pady=5)

        self.join_btn = tk.Button(root, text="Join", command=self.join)
        self.join_btn.pack(pady=5)

    # -------------------------
    # HOST
    # -------------------------
    def host(self):
        threading.Thread(target=self.run_host, daemon=True).start()

    def run_host(self):
        asyncio.run(self.host_async())

    async def host_async(self):
        async with websockets.connect(SERVER_URL) as ws:
            await ws.send(json.dumps({"type": "join"}))

            response = await ws.recv()
            data = json.loads(response)

            if data["type"] == "room_assigned":
                room = data["room"]
                self.update_room_label(f"Room: {room}")

    # -------------------------
    # JOIN
    # -------------------------
    def join(self):
        room_code = self.entry.get()
        threading.Thread(target=self.run_join, args=(room_code,), daemon=True).start()

    def run_join(self, room_code):
        asyncio.run(self.join_async(room_code))

    async def join_async(self, room_code):
        async with websockets.connect(SERVER_URL) as ws:
            await ws.send(json.dumps({
                "type": "join",
                "room": room_code
            }))

            response = await ws.recv()
            data = json.loads(response)

            if data["type"] == "room_assigned":
                self.update_room_label(f"Joined: {room_code}")

    # -------------------------
    # UI UPDATE SAFE
    # -------------------------
    def update_room_label(self, text):
        self.root.after(0, lambda: self.room_label.config(text=text))


def main():
    root = tk.Tk()
    app = App(root)
    root.mainloop()