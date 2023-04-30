from os import getenv
from pathlib import Path
import torch.cuda
from faster_whisper import WhisperModel
from dotenv import load_dotenv


load_dotenv()

WHISPER_MODEL = getenv('WHISPER_MODEL', "small.en")
SAMPLE_JP_FILEPATH = Path(__file__).resolve(
).parent.parent / r'audio' / 'samples' / 'japanese_speech_sample.wav'
SAMPLE_EN_FILEPATH = Path(__file__).resolve(
).parent.parent / 'audio' / 'samples' / 'english_speech_sample.wav'

print(f"[WHISPER] loading up {WHISPER_MODEL} whisper model..")
model = WhisperModel(WHISPER_MODEL, device="cuda" if torch.cuda.is_available() else "cpu", compute_type="int8")
print(f"[WHISPER] successfully loaded! running on {model.model.device}")


def transcribe(filepath):
    segments, info = model.transcribe(filepath)
    # segments = list(segments)
    return {"text": "".join(map(lambda x: x.text, segments)), "language": info.language}


if __name__ == '__main__':
    # test if whisper is up and running
    print('Testing Whisper on English speech sample.')
    print(f'Actual audio: Oh. Honestly, I could not be bothered to play this game to full completion.'
          f'The narrator is obnoxious and unfunny, with his humor and dialogue proving to be more irritating than '
          f'entertaining.\nWhisper audio: {transcribe(str(SAMPLE_EN_FILEPATH.resolve()))}\n')
