from dotenv import load_dotenv
from os import getenv
from enum import Enum

load_dotenv()


class TranslationBackend(Enum):
    ARGO = 'ARGO'
    DEEPL = 'DEPPL'
    GOOGLE = 'GOOGLE'
    WHISPER = 'WHISPER'


TRANSLATION_BACKEND: TranslationBackend = TranslationBackend[
    getenv('TRANSLATION_BACKEND', TranslationBackend.ARGO)]  # 'ARGO' | 'DEEPL' | 'GOOGL' | 'WHISPER'
assert TRANSLATION_BACKEND in [TranslationBackend.ARGO, TranslationBackend.DEEPL, TranslationBackend.GOOGLE,
                               TranslationBackend.WHISPER]
TARGET_LANGUAGE_CODE = getenv('TARGET_LANGUAGE_CODE')
DEEPL_AUTH_KEY = getenv('DEEPL_AUTH_KEY')

if TRANSLATION_BACKEND == TranslationBackend.ARGO:
    import argostranslate.package
    import argostranslate.translate

    # Download and install Argos Translate package
    argostranslate.package.update_package_index()
    available_packages = argostranslate.package.get_available_packages()
    package_to_install = next(
        filter(
            lambda x: x.to_code == TARGET_LANGUAGE_CODE, available_packages
        )
    )
    print("INSTALL BEGIN")
    argostranslate.package.install_from_path(package_to_install.download())
    print("INSTALL ENDED")

elif TRANSLATION_BACKEND == TranslationBackend.GOOGLE:
    import googletrans

    google_translator = googletrans.Translator()

elif TRANSLATION_BACKEND == TranslationBackend.DEEPL:
    import deepl

    deepl_translator = deepl.Translator(DEEPL_AUTH_KEY)

elif TRANSLATION_BACKEND == TranslationBackend.WHISPER:
    raise NotImplementedError()


def translate(text: str, from_code: str, to_code: str):
    if TRANSLATION_BACKEND == TranslationBackend.DEEPL:
        return deepl_translator.translate_text(
            text, target_lang=TARGET_LANGUAGE_CODE)

    if TRANSLATION_BACKEND == TranslationBackend.GOOGLE:
        return google_translator.translate(
            text, dest=TARGET_LANGUAGE_CODE).text

    if TRANSLATION_BACKEND == TranslationBackend.ARGO:
        return argostranslate.translate.translate(text, from_code, to_code)
