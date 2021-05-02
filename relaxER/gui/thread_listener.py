from PyQt5.QtCore import QThread

class ThreadListener(QThread):
    def __init__(self, event):
        super().__init__()
        
        self.__event = event
        self.abort = False

    def run(self):
        exit = False

        while (not exit) and (not self.abort):
            exit = self.__event.wait(1)