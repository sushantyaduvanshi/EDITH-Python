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
        self.pgm_terminated = False     # this property controls the Outermost while loop i.e. (snowboy->recognizer->task)->(snowboy->recognizer->task)->...
        self.hw_detected = False    # this property controls the while loop of restarting snowboy thread after every 15 sec (snowboy)->(snowboy)->...
        self.model = '{}ok_edith.pmdl'.format(self.res_dir)     # this is snowboy hotword detection model (command)
        self.sensitivity = 0.5      # initial sensitivity of snowboy detection
        self.hwd_thread = None      # snowboy hotword detection thread
        self.restart = False

    def hotword_detection_thread(self):
        print(self.sensitivity)
        self.hwd = hotword_detect(model=self.model, sensitivity=self.sensitivity)
        self.hwd.success_function = self.hwd.signal_interrupt   # on success hotword detection it stops snowboy
        self.hwd.detect()
        if(self.hwd.detected):
            self.hw_detected = True     # to tell recognision part of program that hotword is detected


    def start_hwd_thread(self):
        self.hwd_thread = threading.Thread(target=self.hotword_detection_thread)
        self.hwd_thread.start()
        self.hwd_thread_started_time = time.time()


    def hotword_sensitivity_adjust(self):   # adjust sensitivity for hotword detection acc to environmental noice
        match_dict = {0.50:[0,2000],
                        0.48:[2001,8000],
                        0.35:[8001,12000],
                        0.25:[12001,20000],
                        0.15:[20000,50000]}
        curr_energy = cmt.cm_threshold
        for key,value in match_dict.items():
            if( value[0] <= curr_energy <= value[1] ):
                self.sensitivity = key


    def stop_hwd_thread(self):
        self.hwd.detect_stop()


    def detect_recognize_act(self, cmt, stt, tdt):
        while not self.hw_detected and not self.pgm_terminated:     # restart snowboy detection thread after every 15 sec
            cmt.current_mic_threshold()     # adjust mic threshold
            self.hotword_sensitivity_adjust()       # adjust sensitivity of hotword acc to environmental noice
            self.start_hwd_thread()
            while not self.hw_detected and not self.pgm_terminated:
                if(time.localtime().tm_min==0):
                    self.pgm_terminated = True
                    if(self.hwd_thread.is_alive):
                        time.sleep(0.5)
                        self.hwd.interrupted = True
                        self.hwd_thread.join()
                    self.restart = True
                elif( time.time() - self.hwd_thread_started_time >= 15 ):
                    self.stop_hwd_thread()
                    os.system('clear;')
                    break
                time.sleep(0.5)
            self.hwd_thread.join()

        if(self.hw_detected):
            speech = stt.speech_to_text()
            if(speech != None):
                self.do_after_recognition(speech, tdt)
            else:
                print('\nRetrying....')
                speech = stt.speech_to_text()
                if(speech != None):
                    self.do_after_recognition(speech, tdt)


    def do_after_recognition(self, speech, tdt):    # after recognition of speech command into text, processing of input command
        print('\nYou Said : ' + speech + '\n')
        multi_cmd = re.search(r'\band\b', speech.lower())
        if(multi_cmd):
            cmd1 = speech[:multi_cmd.start()-1]
            cmd2 = speech[multi_cmd.end()+1:]
            self.do_after_recognition(cmd1, tdt)
            self.do_after_recognition(cmd2, tdt)
        else:
            if(re.search(r'\byourself\b|\byour\b', speech.lower())):
                if(re.search(r'(terminate|stop|close|quit|shutdown)', speech.lower())):
                    self.pgm_terminated = True
                elif(re.search(r'reboot|restart|refresh|start', speech.lower())):
                    self.pgm_terminated = True
                    self.restart=True
                    self.say('ok_sir')
                else:
                    tdt.identify_task(speech)
            else:
                tdt.identify_task(speech)


    def say(self, file_name):
        os.system('mpg321 {0}{1}.mp3'.format(self.res_dir, file_name))


    def create_gtts(self, speech, file_name):       # it google text to speech, for get voice responses from Edith
        audio = gTTS(text=speech, lang='en-in')
        audio.save('{0}{1}.mp3'.format(self.res_dir, file_name))


    def create_assistant_response_audio(self):      # for creating some default voice responses of Edith; This function is used expilictly during developement.
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
                    self.create_gtts(speech=text, file_name=file_name)
                    os.system('mpg321 {0}{1}.mp3'.format(self.res_dir, file_name))
                elif(opt == '2'):
                    self.create_assistant_response_audio()
            else:
                self.create_gtts(speech=text, file_name=file_name)
                os.system('mpg321 {0}{1}.mp3'.format(self.res_dir, file_name))
        elif(opt == '0'):
            print('\nTask Terminated !!!')
        return




if(__name__ == '__main__'):

    main_obj = main()
    cmt = speech_recognizer.cmt_class()     # cmt -> current mic threshold
    stt = speech_recognizer.stt_class()     # stt -> speech to text
    tdt = do_task(main_obj=main_obj)        # tdt -> todo task
    while not main_obj.pgm_terminated:      # (snowboy->recognizer->task)->(snowboy->recognizer->task)->...
        main_obj.detect_recognize_act(cmt, stt, tdt)
        main_obj.hw_detected = False
        os.system('clear;echo "\n"')
    print('Exited!!!\n')
    if(main_obj.restart):
        os.system('clear;')
        print('Restarting...')
        os.system('kill {0};python3 {1}/main.py'.format(os.getpid(), main_obj.base_dir))
