import speech_recognition as sr
import time
import threading
import os


class stt_class(sr.Recognizer):

    def __init__(self):
        self.mic = sr.Microphone()
        sr.Recognizer.__init__(self)
        # self.sr = sr.Recognizer()

    def speech_to_text(self):
        with self.mic as source:
            print('\nAdjusting Ambient Noise...\n')
            self.adjust_for_ambient_noise(source)
            os.system('play ./snowboy_resource/resources/dong.wav')
            print('\nListening...\n')
            try:
                audio = self.listen(source, timeout=10)
            except sr.WaitTimeoutError:
                print("You Didn't Say Anything...")
                return None
        print('Recognizing Speech...\n')
        try:
            text = self.recognize_google(audio)
            return text
        except sr.RequestError:
            print('Connection Not Established !!!')
        except sr.UnknownValueError:
            print('Sorry Couldn\'t be Recognized !!!')


class cmt_class(sr.Recognizer):

    def __init__(self):
        self.cm_threshold = 0
        self.mic = sr.Microphone()
        sr.Recognizer.__init__(self)
        # self.re = sr.Recognizer

    def current_mic_threshold(self):
        with self.mic as source:
            self.adjust_for_ambient_noise(source)
            print('noise is adjusted to :'+ str(self.energy_threshold))
            self.cm_threshold = self.energy_threshold



if(__name__ == '__main__'):
    ct = cmt_class()
    ct.current_mic_threshold()
    print('byeee')