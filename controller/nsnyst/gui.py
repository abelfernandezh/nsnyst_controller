from PyQt4.QtGui import QMainWindow, QToolBar
import qtawesome


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)

        self.showMaximized()
        self.setWindowTitle('NSNyst Controller')

        self.toolBar = QToolBar()
        self.toolBar.addAction('Configure Test')
        self.addToolBar(self.toolBar)
