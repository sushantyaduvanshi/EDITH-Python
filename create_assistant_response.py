from main import main

if(__name__ == '__main__'):
    obj = main()
    while True:
        obj.create_assistant_response_audio()
        print('\n\nDo want to add another ? (y/n)')
        opt = input()
        if(opt == 'y'):
            continue
        elif(opt == 'n'):
            break