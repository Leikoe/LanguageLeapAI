import time
from os import getenv
from pathlib import Path
from dotenv import load_dotenv
from pynput.keyboard import Key, Controller
from .logger import logger
from voicevox_core import AccelerationMode, AudioQuery, VoicevoxCore

load_dotenv()


# Voicevox settings
OPEN_JTALK_DICT_DIR = getenv('OPEN_JTALK_DICT_DIR')
VOICE_ID = int(getenv('VOICE_ID'))
TTS_WAV_PATH = Path(__file__).resolve(
).parent.parent / 'audio' / r'tts.wav'

print(f"[VOICEVOX] loading up voicevox core..")
core = VoicevoxCore(
    acceleration_mode="CPU", open_jtalk_dict_dir=OPEN_JTALK_DICT_DIR
)
core.load_model(VOICE_ID)
print(f"[VOICEVOX] successfully loaded! running on {'gpu' if core.is_gpu_mode else 'cpu'}")


def tts_generate_wav_jp(sentence: str):
    start = time.time()

    logger.debug("querying voicevox")
    audio_query = core.audio_query(sentence, VOICE_ID)
    audio_query.output_stereo = True
    logger.debug(f"querying took: {time.time() - start}")

    logger.debug("synthesis starting")
    wav = core.synthesis(audio_query, VOICE_ID)
    logger.debug(f"synthesis took: {time.time() - start}")

    TTS_WAV_PATH.write_bytes(wav)
    logger.debug(f"wrote to wav file took: {time.time() - start}")


if __name__ == '__main__':
    # test if voicevox is up and running
    print('Voicevox attempting to speak now...')
    tts_generate_wav_jp('むかしあるところに、ジャックという男の子がいました。ジャックはお母さんと一緒に住んでいました。')
