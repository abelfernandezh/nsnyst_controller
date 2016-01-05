from PyQt4.QtGui import QMainWindow, QToolBar
from PyQt4.QtCore import QSize
import controller.artwork.icons as fa


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)

        fa_icon = fa.icon('fa.television')
        self.showMaximized()
        self.setWindowTitle('NSNyst Controller')

        self.toolBar = QToolBar()
        self.toolBar.setIconSize(QSize(48, 48))
        self.toolBar.addAction(fa_icon, 'Configurar Estímulo')
        self.addToolBar(self.toolBar)
