"""
Main App
"""
from threading import Thread
from time import sleep
from collections import deque
import os as _os
import porcupine
import glados
from openAI import chatGPT


def thread_listen(listen: deque):
    """
    Use Porcupine and Whisper to listen for wake word and parse the input
    
    Anything detected is added to the listen queue
    """
    porcupine.Engine(
        access_key = _os.environ["PICOVOICE_API_KEY"],
        keywords = ['computer', 'jarvis'],
        sensitivities = [0.6, 0.6],
        input_device_index = -1,
        listen_queue = listen
    ).run()


def thread_tts(tts: deque, speak: deque):
    """
    Convert text to speech and append to queue
    """
    while True:
        if tts:
            text = tts.popleft()
            if text.strip():
                speak.append((glados.tts(text.strip()), text.strip()))
        sleep(0.1)


def thread_speak(speak: deque):
    """
    Play audio files
    """
    while True:
        if speak:
            audio, text = speak.popleft()
            if audio:
                glados.speak(audio, text)
        sleep(0.1)


def thread_think(listen: deque, speak: deque):
    """
    Send input to chatGPT to respond to
    """
    _chatGPT = chatGPT(
        api_key = _os.environ["OPENAI_API_KEY"],
        speak = speak
    )
    while True:
        if listen:
            _chatGPT.query(listen.popleft())
        sleep(0.1)


if __name__ == '__main__':
    q_listen = deque()
    q_tts = deque()
    q_speak = deque()

    threads = []

    threads.append(Thread(target=thread_listen, args=(q_listen,), name='Thread-Listen'))
    threads.append(Thread(target=thread_think, args=(q_listen, q_tts), name='Thread-Think'))
    threads.append(Thread(target=thread_tts, args=(q_tts, q_speak), name='Thread-TTS'))
    threads.append(Thread(target=thread_speak, args=(q_speak,), name='Thread-Speak'))

    for thread in threads:
        thread.start()
