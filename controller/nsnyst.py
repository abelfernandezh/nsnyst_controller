from sys import argv
from PyQt4.QtGui import QApplication
from controller.nsnyst.gui import MainWindow
from controller.nsnyst.stimulation import FixationStimuli, Chanel

if __name__ == '__main__':
    app = QApplication(argv)
    main_window = MainWindow()
    main_window.show()
    app.exec_()
