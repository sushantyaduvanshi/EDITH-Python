import speech_recognition as sr

mic = sr.Microphone()
re = sr.Recognizer()


def n(text):
    print('\n' + text + '\n')

try:
    with mic as source:
        re.adjust_for_ambient_noise(source)
        n('noise is adjusted to :'+ str(re.energy_threshold))
    while True:
        with mic as source:
            n('listening to cmd...')
            audio = re.listen(source)
            # audio = re.listen(source, snowboy_configuration=(sbLoc, sbAudio))
        try:
            value = re.recognize_google(audio)
            if str is bytes:  # this version of Python uses bytes for strings (Python 2)
                print("You said {}".format(value).encode("utf-8"))
            else:  # this version of Python uses unicode for strings (Python 3+)
                print("You said {}".format(value))
        except sr.UnknownValueError:
            print("Oops! Didn't catch that")
        except sr.RequestError as e:
            print("Uh oh! Couldn't request results from Google Speech Recognition service; {0}".format(e))
except KeyboardInterrupt:
    pass