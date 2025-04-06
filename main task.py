import json
import time
import requests
import pyttsx3
import vosk
import os
import pyaudio

MODEL_PATH = "C:/Users/Admin/OneDrive/Desktop/vosk-model-en-us-0.22"

p = pyaudio.PyAudio()
info = p.get_default_input_device_info()

print("Default Input Device:", info["name"])
print("Sample Rate:", info["defaultSampleRate"])
print("Max Input Channels:", info["maxInputChannels"])
print("Loading model from:", MODEL_PATH)


class Recognize:
    def __init__(self):
        model = vosk.Model(MODEL_PATH)
        self.record = vosk.KaldiRecognizer(model, 16000)
        self.stream_audio()

    def stream_audio(self):
        pa = pyaudio.PyAudio()
        self.stream = pa.open(format=pyaudio.paInt16,
                              channels=1,
                              rate=16000,
                              input=True,
                              frames_per_buffer=8000)

    def listen(self):
        while True:
            data = self.stream.read(4000, exception_on_overflow=False)
            if self.record.AcceptWaveform(data) and len(data) > 0:
                result = json.loads(self.record.Result())
                if 'text' in result and result['text']:
                    yield result['text']


class Speech:
    def __init__(self):
        self.tts = pyttsx3.init()

    def set_voice(self, speaker=0):
        voices = self.tts.getProperty('voices')
        if speaker < len(voices):
            self.tts.setProperty('voice', voices[speaker].id)

    def text2voice(self, text='Ready', speaker=0):
        self.set_voice(speaker)
        self.tts.say(text)
        self.tts.runAndWait()


def get_weather():
    try:
        response = requests.get("https://wttr.in/Saint-Petersburg?format=%t")
        if response.status_code == 200:
            return response.text.strip()
        else:
            return "Error fetching weather."
    except requests.exceptions.RequestException:
        return "Network error."

def get_wind_speed():
    try:
        response = requests.get("https://wttr.in/Saint-Petersburg?format=%w")
        if response.status_code == 200:
            return response.text.strip()
        else:
            return "Error fetching wind speed."
    except requests.exceptions.RequestException:
        return "Network error."


def should_walk():
    temp = get_weather()
    wind = get_wind_speed()
    try:
        temp_value = int(temp.replace("+", "").replace("°C", "").strip())
        wind_speed = int(wind.replace("km/h", "").strip())
        if temp_value < 5 or wind_speed > 15:
            return "Not recommended to walk."
        else:
            return "It is fine to walk."
    except ValueError:
        return "Could not determine if walking is advisable."


def process_command(command):
    command = command.lower().strip()
    if "weather" in command:
        return f"The current temperature is {get_weather()}"
    elif "wind" in command:
        return f"The wind speed is {get_wind_speed()}"
    elif "direction" in command:
        return "I cannot provide directions yet."
    elif "walk" in command:
        return should_walk()
    else:
        return "Command not recognized."


rec = Recognize()
speech = Speech()
speech.text2voice("Starting assistant")
time.sleep(0.5)

for text in rec.listen():
    print("User said:", text)  
    if text.lower() == "exit":
        speech.text2voice("Goodbye!")
        break
    else:
        response = process_command(text)
        print("Assistant:", response)
        speech.text2voice(response)
