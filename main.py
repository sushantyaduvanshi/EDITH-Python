from snowboy_resource.examples.Python3.hot_word_detector import hotword_detect
import speech_recognizer
import threading
import time
import re
import os
from gtts import gTTS
from to_do_task import do_task


class main:


    def __init__(self):
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.res_dir = os.path.join(self.base_dir, 'snowboy_resource/resources/')
        self.pgm_terminated = False
        self.hw_detected = False
        self.model = '{}edith.pmdl'.format(self.res_dir)
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
        match_dict = {0.40:[0,3000],
                        # 0.40:[1001,3000],
                        0.35:[3001,8000],
                        0.25:[8001,12000],
                        0.15:[12001,20000],
                        0.1:[20000,50000]}
        curr_energy = cmt.cm_threshold
        for key,value in match_dict.items():
            if( value[0] <= curr_energy <= value[1] ):
                self.sensitivity = key


    def stop_hwd_thread(self):
        self.hwd.detect_stop()


    def detect_recognize_act(self, cmt, stt, tdt):
        while not self.hw_detected:
            cmt.current_mic_threshold()
            self.hotword_sensitivity_adjust()
            self.start_hwd_thread()
            # time.sleep(15)
            while not self.hw_detected:
                if( time.time() - self.hwd_thread_started_time >= 15 ):
                    self.stop_hwd_thread()
                    os.system('clear;echo "\n"')
                    break
            self.hwd_thread.join()
            print('\r')

        if(self.hw_detected):
            # self.say('yes_sir')
            speech = stt.speech_to_text()
            if(speech != None):
                self.do_after_recognition(speech, tdt)
            else:
                print('\nRetrying....')
                speech = stt.speech_to_text()
                if(speech != None):
                    self.do_after_recognition(speech, tdt)


    def do_after_recognition(self, speech, tdt):
        print('\nYou Said : ' + speech + '\n')
        if(re.search(r'(terminate|stop|close|quit) (program|yourself|execution|your execution)', speech.lower())):
            self.pgm_terminated = True
        else:
            tdt.identify_task(speech)


    def say(self, file_name):
        os.system('mpg321 {0}{1}.mp3'.format(self.res_dir, file_name))


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
            if(os.path.isfile('{0}{1}.mp3'.format(self.res_dir, file_name))):
                print('\nAlert ALert aleRT !!!')
                print('\nFile with same name already exsist ...')
                print('\nDo You want to override it or want to Retry with the name ? (override=1 , retry=2)')
                opt = input()
                if(opt == '1'):
                    audio = gTTS(text=text, lang='en-in')
                    audio.save('{0}{1}.mp3'.format(self.res_dir, file_name))
                    os.system('mpg321 {0}{1}.mp3'.format(self.res_dir, file_name))
                elif(opt == '2'):
                    self.create_assistant_response_audio()
            else:
                audio = gTTS(text=text, lang='en-in')
                audio.save('{0}{1}.mp3'.format(self.res_dir, file_name))
                os.system('mpg321 {0}{1}.mp3'.format(self.res_dir, file_name))
        elif(opt == '0'):
            print('\nTask Terminated !!!')
        return
        


if(__name__ == '__main__'):

    main_obj = main()
    cmt = speech_recognizer.cmt_class()
    stt = speech_recognizer.stt_class()
    tdt = do_task(main_obj=main_obj)
    # tdt = None
    while not main_obj.pgm_terminated:
        main_obj.detect_recognize_act(cmt, stt, tdt)
        main_obj.hw_detected = False
        os.system('clear;echo "\n"')
    print('Exited!!!\n')
