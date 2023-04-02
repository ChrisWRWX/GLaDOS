import asyncio
import websockets
from io import BytesIO
from openAI import (
    chatGPT as _chatGPT,
    whisper as _whisper
)
import re as _re
import glados
import os

connections = {}
conversations = {}

chatGPT = _chatGPT(api_key=os.environ['OPENAI_API_KEY'])
whisper = _whisper()

async def handler(websocket):

    connections[websocket.id] = websocket
    if websocket.id not in conversations:
        conversations[websocket.id] = []

    while True:
        try:
            message = await websocket.recv()
            
            if isinstance(message, str):
                prompt = message
            else:
                # transcribe audio
                audio = BytesIO(message)
                prompt = whisper.transcribe(audio)

            response = chatGPT.query(prompt, conversations[websocket.id])

            all_text = ""
            running_text = ""
            for chunk in response:
                text = chunk['choices'][0]['delta'].get('content', '')
                running_text = running_text + text
                all_text = all_text + text

                if (
                    '!' in running_text or
                    '?' in running_text or
                    ' - ' in running_text or
                    '.' in running_text or
                    _re.search(r'[a-zA-Z]{2,},', running_text)
                ):
                    temp = glados.tts(running_text)
                    await connections[websocket.id].send(temp.read())
                    await asyncio.sleep(0)
                    running_text = ""

            if running_text:
                await connections[websocket.id].send(running_text)
                await asyncio.sleep(0)

            if websocket.id not in conversations:
                conversations[websocket.id] = []

            conversations[websocket.id].append({"role": "user", "content": prompt})
            conversations[websocket.id].append({"role": "assistant", "content": all_text})

        except websockets.ConnectionClosedOK:
            break
        
        await asyncio.sleep(0)
        
    try:
        await websocket.wait_closed()
    finally:
        del connections[websocket.id]
        del conversations[websocket.id]


async def main():
    async with websockets.serve(handler, "0.0.0.0", 8001):
        await asyncio.Future()  # run forever


if __name__ == "__main__":
    asyncio.run(main())
