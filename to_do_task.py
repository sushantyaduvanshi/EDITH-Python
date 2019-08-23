import os
import re
import speech_recognizer
import wikipedia
import threading
import time


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
            self.app_list_string = self.app_list_string + 'finder'


    def identify_task(self, speech):
        speech = speech.lower()
        if(re.search(r'^open', speech)):
            app_name = re.search(self.app_list_string, speech)
            if(app_name):
                app_name = speech[app_name.start():app_name.end()]
            if(re.search(r'\bfile\b|\bfolder\b', speech)):
                self.find_file_folder(speech[5:])
            elif(re.search(r'new tab', speech)):
                self.open_new_tab_window(action_on='tab',app_name=app_name)
            elif(re.search(r'new window', speech)):
                self.open_new_tab_window(action_on='window', app_name=app_name)
            elif(app_name):
                self.open_app(app_name)

        elif(re.search(r'(prepare|ready) (to|for) (restart|reboot|shutdown|power off)|(quit|stop|close|terminate) all application', speech)):
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
            elif(re.search(r'[all|every] window', speech)):
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

        elif(re.search(r'^(tell me about|what is|search for)', speech)):
            title = re.search(r'^(tell me about|what is|search for)', speech)
            try:
                title = speech[title.end()+1:]
                self.wiki_info(title)
            except IndexError:
                self.wiki_info()

        elif(re.search(r'\bminimise', speech)):
            app_name = re.search(self.app_list_string, speech)
            if(app_name):
                app_name = speech[app_name.start():app_name.end()]
                self.min_app(app_name)


    def min_app(self, app_name):
        os.system('osascript -e \'activate application "{}"\''.format(app_name))
        os.system('osascript -e \'tell application "system events" to keystroke "m" using command down\'')
        self.main_obj.say('ok_sir')


    def open_app(self, app_name, app_arg=''):
        os.system('open -a "{0}" {1}'.format(app_name, app_arg))
        self.main_obj.say(file_name='opening_app')


    def close_app(self, app_name):
        os.system('osascript -e \'tell application "{}" to quit\''.format(app_name))
        self.main_obj.say(file_name='closing_app')


    def open_new_tab_window(self, action_on, app_name=None):
        if(action_on=='tab'):
            if(app_name!=None):
                os.system('osascript -e \'activate application "{}"\''.format(app_name))
                os.system('osascript -e \'tell application "system events" to keystroke "t" using command down\'')
            else:
                os.system('osascript -e \'tell application "system events" to keystroke "t" using command down\'')
            self.main_obj.say('opened_tab')
        elif(action_on=='window'):
            if(app_name!=None):
                os.system('osascript -e \'activate application "{}"\ntell application "system events" to keystroke "n" using command down\''.format(app_name))
            else:
                os.system('osascript -e \'tell application "system events" to keystroke "n" using command down\'')
            self.main_obj.say('opened_window')


    def close_tab_window(self, action_on, app_name=None):
        if(action_on=='tab'):
            if(app_name!=None):
                os.system('osascript -e \'activate application "{}"\ntell application "system events" to keystroke "w" using command down\''.format(app_name))
            else:
                os.system('osascript -e \'tell application "system events" to keystroke "w" using command down\'')
            self.main_obj.say('closed_tab')
        elif(action_on=='window'):
            if(app_name!=None):
                os.system('osascript -e \'activate application "{0}"\ntell application "{0}" to close window 1\''.format(app_name))
                self.main_obj.say('closed_window')
            else:
                self.main_obj.say('app_name_missing')
        elif(action_on=='all windows'):
            if(app_name!=None):
                os.system('osascript -e \'activate application "{0}"\ntell application "{0}" to close every window\''.format(app_name))
            else:
                self.main_obj.say('app_name_missing')
            self.main_obj.say('closed_window')


    def search_google(self, content=None):
        if(content):
            os.system('open -a safari "https://www.google.co.in/search?q={}"'.format(content))
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
        os.system('open {}quit_all_apps.app'.format(self.main_obj.res_dir))
        self.main_obj.say('closing_all_apps')
        if(edith==True):
            self.main_obj.pgm_terminated = True


    def wiki_info(self, title=None):
        if(title):
            th = threading.Thread(target=self.main_obj.say, kwargs={'file_name':'fetching_info'})
            th.start()
            info = wikipedia.page(title)
            self.main_obj.create_gtts(speech=info.content[:300], file_name='wiki_info')
            self.main_obj.say('wiki_info')
            print(info.content[:300])
        else:
            self.main_obj.say('what_search')
            stt = speech_recognizer.stt_class()
            title = stt.speech_to_text()
            if(title):
                self.wiki_info(title)
            else:
                self.main_obj.say('wrong_input')


    def find_file_folder(self, speech):
        file_word = re.search(r'\bfile', speech)
        folder = re.search(r'\bfolder', speech)
        app_name = re.search(self.app_list_string, speech)
        directory = re.search(r'\bdirectory\b', speech)
        if(not directory):
            directory = '~'
        else:
            res = re.search(r'\binside\b', speech)
            res = speech[res.end()+1:directory.start()-1]
            arr = res.split()
            string = '.*'.join(arr)
            print('test0 : ',arr[-1]+'*', string)
            os.system('find ~ -path ~/Library -prune -o -type d -iname {0} | grep -i {1} > {2}tmp.txt'.format(arr[-1]+'*', string, self.main_obj.res_dir))
            with open("{0}tmp.txt".format(self.main_obj.res_dir)) as file:
                file = file.read()
                print('test1 : '+file)
                file = file.strip()
                file = file.split('\n')
                print('test2 : ', file)
                if(len(file)==1 and file[0]!='' and file[0]!='\n'):
                    print(file[0])
                    directory = file[0]
                elif(len(file)>1):
                    return self.main_obj.say(file_name='more_than_one_folder')
                else:
                    return self.main_obj.say(file_name='no_folder')
        if(file_word):
            file_name = speech[:file_word.start()-1].strip().split()
            # file_name = '*'+'*'.join(file_name)+'*' # for searching all result with words inbetween
            file_name = '*'.join(file_name)+'*'
            print(file_name)
            if(file_name!='' or file_name!=' '):
                os.system('find {0} -path ~/Library -prune -o -type f -iname {1} | grep -v Library > {2}tmp.txt'.format(directory, file_name, self.main_obj.res_dir))
                with open('{0}tmp.txt'.format(self.main_obj.res_dir)) as file:
                    file = file.read()
                    file = file.strip()
                    files = file.split('\n')
                    if(len(files)==1 and files[0]!='' and files[0]!='\n'):
                        print(files[0])
                        if(app_name):
                            self.open_app(app_name=speech[app_name.start():app_name.end()], app_arg=files[0])
                        else:
                            os.system('open {}'.format(files[0]))
                    elif(len(files)>1):
                        self.main_obj.say(file_name='more_than_one_file')
                    else:
                        self.main_obj.say(file_name='no_file')
        elif(folder):
            folder_name = speech[:folder.start()-1].strip().split()
            # folder_name = '*'+'*'.join(folder_name)+'*' # for searching all result with words inbetween
            folder_name = '*'.join(folder_name)+'*'
            print(folder_name)
            if(folder_name!='' or folder_name!=' '):
                os.system('find {0} -path ~/Library -prune -o -type d -iname {1} | grep -v Library > {2}tmp.txt'.format(directory, folder_name, self.main_obj.res_dir))
                with open('{0}tmp.txt'.format(self.main_obj.res_dir)) as file:
                    file = file.read()
                    file = file.strip()
                    files = file.split('\n')
                    if(len(files)==1 and files[0]!='' and files[0]!='\n'):
                        print(files[0])
                        if(app_name):
                            self.open_app(app_name=speech[app_name.start():app_name.end()], app_arg=files[0])
                        else:
                            os.system('open {}'.format(files[0]))
                    elif(len(files)>1):
                        self.main_obj.say(file_name='more_than_one_folder')
                    else:
                        self.main_obj.say(file_name='no_folder')


    # Say method audio files :
    # no_file, more_than_one_file, wiki_info(dynamicaly created by pgm), fetching_info, yes_sir, opened tab, closed tab, opened_window, closed_window, what_search, wrong_input, showing_results, app_name_missing, closing_all_apps, 
    


    # Commands:
    # open [app_name]
    # open [file_name|folder_name]
    # open [file_name|folder_name] in [app_name]
    # open [file_name|folder_name] inside [dir_name]
    # open [file_name|folder_name] in [app_name] inside [dir_name]
    # open new tab|window
    # close all applications
    # prepare for shutdown|restart
    # close [app_name]
    # close this tab
    # close all windows of [app_name]
    # close this window of [app_name]
    # search google for [context]
    # tell me about|what is|search for [context] #{for wikipedia results}
    # minimise [app_name]