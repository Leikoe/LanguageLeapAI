import wave
from os import getenv
from typing import Optional
from pynput import keyboard
from dotenv import load_dotenv
import logging
import pyaudio
import time

from modules.asr import transcribe
from modules.translation import translate
from modules.tts import speak

load_dotenv()

# LOGGING STUFF
logger = logging.getLogger(__name__)
logger.setLevel(getenv('LOG', logging.DEBUG))
# create console handler and set level to debug
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

# create formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# add formatter to ch
ch.setFormatter(formatter)

# add ch to logger
logger.addHandler(ch)

logger.info("loading")
# END LOGGING STUFF


TARGET_LANGUAGE_CODE = getenv('TARGET_LANGUAGE_CODE')
MIC_ID = int(getenv('MICROPHONE_ID'))
RECORD_KEY = getenv('MIC_RECORD_KEY')
MIC_AUDIO_PATH = r'audio/mic.wav'
CHUNK = 1024
FORMAT = pyaudio.paInt16

recording = False


def on_press_key(key):
    global recording
    try:
        if key.char == RECORD_KEY:
            recording = True
    except AttributeError:
        # logger.error(f"special key pressed: {key}")
        pass


def on_release_key(key):
    global recording
    try:
        if key.char == RECORD_KEY:
            recording = False
    except AttributeError:
        # logger.error(f"special key pressed: {key}")
        pass


if __name__ == '__main__':
    logger.info(f"now running, translating to {TARGET_LANGUAGE_CODE}")
    p = pyaudio.PyAudio()

    # get channels and sampling rate of mic
    mic_info = p.get_device_info_by_index(MIC_ID)
    MIC_CHANNELS = mic_info['maxInputChannels']
    print(f"MIC_CHANNELS: {MIC_CHANNELS}")
    MIC_SAMPLING_RATE = int(mic_info['defaultSampleRate'])
    print(f"MIC_SAMPLING_RATE: {MIC_SAMPLING_RATE}")

    frames = []
    recording_last = False
    stream: Optional[pyaudio.Stream] = None

    listener = keyboard.Listener(
        on_press=on_press_key,
        on_release=on_release_key,
    )
    listener.start()

    try:
        while True:
            if not recording_last and recording:
                logger.info("starting recording..")
                frames = []
                stream = p.open(format=FORMAT,
                                channels=MIC_CHANNELS,
                                rate=MIC_SAMPLING_RATE,
                                input=True,
                                frames_per_buffer=CHUNK,
                                input_device_index=MIC_ID)

            if recording and stream:
                data = stream.read(CHUNK)
                frames.append(data)

            if recording_last and not recording:
                logger.info("ending recording")
                start = time.time()
                if stream is not None:
                    stream.stop_stream()
                    stream.close()
                stream = None

                # if empty audio file
                if not frames:
                    logger.info("No audio file to transcribe detected.")
                    continue

                # write microphone audio to file
                wf = wave.open(MIC_AUDIO_PATH, 'wb')
                wf.setnchannels(MIC_CHANNELS)
                wf.setsampwidth(p.get_sample_size(FORMAT))
                wf.setframerate(MIC_SAMPLING_RATE)
                wf.writeframes(b''.join(frames))
                wf.close()
                logger.debug(f"wrote audio file to os | took {time.time() - start}")

                # transcribe (audio -> text)
                transcribed = transcribe(MIC_AUDIO_PATH)
                logger.debug(f"transcribe | took {time.time() - start}")
                from_code = transcribed["language"]
                speech = transcribed["text"]
                if speech:
                    logger.info(f'transcript: {speech}')
                    # translate (text -> text)
                    translated = translate(speech, from_code, TARGET_LANGUAGE_CODE)
                    logger.info(f"translation: {translated}")
                    logger.debug(f"translate | took {time.time() - start}")
                    # text to speech (text -> audio)
                    speak(translated, TARGET_LANGUAGE_CODE)
                    logger.debug(f"tts | took {time.time() - start}")

                else:
                    logger.error('No speech detected.')

            recording_last = recording
            if not recording:
                time.sleep(0.01)

    except KeyboardInterrupt:
        logger.info('Closing voice translator.')
