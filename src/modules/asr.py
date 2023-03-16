from os import getenv
from pathlib import Path

import requests
import whisper
from dotenv import load_dotenv

load_dotenv()

BASE_URL = getenv('WHISPER_BASE_URL')
WHISPER_LOCAL_MODEL = getenv('WHISPER_LOCAL_MODEL', "small.en")
WHISPER_LOCAL = bool(getenv('WHISPER_LOCAL', False))
REQUEST_TIMEOUT = int(getenv('REQUEST_TIMEOUT'))
SAMPLE_JP_FILEPATH = Path(__file__).resolve(
).parent.parent / r'audio\samples\japanese_speech_sample.wav'
SAMPLE_EN_FILEPATH = Path(__file__).resolve(
).parent.parent / r'audio\samples\english_speech_sample.wav'

if WHISPER_LOCAL:
    print(f"[WHISPER] loading up {WHISPER_LOCAL_MODEL} whisper model..")
    whisper_model = whisper.load_model(WHISPER_LOCAL_MODEL)
    whisper_model.transcribe(str(SAMPLE_EN_FILEPATH))
    print(f"[WHISPER] successfully loaded! running on {whisper_model.device}")


def transcribe(filepath):
    if WHISPER_LOCAL:
        return whisper_model.transcribe(filepath)["text"]
    try:
        with open(filepath, 'rb') as infile:
            files = {'audio_file': infile}
            r = requests.post(
                f'{BASE_URL}/asr?task=transcribe&language=en&output=json', files=files)

    except requests.exceptions.Timeout:
        print('Request timeout')
        return None

    except requests.exceptions.ConnectionError:
        print('Unable to reach Whisper, ensure that it is running, or the WHISPER_BASE_URL variable is set correctly')
        return None

    return r.json()['text'].strip()


def translate(filepath, language):
    try:
        with open(filepath, 'rb') as infile:
            files = {'audio_file': infile}
            r = requests.post(f'{BASE_URL}/asr?task=translate&language={language}&output=json',
                              files=files,
                              timeout=REQUEST_TIMEOUT)
    except requests.exceptions.Timeout:
        print('Request timeout')
        return None

    except requests.exceptions.ConnectionError:
        print('Unable to reach Whisper, ensure that it is running, or the WHISPER_BASE_URL variable is set correctly')
        return None

    translation = r.json()['text'].strip()

    # remove most hallucinations
    if translation.lower().startswith('thank you for'):
        return None

    return translation


if __name__ == '__main__':
    # test if whisper is up and running
    print('Testing Whisper on English speech sample.')
    print(f'Actual audio: Oh. Honestly, I could not be bothered to play this game to full completion.'
          f'The narrator is obnoxious and unfunny, with his humor and dialogue proving to be more irritating than '
          f'entertaining.\nWhisper audio: {transcribe(SAMPLE_EN_FILEPATH)}\n')

    print('Testing Whisper on Japanese speech sample.')
    print(f'Actual translation: How is this dress? It suits you very well.\n'
          f"Whisper translation: {translate(SAMPLE_JP_FILEPATH, 'ja')}")
