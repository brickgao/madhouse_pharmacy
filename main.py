#encoding: utf-8

import ui, qtgui, threading

class threadWevservice(threading.Thread):

    def __init__(self, thread_name):
        threading.Thread.__init__(self)

    def run(self):
        ui.run()

class threadGui(threading.Thread):

    def __init__(self, thread_name):
        threading.Thread.__init__(self)

    def run(self):
        qtgui.run()

if __name__ == '__main__':
    webService = threadWevservice('webService')
    gui = threadGui('gui')
    webService.start()
    gui.start()