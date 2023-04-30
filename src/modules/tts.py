from os import getenv
from pathlib import Path
from dotenv import load_dotenv
import soundfile as sf
import sounddevice as sd
from pynput.keyboard import Controller
from .logger import logger

load_dotenv()

# only import voicevox's speak function when translating to japanese
TARGET_LANGUAGE_CODE = getenv('TARGET_LANGUAGE_CODE')
if TARGET_LANGUAGE_CODE == 'ja':
    from .portable_voicevox import tts_generate_wav_jp
else:
    from .tts_multi import tts_generate_wav_multi as speak_multi

TTS_WAV_PATH = Path(__file__).resolve(
).parent.parent / 'audio' / r'tts.wav'

# Keyboard
INGAME_PUSH_TO_TALK_KEY = getenv('INGAME_PUSH_TO_TALK_KEY')
keyboard = Controller()

# Audio devices
CABLE_INPUT_ID = int(getenv('CABLE_INPUT_ID'))


def play_voice(device_id):
    data, fs = sf.read(TTS_WAV_PATH, dtype='float32')

    if INGAME_PUSH_TO_TALK_KEY:
        keyboard.press(INGAME_PUSH_TO_TALK_KEY)

    logger.info("speaking now..")
    sd.play(data, fs, device=device_id, blocking=True)
    # sd.wait()
    logger.info("finished speaking")

    if INGAME_PUSH_TO_TALK_KEY:
        keyboard.release(INGAME_PUSH_TO_TALK_KEY)


# Text-to-Speech, feel free to add your own function or add more languages
def speak(sentence, language_code):
    # Japanese
    if language_code == 'ja':
        tts_generate_wav_jp(sentence)
        pass

    else:
        speak_multi(sentence, language_code)
        pass

    # elif language_code == 'en':
    #     speak_multi(sentence, language_code)
    #     pass
    #
    # # French
    # elif language_code == 'ko':
    #     # Write your own function to play your TTS audio
    #     pass
    #
    # # Chinese
    # elif language_code == 'zh':
    #     pass
    #
    # # French
    # elif language_code == 'fr':
    #     pass
    #
    # # Spanish
    # elif language_code == 'es':
    #     pass
    #
    # # Russian
    # elif language_code == 'ru':
    #     pass
    #
    # # German
    # elif language_code == 'de':
    #     pass

    play_voice(CABLE_INPUT_ID)
