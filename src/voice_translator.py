import wave
from os import getenv
from time import sleep

import deepl
import googletrans
import keyboard
import pyaudio
import requests
import time

# LOGGING STUFF
import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
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

from dotenv import load_dotenv

from modules.asr import transcribe
from modules.tts import speak

load_dotenv()

USE_DEEPL = getenv('USE_DEEPL', 'False').lower() in ('true', '1', 't')
if not USE_DEEPL:
    import argostranslate.package
    import argostranslate.translate

    from_code = "en"
    to_code = "ja"

    # Download and install Argos Translate package
    argostranslate.package.update_package_index()
    available_packages = argostranslate.package.get_available_packages()
    package_to_install = next(
        filter(
            lambda x: x.from_code == from_code and x.to_code == to_code, available_packages
        )
    )
    argostranslate.package.install_from_path(package_to_install.download())

DEEPL_AUTH_KEY = getenv('DEEPL_AUTH_KEY')
TARGET_LANGUAGE = getenv('TARGET_LANGUAGE_CODE')
MIC_ID = int(getenv('MICROPHONE_ID'))
RECORD_KEY = getenv('MIC_RECORD_KEY')
LOGGING = getenv('LOGGING', 'False').lower() in ('true', '1', 't')
MIC_AUDIO_PATH = r'audio/mic.wav'
CHUNK = 1024
FORMAT = pyaudio.paInt16


def on_press_key(_):
    global frames, recording, stream
    if not recording:
        logger.debug("starting recording..")
        frames = []
        recording = True
        stream = p.open(format=FORMAT,
                        channels=MIC_CHANNELS,
                        rate=MIC_SAMPLING_RATE,
                        input=True,
                        frames_per_buffer=CHUNK,
                        input_device_index=MIC_ID)


def on_release_key(_):
    logger.debug("ending recording")
    start = time.time()
    global recording, stream
    recording = False
    stream.stop_stream()
    stream.close()
    stream = None

    # if empty audio file
    if not frames:
        logger.info("No audio file to transcribe detected.")
        return

    # write microphone audio to file
    wf = wave.open(MIC_AUDIO_PATH, 'wb')
    wf.setnchannels(MIC_CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(MIC_SAMPLING_RATE)
    wf.writeframes(b''.join(frames))
    wf.close()
    logger.debug(f"wrote audio file to os | took {time.time() - start}")

    # transcribe audio
    try:
        eng_speech = transcribe(MIC_AUDIO_PATH)
        logger.debug(f"[DEBUG] transcribed | took {time.time() - start}")
    except requests.exceptions.JSONDecodeError:
        logger.error('Too many requests to process at once')
        return

    if eng_speech:

        if USE_DEEPL:
            jp_speech = translator.translate_text(
                eng_speech, target_lang=TARGET_LANGUAGE)
        else:
            # jp_speech = translator.translate(
            #     eng_speech, dest=TARGET_LANGUAGE).text
            jp_speech = argostranslate.translate.translate(eng_speech, from_code, to_code)

        if LOGGING:
            logger.info(f'English: {eng_speech}')
            logger.info(f'Japanese: {jp_speech}')

        logger.debug(f"translated | took {time.time() - start}")

        # speak(jp_speech, TARGET_LANGUAGE)

    else:
        logger.error('No speech detected.')


if __name__ == '__main__':
    logger.info("now running")
    p = pyaudio.PyAudio()

    # get channels and sampling rate of mic
    mic_info = p.get_device_info_by_index(MIC_ID)
    MIC_CHANNELS = mic_info['maxInputChannels']
    MIC_SAMPLING_RATE = int(mic_info['defaultSampleRate'])

    frames = []
    recording = False
    stream = None

    # Set DeepL or Google Translator
    if USE_DEEPL:
        translator = deepl.Translator(DEEPL_AUTH_KEY)
    else:
        translator = googletrans.Translator()

    keyboard.on_press_key(RECORD_KEY, on_press_key)
    keyboard.on_release_key(RECORD_KEY, on_release_key)

    try:
        while True:
            if recording and stream:
                data = stream.read(CHUNK)
                frames.append(data)
            else:
                sleep(0.5)

    except KeyboardInterrupt:
        logger.info('Closing voice translator.')
