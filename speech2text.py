import pyaudio
import speech_recognition as sr

# Initialize recognizer
recognizer = sr.Recognizer()

# Initialize PyAudio
audio = pyaudio.PyAudio()

# Define the parameters for the audio stream
stream_params = {
    "format": pyaudio.paInt16,
    "channels": 1,
    "rate": 44100,
    "input": True,
    "frames_per_buffer": 1024
}

# Function to convert audio to text
def audio_to_text():
    with sr.Microphone(device_index=0) as source:
        print("Listening...")

        # Adjust for ambient noise
        recognizer.adjust_for_ambient_noise(source)

        # Record audio
        audio_data = recognizer.listen(source)

    try:
        print("Recognizing...")
        # Recognize speech using Google Speech Recognition
        text = recognizer.recognize_google(audio_data)
        print("You said: ", text)
    except sr.UnknownValueError:
        print("Sorry, could not understand audio.")
    except sr.RequestError as e:
        print("Could not request results from Google Speech Recognition service; {0}".format(e))

# Start capturing audio and converting to text
while True:
    audio_to_text()
