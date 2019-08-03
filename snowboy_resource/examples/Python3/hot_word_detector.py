if(__package__ or '.' in __name__):
    from . import snowboydecoder
else:
    import snowboydecoder
import sys
import signal


class hotword_detect:

    def __init__(self, model=None, success_function=snowboydecoder.play_audio_file, sensitivity=0.5):
        self.detected = False
        self.interrupted = False
        if(model == None):
            print("Error: need to specify model name")
            print("Usage: python demo.py your.model")
            sys.exit(-1)
        else:
            self.model = model
        self.success_function = success_function
        self.sensitivity = sensitivity


    def signal_interrupt(self):
        self.detected = True
        self.interrupted = True


    def interrupt_callback(self):
        return self.interrupted


    def detect(self):
        self.detector = snowboydecoder.HotwordDetector(self.model, sensitivity=self.sensitivity)
        print('Listening... Press Ctrl+C to exit')

        # main loop
        self.detector.start(detected_callback=self.success_function,
                    interrupt_check=self.interrupt_callback,
                    sleep_time=0.03)

        self.detector.terminate()

    def detect_stop(self):
        self.interrupted = True
        # self.detector.terminate()
        print('Detecting Stoped...!!!')



if(__name__ == '__main__'):
    h = hotword_detect(model="/Users/sushantyadav/Documents/Projects/Edith/snowboy_resource/examples/Python3/resources/edith.pmdl", success_function=snowboydecoder.play_audio_file)
    try:
        h.detect()
    except KeyboardInterrupt:
        h.detect_stop()
