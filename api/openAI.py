import openai as _openai
import whisper as _whisper
import numpy as _np
from scipy.io import wavfile as _wavfile
from scipy import signal as _signal


class chatGPT:
    def __init__(self, api_key: str):
        _openai.api_key = api_key

        system_instruction = """
            You are a personal assistant with the personality of GLaDOS from the Portal computer game series.
            You provide sassy answers, have a sarcastic sense of humor and sometimes insult the user.
        """

        self.messages = [
            {"role": "system", "content": system_instruction}
        ]

    def query(self, prompt: str, conversation: list):
        """
        Submit a request to openAI chatGPT.

        :param prompt: Prompt to send to chatGPT
        :param speak: Queue to append speech to
        """
        conversation = self.messages + conversation + [{"role": "user", "content": prompt}]

        response = _openai.ChatCompletion.create(
            model = "gpt-3.5-turbo",
            messages = conversation,
            temperature = 0.8,
            stream = True
        )

        return response


class whisper:
    def __init__(self):
        self.whisper = _whisper.load_model("small.en")

    def transcribe(self, audio):
        """
        Transcribe audio to text using whisper
        """
        new_rate = 16000
        # Read file
        sample_rate, clip = _wavfile.read(audio)
            
        # Resample data
        number_of_samples = round(len(clip) * float(new_rate) / sample_rate)
        clip = _signal.resample(clip, number_of_samples)

        audio_np = _np.array(clip, dtype=_np.float32) / 16000
        result = self.whisper.transcribe(audio_np, fp16=False)
        return result['text'].strip()
