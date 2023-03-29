import statistics
import os as _os
import io as _io
import sys as _sys
import struct
import wave
from threading import Thread
import pvporcupine
from pvrecorder import PvRecorder
import pvcobra
import wave
import whisper
from scipy.io.wavfile import read
import numpy as _np


class Engine(Thread):
    """
    Microphone Demo for Porcupine wake word engine.
    It creates an input audio stream from a microphone, monitors it, and
    upon detecting the specified wake word(s) prints the detection time
    and wake word on console. It optionally saves
    the recorded audio into a file for further debugging.
    """
    def __init__(
        self,
        access_key,
        keywords,
        sensitivities,
        listen_queue=None,
        input_device_index=None,
    ):
        """
        Constructor.

        :param library_path: Absolute path to Porcupine's dynamic library.
        :param model_path: Absolute path to the file containing model parameters.
        :param keyword_paths: Absolute paths to keyword model files.
        :param sensitivities: Sensitivities for detecting keywords. Each value should be a number within [0, 1]. A
        higher sensitivity results in fewer misses at the cost of increasing the false alarm rate. If not set 0.5 will
        be used.
        :param input_device_index: Optional argument. If provided, audio is recorded from this input device. Otherwise,
        the default audio input device is used.
        """
        super(Engine, self).__init__()
        self.whisper = whisper.load_model("small.en")
        self._listen_queue = listen_queue
        self._cobra = pvcobra.create(access_key)
        self.MAX_RECORD_SECONDS = 5

        keyword_paths = [pvporcupine.KEYWORD_PATHS[x] for x in keywords]
        self.keywords = list()
        for x in keyword_paths:
            keyword_phrase_part = _os.path.basename(x).replace('.ppn', '').split('_')
            if len(keyword_phrase_part) > 6:
                self.keywords.append(' '.join(keyword_phrase_part[0:-6]))
            else:
                self.keywords.append(keyword_phrase_part[0])

        self.porcupine = pvporcupine.create(
            access_key = access_key,
            library_path = pvporcupine.LIBRARY_PATH,
            model_path = pvporcupine.MODEL_PATH,
            keyword_paths = keyword_paths,
            sensitivities = sensitivities
        )

        self.recorder = PvRecorder(
            device_index = input_device_index,
            frame_length = self.porcupine.frame_length
        )
        self.recorder.start()

        print('Using device:', self.recorder.selected_device)
        print(f'Listening for: {self.keywords}')


    def run(self):
        """
        Creates an input audio stream, instantiates an instance of Porcupine object, and monitors the audio stream for
        occurrences of the wake word(s). It prints the time of detection for each occurrence and the wake word.
        """
        while True:
            pcm = self.recorder.read()
            result = self.porcupine.process(pcm)
            if result >= 0:
                print('\nDetected:', self.keywords[result])
                audio = self.record_audio(self._cobra, self.recorder)
                self.recorder.stop()
                self._listen_queue.append(self.transcribe(audio))
                self.recorder.start()


    def record_audio(self, cobra, recorder):
        """
        Record audio and return as a BytesIO object
        """
        prob_voice = []
        started = False
        i=0

        byte_audio = _io.BytesIO(bytes())
        wav_file = wave.open(byte_audio, "w")
        wav_file.setparams((1, 2, 16000, 512, "NONE", "NONE"))

        while True and i <= self.MAX_RECORD_SECONDS * (16000 / 512):
            pcm = recorder.read()

            wav_file.writeframes(struct.pack("h" * len(pcm), *pcm))

            voice_probability = cobra.process(pcm)
            percentage = voice_probability * 100

            if voice_probability > 0.5: started = True
            prob_voice.append(voice_probability)

            bar_length = int((percentage / 10) * 3)
            empty_length = 30 - bar_length
            _sys.stdout.write(
                "\r[%3d]|%s%s|" % (
                percentage, '█' * bar_length, ' ' * empty_length
            ))
            _sys.stdout.flush()

            if started and len(prob_voice) >= 2 and statistics.mean(prob_voice[-2:]) <= 0.1:
                break

            i+=1

        print('\n')
        byte_audio.seek(0)
        audio_np = _np.array(read(byte_audio)[1], dtype=_np.float32) / 16000
        return audio_np

    def transcribe(self, audio):
        """
        Transcribe audio to test using whisper
        """
        result = self.whisper.transcribe(audio, fp16=False)
        print(f"\nUSER: {result['text'].strip()}\n")
        return result['text'].strip()
