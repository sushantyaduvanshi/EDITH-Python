import os
import re
import speech_recognizer


class do_task:

    def __init__(self, main_obj=None):
        self.main_obj = main_obj
        self.app_list_string = ''
        os.system('find /Applications -name *.app > {}applications.txt'.format(self.main_obj.res_dir))
        with open(self.main_obj.res_dir + 'applications.txt') as file:
            arr = file.read().strip().split('\n')
            for i in range(len(arr)):
                match = re.search(r'/[a-z _\-A-Z0-9]*.app$', arr[i])
                if match != None:
                    self.app_list_string += arr[i][match.start()+1:match.end()-4].lower() + '|'
            self.app_list_string = self.app_list_string[:-1]


    def identify_task(self, speech):
        speech = speech.lower()
        if(re.search(r'^open', speech)):
            app_name = re.search(self.app_list_string, speech)
            if(app_name):
                app_name = speech[app_name.start():app_name.end()]
            if(re.search(r'new tab', speech)):
                self.open_new_tab_window(action_on='tab',app_name=app_name)
            elif(re.search(r'new window', speech)):
                self.open_new_tab_window(action_on='window', app_name=app_name)
            elif(app_name):
                self.open_app(app_name)

        elif(re.search(r'(prepare|ready) (to|for) (restart|reboot|shutdown|power off)|(quit|stop|close|terminate) all applications', speech)):
            if(re.search(r'restart|reboot|shutdown|power off', speech)):
                self.quit_all_applications()
            else:
                self.quit_all_applications(edith=False)
        
        elif(re.search(r'^close', speech)):
            app_name = re.search(self.app_list_string, speech)
            if(app_name):
                app_name = speech[app_name.start():app_name.end()]                
            if(re.search(r'tab', speech)):
                self.close_tab_window(action_on='tab', app_name=app_name)
            elif(re.search(r'[all|every] window[s]', speech)):
                self.close_tab_window(action_on='all windows', app_name=app_name)
            elif(re.search(r'window', speech)):
                self.close_tab_window(action_on='window', app_name=app_name)
            elif(app_name):
                self.close_app(app_name)


        elif(re.search(r'^search google', speech)):
            if(re.search(r'^search google for', speech)):
                try:
                    self.search_google(speech[18:])
                except IndexError:
                    self.search_google()
            else:
                self.search_google()



    def open_app(self, app_name):
        res = os.system('open -a "{}"'.format(app_name))
        print(res)
        if(res == 0):
            self.main_obj.say(file_name='opening_app')


    def close_app(self, app_name):
        res = os.system('osascript -e \'tell application "{}" to quit\''.format(app_name))
        print(res)
        if(res == 0):
            self.main_obj.say(file_name='closing_app')


    def open_new_tab_window(self, action_on, app_name=None):
        if(action_on=='tab'):
            if(app_name!=None):
                res = os.system('osascript -e \'activate application "{}"\ntell application "system events" to keystroke "t" using command down\''.format(app_name))
            else:
                res = os.system('osascript -e \'tell application "system events" to keystroke "t" using command down\'')
            print(res)
            if(res == 0):
                self.main_obj.say('opened_tab')
        elif(action_on=='window'):
            if(app_name!=None):
                res = os.system('osascript -e \'activate application "{}"\ntell application "system events" to keystroke "n" using command down\''.format(app_name))
            else:
                res = os.system('osascript -e \'tell application "system events" to keystroke "n" using command down\'')
            print(res)
            if(res == 0):
                self.main_obj.say('opened_window')


    def close_tab_window(self, action_on, app_name=None):
        if(action_on=='tab'):
            if(app_name!=None):
                res = os.system('osascript -e \'activate application "{}"\ntell application "system events" to keystroke "w" using command down\''.format(app_name))
            else:
                res = os.system('osascript -e \'tell application "system events" to keystroke "w" using command down\'')
            print(res)
            if(res == 0):
                self.main_obj.say('closed_tab')
        elif(action_on=='window'):
            if(app_name!=None):
                res = os.system('osascript -e \'activate application "{0}"\ntell application "{0}" to close window 1\''.format(app_name))
                print(res)
                if(res == 0):
                    self.main_obj.say('closed_window')
            else:
                self.main_obj.say('app_name_missing')
        elif(action_on=='all windows'):
            if(app_name!=None):
                res = os.system('osascript -e \'activate application "{0}"\ntell application "{0}" to close every window\''.format(app_name))
            else:
                self.main_obj.say('app_name_missing')
            print(res)
            if(res == 0):
                self.main_obj.say('closed_window')


    def search_google(self, content=None):
        if(content):
            res = os.system('open -a safari "https://www.google.co.in/search?q={}"'.format(content))
            print(res)
            if(res == 0):
                self.main_obj.say('showing_results')
        else:
            self.main_obj.say('what_search')
            stt = speech_recognizer.stt_class()
            content = stt.speech_to_text()
            if(content):
                self.search_google(content)
            else:
                self.main_obj.say('wrong_input')


    def quit_all_applications(self, edith=True):
        res = os.system('open {}quit_all_apps.app'.format(self.main_obj.res_dir))
        print(res)
        if(res == 0):
            self.main_obj.say('closing_all_apps')
        if(edith==True):
            self.main_obj.pgm_terminated = True



    # Say method audio files :
    # yes_sir, opened tab, closed tab, opened_window, closed_window, what_search, wrong_input, showing_results, app_name_missing, closing_all_apps
    