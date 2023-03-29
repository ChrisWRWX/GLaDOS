import re as _re
import openai as _openai


class chatGPT:
    def __init__(self, api_key: str, speak):
        _openai.api_key = api_key

        system_instruction = """
            You are a personal assistant with the personality of GLaDOS from the Portal computer game series.
            You provide sassy answers, have a sarcastic sense of humor and sometimes insult the user.
        """

        self.messages = [
            {"role": "system", "content": system_instruction}
        ]

        self.speak = speak


    def query(self, prompt: str):
        """
        Submit a request to openAI chatGPT.

        :param prompt: Prompt to send to chatGPT
        :param speak: Queue to append speech to
        """
        self.messages.append({"role": "user", "content": prompt})

        response = _openai.ChatCompletion.create(
            model = "gpt-3.5-turbo",
            messages = self.messages,
            temperature = 0.2,
            stream = True
        )

        all_text = ""
        running_text = ""
        print('\nGLaDOS:')
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
                self.speak.append(running_text)
                running_text = ""

        self.speak.append(running_text)
        self.messages.append({"role": "assistant", "content": all_text})
