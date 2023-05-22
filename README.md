# GLaDOS

An AI assistant with the voice and personality of [GLaDOS](https://en.wikipedia.org/wiki/GLaDOS) from the Portal computer game series.

## Installation

### Docker Compose
```yml
version: "3.9"
services:
  glados:
    container_name: GLaDOS
    image: ghcr.io/chriswrwx/glados:latest
    environment:
      OPENAI_API_KEY: ${OPENAI_API_KEY}
    ports:
      - 443:443
      - 80:80
    restart: unless-stopped
```

### OpenAI

https://platform.openai.com/account/

Used for chatGPT. Generate an API Key and provide as the environment variable `OPENAI_API_KEY`


## Credits
- [OpenAI-Whisper](https://pypi.org/project/openai-whisper/) for speech recognition.
- [chatGPT](https://chat.openai.com/) for conversation processing.
- [GLaDOS Text-to-speech (TTS) Voice Generator](https://github.com/R2D2FISH/glados-tts) for speech synthesis