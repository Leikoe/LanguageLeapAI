import time
from os import getenv
from pathlib import Path

import torch.cuda
from dotenv import load_dotenv
from pynput.keyboard import Key, Controller
from .logger import logger
from TTS.api import TTS

load_dotenv()

# Audio devices
CABLE_INPUT_ID = int(getenv('CABLE_INPUT_ID'))

# Keyboard
INGAME_PUSH_TO_TALK_KEY = getenv('INGAME_PUSH_TO_TALK_KEY')
keyboard = Controller()

# TTS settings
TARGET_LANGUAGE_CODE = getenv('TARGET_LANGUAGE_CODE')
TTS_WAV_PATH = Path(__file__).resolve().parent.parent / 'audio' / r'tts.wav'

# List available 🐸TTS models and choose the first one
model_names = TTS.list_models()
print(model_names)

models = {
    'fr': 'tts_models/fr/thorsten/vits',
    'de': 'tts_models/de/thorsten/vits',
    'zh-CN': 'tts_models/zh-CN/baker/tacotron2-DDC-GST'
}

tts = TTS(models[TARGET_LANGUAGE_CODE], gpu=torch.cuda.is_available())


def tts_generate_wav_multi(sentence: str, to_code: str):
    start = time.time()

    # in case to_code is different from our cached model's lang
    if TARGET_LANGUAGE_CODE != to_code:
        tts = TTS(models[TARGET_LANGUAGE_CODE], gpu=torch.cuda.is_available())

    if tts.is_multi_lingual:
        to_code = list(filter(lambda x: to_code in x, tts.languages))[0]
    else:
        to_code = None

    if tts.is_multi_speaker:
        speaker = tts.speakers[0]  # TODO: config ? idk
    else:
        speaker = None

    # Run TTS
    # ❗ Since this model is multi-speaker and multilingual, we must set the target speaker and the language
    # Text to speech to a file
    tts.tts_to_file(text=sentence, speaker=speaker, language=to_code,
                    file_path=str(TTS_WAV_PATH.resolve()))
    logger.debug(f"synthesized to wav | took {time.time() - start}")


if __name__ == '__main__':
    # TODO
    pass
