import io
import torch
from scipy.io import wavfile as _wavfile
from utils.tools import prepare_text
import logging

logging.getLogger().setLevel(logging.INFO)

try:
    import winsounds
    import os
    os.environ['PHONEMIZER_ESPEAK_LIBRARY'] = 'C:\Program Files\eSpeak NG\libespeak-ng.dll'
    os.environ['PHONEMIZER_ESPEAK_PATH'] = 'C:\Program Files\eSpeak NG\espeak-ng.exe'
except ImportError:
    from subprocess import call

logging.info("Initializing TTS Engine...")

# Load models
glados = torch.jit.load('models/glados.pt')
vocoder = torch.jit.load('models/vocoder-cpu-hq.pt', map_location='cpu')

logging.info("Loading voice models")
# Prepare models in RAM
for i in range(2):
    init = glados.generate_jit(prepare_text(str(i)))
    init_mel = init['mel_post'].to('cpu')
    init_vo = vocoder(init_mel)
logging.info("Voice models loaded")


def tts(text):
    """
    Convert text to speech
    """
    # Fix pronunciation
    text = text.replace('GLaDOS', 'Glados')

    # Tokenize, clean and phonemize input text
    x = prepare_text(text).to('cpu')

    with torch.no_grad():
        # Generate generic TTS-output
        tts_output = glados.generate_jit(x)

        # Use HiFiGAN as vocoder to make output sound like GLaDOS
        mel = tts_output['mel_post'].to('cpu')
        audio = vocoder(mel)
        
        # Normalize audio to fit in wav-file
        audio = audio.squeeze()
        audio = audio * 32768.0
        audio = audio.cpu().numpy().astype('int16')

        # Write audio to memory file
        # 22,05 kHz sample rate
        byte_io = io.BytesIO(bytes())
        _wavfile.write(byte_io, 22050, audio)
        
        return byte_io
