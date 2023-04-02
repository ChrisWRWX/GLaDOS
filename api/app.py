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
import logging
import json
import time

logging.getLogger().setLevel(logging.INFO)

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
            
            start_time = time.time()
            if isinstance(message, str):
                prompt = message
            else:
                # transcribe audio
                audio = BytesIO(message)
                prompt = whisper.transcribe(audio)
            
            logging.info(json.dumps({
                "id": str(websocket.id),
                "time": str(round((time.time() - start_time) * 1000, 0)) + "ms",
                "prompt": prompt
            }))

            start_time = time.time()
            response = chatGPT.query(prompt, conversations[websocket.id])
            logging.info(f'chatGPT response - {str(round((time.time() - start_time) * 1000, 0))}ms')
            
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
                    '.' in running_text
                ):
                    start_time = time.time()
                    temp = glados.tts(running_text.strip())
                    logging.info(json.dumps({
                        "id": str(websocket.id),
                        "time": str(round((time.time() - start_time) * 1000, 0)) + "ms",
                        "response": running_text.strip()
                    }))
                    await connections[websocket.id].send(temp.read())
                    await asyncio.sleep(0)
                    running_text = ""

            if running_text.strip():
                start_time = time.time()
                temp = glados.tts(running_text.strip())
                logging.info(json.dumps({
                    "id": str(websocket.id),
                    "time": str(round((time.time() - start_time) * 1000, 0)) + "ms",
                    "response": running_text.strip()
                }))
                await connections[websocket.id].send(temp.read())
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
