# ============================================================
# Modified Voicevox Text to Speech Plugin for Whispering Tiger
# V1.0.3
# See https://github.com/Sharrnah/whispering
# ============================================================

import sys
from importlib import util

import os

import numpy as np

from .downloader import download_thread
import tarfile
import zipfile
import shutil

import time
from os import getenv
from pathlib import Path
from dotenv import load_dotenv
from .logger import logger

import platform

OS = platform.system()
ARCH = platform.machine()

load_dotenv()

# Voicevox settings
VOICE_ID = int(getenv('VOICE_ID'))
TTS_WAV_PATH = Path(__file__).resolve(
).parent.parent / 'audio' / r'tts.wav'
VOICEVOX_ACCELERATION_MODE = getenv("VOICEVOX_ACCELERATION_MODE", "CPU")


def load_module(package_dir):
    package_dir = os.path.abspath(package_dir)
    package_name = os.path.basename(package_dir)

    # Add the parent directory of the package to sys.path
    parent_dir = os.path.dirname(package_dir)
    sys.path.insert(0, parent_dir)

    # Load the package
    spec = util.find_spec(package_name)
    if spec is None:
        raise ImportError(f"Cannot find package '{package_name}'")

    module = util.module_from_spec(spec)
    spec.loader.exec_module(module)

    # Remove the parent directory from sys.path
    sys.path.pop(0)

    return module


def extract_tar_gz(file_path, output_dir):
    with tarfile.open(file_path, "r:gz") as tar_file:
        tar_file.extractall(path=output_dir)
    # remove the zip file after extraction
    os.remove(file_path)


def extract_zip(file_path, output_dir):
    with zipfile.ZipFile(file_path, "r") as zip_file:
        zip_file.extractall(path=output_dir)
    # remove the zip file after extraction
    os.remove(file_path)


def move_files(source_dir, target_dir):
    for file_name in os.listdir(source_dir):
        source_path = os.path.join(source_dir, file_name)
        target_path = os.path.join(target_dir, file_name)

        # Check if it's a file
        if os.path.isfile(source_path):
            shutil.move(source_path, target_path)


voicevox_plugin_dir = Path(Path.cwd() / "Plugins" / "voicevox_plugin")
os.makedirs(voicevox_plugin_dir, exist_ok=True)

voicevox_core_python_repository = {
    "Windows": {
        "AMD64": {
            "CPU": {
                "url": "https://github.com/VOICEVOX/voicevox_core/releases/download/0.14.3/voicevox_core-0.14.3+cpu-cp38-abi3-win_amd64.whl",
                "sha256": "02a3d7359cf4f6c86cc66f5fecf262a7c529ef27bc130063f05facba43bf4006"
            },
            "CUDA": {
                "url": "https://github.com/VOICEVOX/voicevox_core/releases/download/0.14.3/voicevox_core-0.14.3+cuda-cp38-abi3-win_amd64.whl",
                "sha256": "ba987ea728a5fbbea50430737f042924c506849e6e337f95c99895dfc342082e"
            },
            "DIRECTML": {
                "url": "https://github.com/VOICEVOX/voicevox_core/releases/download/0.14.3/voicevox_core-0.14.3+directml-cp38-abi3-win_amd64.whl",
                "sha256": "bf0ac3ad7f1088470e0353ef919d0019eeefc3cf47363d8b293ccf0b3d1732d8"
            }
        }
    },
    "Linux": {
        "AMD64": {
            "CPU": {
                "url": "https://github.com/VOICEVOX/voicevox_core/releases/download/0.14.3/voicevox_core-0.14.3+cpu-cp38-abi3-linux_x86_64.whl",
                "sha256": "02a3d7359cf4f6c86cc66f5fecf262a7c529ef27bc130063f05facba43bf4006"
            },
            "CUDA": {
                "url": "https://github.com/VOICEVOX/voicevox_core/releases/download/0.14.3/voicevox_core-0.14.3+cuda-cp38-abi3-linux_x86_64.whl",
                "sha256": "ba987ea728a5fbbea50430737f042924c506849e6e337f95c99895dfc342082e"
            }
        },
        "arm64": {
            "CPU": {
                "url": "https://github.com/VOICEVOX/voicevox_core/releases/download/0.14.3/voicevox_core-0.14.3+cpu-cp38-abi3-linux_aarch64.whl",
                "sha256": "02a3d7359cf4f6c86cc66f5fecf262a7c529ef27bc130063f05facba43bf4006"
            }
        }
    },
    "Darwin": {
        "AMD64": {
            "CPU": {
                "url": "https://github.com/VOICEVOX/voicevox_core/releases/download/0.14.3/voicevox_core-0.14.3+cpu-cp38-abi3-macosx_10_7_x86_64.whl",
                "sha256": "02a3d7359cf4f6c86cc66f5fecf262a7c529ef27bc130063f05facba43bf4006"
            }
        },
        "arm64": {
            "CPU": {
                "url": "https://github.com/VOICEVOX/voicevox_core/releases/download/0.14.3/voicevox_core-0.14.3+cpu-cp38-abi3-macosx_11_0_arm64.whl",
                "sha256": "dd5ba2f7be8bad6cf6d0b151e4abb6e82e4dd50a972829a1a554f72c2c83fb73"
            }
        }
    },

}

