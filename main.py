from snowboy_resource.examples.Python3.hot_word_detector import hotword_detect
import speech_recognizer
import threading
import time
import re
import os
from gtts import gTTS


class main:


    def __init__(self):
        self.pgm_terminated = False
        self.hw_detected = False
        self.model = './snowboy_resource/resources/edith.pmdl'
        self.sensitivity = 0.5
        self.hwd_thread = None


    def hotword_detection_thread(self):
        print(self.sensitivity)
        self.hwd = hotword_detect(model=self.model, sensitivity=self.sensitivity)
        self.hwd.success_function = self.hwd.signal_interrupt
        self.hwd.detect()
        if(self.hwd.detected and self.hwd.detected == True):
            self.hw_detected = True


    def start_hwd_thread(self):
        self.hwd_thread = threading.Thread(target=self.hotword_detection_thread)
        self.hwd_thread.start()
        self.hwd_thread_started_time = time.time()


    def hotword_sensitivity_adjust(self):
        match_dict = {0.5:[0,5000],
                        0.45:[5001,10000],
                        0.35:[10001,15000],
                        0.25:[15001,20000],
                        0.15:[20000,25000],
                        0.1:[25000,50000]}
        curr_energy = cmt.cm_threshold
        for key,value in match_dict.items():
            if( value[0] <= curr_energy <= value[1] ):
                self.sensitivity = key


    def stop_hwd_thread(self):
        self.hwd.detect_stop()


    def detect_recognize_act(self, cmt, stt):
        while not self.hw_detected:
            cmt.current_mic_threshold()
            self.hotword_sensitivity_adjust()
            self.start_hwd_thread()
            # time.sleep(15)
            while not self.hw_detected:
                if( time.time() - self.hwd_thread_started_time >= 15 ):
                    self.stop_hwd_thread()
                    break
            self.hwd_thread.join()
            print('\r')

        if(self.hw_detected):
            # self.say('yes_sir')
            text = stt.speech_to_text()
            if(text != None):
                print('\nYou Said : ' + text + '\n')
                if(re.search(r'terminate program',text.lower())):
                    self.pgm_terminated = True
            else:
                pass


    def say(self, file_name):
        os.system('mpg321 ./snowboy_resource/resources/{}.mp3'.format(file_name))


    def create_assistant_response_audio(self):
        stt = speech_recognizer.stt_class()
        print('\nSay Text ...')
        text = stt.speech_to_text()
        print('\nEnter File Name to be saved with ...')
        file_name = input()
        print("\nYour inputs : ")
        print('\nText = {}\nFile Name = {}'.format(text, file_name))
        print('\nTo confirm press 1 else 0 to decline the task !')
        opt = input()
        if(opt == '1'):
            if(os.path.isfile('./snowboy_resource/resources/{}.mp3'.format(file_name))):
                print('\nAlert ALert aleRT !!!')
                print('\nFile with same name already exsist ...')
                print('\nDo You want to override it or want to Retry with the name ? (override=1 , retry=2)')
                opt = input()
                if(opt == '1'):
                    audio = gTTS(text=text, lang='en-in')
                    audio.save('./snowboy_resource/resources/{}.mp3'.format(file_name))
                    os.system('mpg321 ./snowboy_resource/resources/{}.mp3'.format(file_name))
                elif(opt == '2'):
                    self.create_assistant_response_audio()
            else:
                audio = gTTS(text=text, lang='en-in')
                audio.save('./snowboy_resource/resources/{}.mp3'.format(file_name))
                os.system('mpg321 ./snowboy_resource/resources/{}.mp3'.format(file_name))
        elif(opt == '0'):
            print('\nTask Terminated !!!')
        return
        


if(__name__ == '__main__'):

    cmt = speech_recognizer.cmt_class()
    stt = speech_recognizer.stt_class()
    main_obj = main()
    while not main_obj.pgm_terminated:
        main_obj.detect_recognize_act(cmt, stt)
        main_obj.hw_detected = False
    print('Exited!!!\n')
