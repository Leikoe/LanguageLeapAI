from os import getenv
from pathlib import Path
import whisper
from dotenv import load_dotenv

load_dotenv()

WHISPER_LOCAL_MODEL = getenv('WHISPER_LOCAL_MODEL', "small.en")
WHISPER_LOCAL = bool(getenv('WHISPER_LOCAL', False))
SAMPLE_JP_FILEPATH = Path(__file__).resolve(
).parent.parent / r'audio\samples\japanese_speech_sample.wav'
SAMPLE_EN_FILEPATH = Path(__file__).resolve(
).parent.parent / r'audio/samples/english_speech_sample.wav'

print(f"[WHISPER] loading up {WHISPER_LOCAL_MODEL} whisper model..")
whisper_model = whisper.load_model(WHISPER_LOCAL_MODEL)
whisper_model.transcribe(str(SAMPLE_EN_FILEPATH))
print(f"[WHISPER] successfully loaded! running on {whisper_model.device}")


def transcribe(filepath, language):
    return whisper_model.transcribe(filepath, language=language)

if __name__ == '__main__':
    # test if whisper is up and running
    print('Testing Whisper on English speech sample.')
    print(f'Actual audio: Oh. Honestly, I could not be bothered to play this game to full completion.'
          f'The narrator is obnoxious and unfunny, with his humor and dialogue proving to be more irritating than '
          f'entertaining.\nWhisper audio: {transcribe(SAMPLE_EN_FILEPATH)}\n')