voicevox_core_dll_repository = {
    "Windows": {
        "AMD64": {
            "CPU": {
                "url": "https://github.com/VOICEVOX/voicevox_core/releases/download/0.14.3/voicevox_core-windows-x64-cpu-0.14.3.zip",
                "sha256": "cf643566b08eb355e00b9b185d25f9f681944074f3ba1d9ae32bc04b98c3df50",
                "path": "voicevox_core-windows-x64-cpu-0.14.3"
            },
            "CUDA": {
                "url": "https://github.com/VOICEVOX/voicevox_core/releases/download/0.14.3/voicevox_core-windows-x64-cuda-0.14.3.zip",
                "sha256": "0ecb724e23820c477372584a4c732af1c01bcb49b451c4ad21fb810baafb20ca",
                "path": "voicevox_core-windows-x64-cuda-0.14.3"
            },
            "DIRECTML": {
                "url": "https://github.com/VOICEVOX/voicevox_core/releases/download/0.14.3/voicevox_core-windows-x64-directml-0.14.3.zip",
                "sha256": "a529b26f6ae7c258cff42671955c1ac4c44080137a4090ee6c977557cc648839",
                "path": "voicevox_core-windows-x64-directml-0.14.3"

            },
        }

    },
    "Linux": {
        "AMD64": {
            "CPU": {
                "url": "https://github.com/VOICEVOX/voicevox_core/releases/download/0.14.3/voicevox_core-linux-x64-cpu-0.14.3.zip",
                "sha256": "cf643566b08eb355e00b9b185d25f9f681944074f3ba1d9ae32bc04b98c3df50",
                "path": "voicevox_core-linux-x64-cpu-0.14.3"
            },
            "CUDA": {
                "url": "https://github.com/VOICEVOX/voicevox_core/releases/download/0.14.3/voicevox_core-linux-x64-gpu-0.14.3.zip",
                "sha256": "0ecb724e23820c477372584a4c732af1c01bcb49b451c4ad21fb810baafb20ca",
                "path": "voicevox_core-linux-x64-gpu-0.14.3"
            }
        },
        "arm64": {
            "CPU": {
                "url": "https://github.com/VOICEVOX/voicevox_core/releases/download/0.14.3/voicevox_core-linux-arm64-cpu-0.14.3.zip",
                "sha256": "cf643566b08eb355e00b9b185d25f9f681944074f3ba1d9ae32bc04b98c3df50",
                "path": "voicevox_core-linux-arm64-cpu-0.14.3"
            }
        },
    },
    "Darwin": {
        "AMD64": {
            "CPU": {
                "url": "https://github.com/VOICEVOX/voicevox_core/releases/download/0.14.3/voicevox_core-osx-x64-cpu-0.14.3.zip",
                "sha256": "cf643566b08eb355e00b9b185d25f9f681944074f3ba1d9ae32bc04b98c3df50",
                "path": "voicevox_core-osx-x64-cpu-0.14.3"
            }
        },
        "arm64": {
            "CPU": {
                "url": "https://github.com/VOICEVOX/voicevox_core/releases/download/0.14.3/voicevox_core-osx-arm64-cpu-0.14.3.zip",
                "sha256": "9dad5f357d5607837f8d235b8a3b4b31aefcb8d182737d7f655031d708a2ed7a",
                "path": "voicevox_core-osx-arm64-cpu-0.14.3"
            }
        }
    },
}

