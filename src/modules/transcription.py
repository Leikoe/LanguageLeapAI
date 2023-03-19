from os import getenv
from pathlib import Path
import whisper
from dotenv import load_dotenv

load_dotenv()

WHISPER_MODEL = getenv('WHISPER_MODEL', "small.en")
SAMPLE_JP_FILEPATH = Path(__file__).resolve(
).parent.parent / r'audio' / 'samples' / 'japanese_speech_sample.wav'
SAMPLE_EN_FILEPATH = Path(__file__).resolve(
).parent.parent / 'audio' / 'samples' / 'english_speech_sample.wav'

print(f"[WHISPER] loading up {WHISPER_MODEL} whisper model..")
whisper_model = whisper.load_model(WHISPER_MODEL)
whisper_model.transcribe(str(SAMPLE_EN_FILEPATH.resolve()), fp16=False if whisper_model.device == 'cpu' else None)
print(f"[WHISPER] successfully loaded! running on {whisper_model.device}")


def transcribe(filepath):
    return whisper_model.transcribe(filepath, fp16=False if whisper_model.device == 'cpu' else None)


if __name__ == '__main__':
    # test if whisper is up and running
    print('Testing Whisper on English speech sample.')
    print(f'Actual audio: Oh. Honestly, I could not be bothered to play this game to full completion.'
          f'The narrator is obnoxious and unfunny, with his humor and dialogue proving to be more irritating than '
          f'entertaining.\nWhisper audio: {transcribe(str(SAMPLE_EN_FILEPATH.resolve()))}\n')
