import os, json
import pyttsx3, pyaudio, requests
from vosk import Model, KaldiRecognizer
import webbrowser

engine = pyttsx3.init()

def speak(text):
    engine.say(text)
    engine.runAndWait()

model_path =  "C:/Users/Admin/OneDrive/Desktop/vosk-model-en-us-0.22"
if not os.path.exists(model_path):
    print("Please download the model from https://alphacephei.com/vosk/models and unpack as 'model' in the current folder.")
    exit(1)
model = Model(model_path)

recognizer = KaldiRecognizer(model, 16000)

p = pyaudio.PyAudio()
stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=8192)
stream.start_stream()


def listen():
    while True:
        data = stream.read(4096, exception_on_overflow=False)
        if recognizer.AcceptWaveform(data):
            result = json.loads(recognizer.Result())
            return result['text']


def handle_api_request(word):
    response = requests.get(f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}")
    if response.status_code == 200:
        return response.json()
    else:
        speak("Failed to fetch data from the dictionary API.")
        return None

 
def find_word(word):
    data = handle_api_request(word)
    if data:
        meanings = data[0].get('meanings', [])
        if meanings:
            definitions = meanings[0].get('definitions', [])
            if definitions:
                speak(f"The definition of {word} is: {definitions[0]['definition']}")
                if 'example' in definitions[0]:
                    speak(f"An example of usage: {definitions[0]['example']}")
            else:
                speak("No definitions found.")
        else:
            speak("No meanings found.")

def show_link(word):
    url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}"
    webbrowser.open(url)
    speak(f"Opening browser for the word {word}.")


def process_command(command):
    words = command.split()
    if len(words) > 1:
        action = words[0]
        word = ' '.join(words[1:])
        if action == "find":
            find_word(word)
        elif action == "link":
            show_link(word)
        else:
            speak("Command not recognized.")
    else:
        speak("Please specify a word after the command.")

while True:
    print("Listening for command...")
    command = listen()
    print(f"Command received: {command}")
    process_command(command)