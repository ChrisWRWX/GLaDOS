# GLaDOS

## Installation

- Clone this repository
- pip install -r requirements.txt
- Install [eSpeak](https://github.com/espeak-ng/espeak-ng/releases)

### OpenAI

https://platform.openai.com/account/

Used for chatGPT.

Generate an API Key and save as the environment variable `OPENAI_API_KEY`

### Picovoice
https://console.picovoice.ai/

Used for wake word detection.

Generate an API Key and save as the environment variable `PICOVOICE_API_KEY`

## Usage

- Run `app.py`
- GLaDOS is triggered with the wake word `computer`.
- Ask whatever you like.
- Follow ups are added to the same conversation.

## Credits

- GLaDOS Text-to-speech (TTS) Voice Generator: https://github.com/R2D2FISH/glados-tts