open_jtalk_dict_file = {
    "url": "https://jaist.dl.sourceforge.net/project/open-jtalk/Dictionary/open_jtalk_dic-1.11/open_jtalk_dic_utf_8-1.11.tar.gz",
    "sha256": "33e9cd251bc41aa2bd7ca36f57abbf61eae3543ca25ca892ae345e394cb10549",
    "path": "open_jtalk_dic_utf_8-1.11"
}

core = None
acceleration_mode = VOICEVOX_ACCELERATION_MODE
voicevox_core_module = None

os.makedirs(Path(voicevox_plugin_dir / acceleration_mode), exist_ok=True)

if not Path(voicevox_plugin_dir / acceleration_mode / "voicevox_core" / "__init__.py").is_file():
    download_thread(voicevox_core_python_repository[OS][ARCH][acceleration_mode]["url"],
                               str(Path(voicevox_plugin_dir / acceleration_mode).resolve()),
                               voicevox_core_python_repository[OS][ARCH][acceleration_mode]["sha256"])
    extract_zip(str(Path(voicevox_plugin_dir / acceleration_mode / os.path.basename(
        voicevox_core_python_repository[OS][ARCH][acceleration_mode]["url"])).resolve()),
                str(Path(voicevox_plugin_dir / acceleration_mode).resolve()))

# if not Path(voicevox_plugin_dir / acceleration_mode / "voicevox_core" / "voicevox_core.lib").is_file():
    download_thread(voicevox_core_dll_repository[OS][ARCH][acceleration_mode]["url"],
                               str(Path(voicevox_plugin_dir / acceleration_mode).resolve()),
                               voicevox_core_dll_repository[OS][ARCH][acceleration_mode]["sha256"])
    extract_zip(str(Path(voicevox_plugin_dir / acceleration_mode / os.path.basename(
        voicevox_core_dll_repository[OS][ARCH][acceleration_mode]["url"]))),
                str(Path(voicevox_plugin_dir / acceleration_mode).resolve()))
    # move dll files to voicevox_core directory
    move_files(str(Path(
        voicevox_plugin_dir / acceleration_mode / voicevox_core_dll_repository[OS][ARCH][acceleration_mode][
            "path"]).resolve()),
               str(Path(voicevox_plugin_dir / acceleration_mode / "voicevox_core").resolve()))
    # delete folder
    shutil.rmtree(Path(
        voicevox_plugin_dir / acceleration_mode / voicevox_core_dll_repository[OS][ARCH][acceleration_mode][
            "path"]))

open_jtalk_dict_path = Path(voicevox_plugin_dir / open_jtalk_dict_file["path"])
if not Path(open_jtalk_dict_path / "sys.dic").is_file():
    download_thread(open_jtalk_dict_file["url"], str(voicevox_plugin_dir.resolve()),
                               open_jtalk_dict_file["sha256"])
    extract_tar_gz(str(voicevox_plugin_dir / os.path.basename(open_jtalk_dict_file["url"])),
                   str(voicevox_plugin_dir.resolve()))


# load the voicevox_core module
if voicevox_core_module is None:
    voicevox_core_module = load_module(
        str(Path(voicevox_plugin_dir / acceleration_mode / "voicevox_core").resolve()))

if core is None:
    acceleration_mode = "AUTO"
if acceleration_mode == "CPU":
    acceleration_mode = voicevox_core_module.AccelerationMode.CPU
elif acceleration_mode == "CUDA" or acceleration_mode == "GPU":
    acceleration_mode = voicevox_core_module.AccelerationMode.GPU

core = voicevox_core_module.VoicevoxCore(
    acceleration_mode=acceleration_mode,
    open_jtalk_dict_dir=str(open_jtalk_dict_path.resolve())
)

core.load_model(VOICE_ID)

def tts_generate_wav_jp(sentence: str):
    start = time.time()

    if len(sentence.strip()) == 0:
        logger.debug("empty sentence")
        wav = np.zeros(0).astype(np.int16)
        TTS_WAV_PATH.write_bytes(wav)
        return

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
