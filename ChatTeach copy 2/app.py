from flask import Flask, render_template, request
import pyaudio
import wave
import openai
from gtts import gTTS
from playsound import playsound
from google.cloud import speech
from google.cloud.speech import RecognitionAudio, RecognitionConfig


# Load Google credentials
client = speech.SpeechClient.from_service_account_file('key.json')
openai.api_key="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"

app = Flask(__name__)

# Set the audio parameters
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 1024
RECORD_SECONDS = 5
WAVE_OUTPUT_FILENAME = "output.wav"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/record', methods=['GET'])
def record():
    # Record audio
    audio = pyaudio.PyAudio()
    stream = audio.open(format=FORMAT, channels=CHANNELS,
                rate=RATE, input=True,
                frames_per_buffer=CHUNK)
    print("Recording...")
    frames = []
    for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        frames.append(data)
    print("Recording finished")
    # Stop recording
    stream.stop_stream()
    stream.close()
    audio.terminate()
    # Save the audio as a WAV file
    wf = wave.open("myrecording.wav", 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(audio.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()
    
    # Convert audio to text using Google Cloud Speech-to-Text API
    file_name = "output.wav"
    with open(file_name, 'rb') as f:
        mp3_data = f.read()

    audio_file = RecognitionAudio(content=mp3_data)

    config = RecognitionConfig(
        sample_rate_hertz=44100, 
        enable_automatic_punctuation=True,
        language_code='en-US'
    )

    response = client.recognize(
        config=config,
        audio=audio_file
    )

    # Use OpenAI to generate a response
    completion = openai.Completion.create(engine="text-davinci-003",prompt=(response.results[0].alternatives[0].transcript),max_tokens=1000)
    message=completion.choices[0]['text']
    # Convert response to speech and play it
    speech=gTTS(text=message)
    speech.save("tmp.mp3")
    playsound("tmp.mp3")

    return render_template('index.html', response=message)

if __name__ == '__main__':
    app.run(debug=True)
