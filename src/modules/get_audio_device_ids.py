if __name__ == '__main__':
    try:
        import speech_recognition as sr

        for mic_id, mic_name in enumerate(sr.Microphone.list_microphone_names()):
            print(f'{mic_id}: {mic_name}')
    except:
        import pyaudio

        p = pyaudio.PyAudio()
        info = p.get_host_api_info_by_index(0)
        numdevices = info.get('deviceCount')

        for i in range(0, numdevices):
            print("Device id ", i, " - ", p.get_device_info_by_host_api_device_index(0, i)["name"])
