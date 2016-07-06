from PyQt4.QtGui import QWidget, QPainter


class SignalsRenderer(QWidget):
    _timeLimit = 0
    _height = 0
    _width = 0
    _dY = 0
    _dX = 0
    _currentX = 0
    _currentY1 = 0
    _currentY2 = 0
    _blocks = []

    def __init__(self, parent=None, timeLimit=10):
        super(SignalsRenderer, self).__init__(parent)
        self._timeLimit = timeLimit
        self.updatePaintingValues()

    @property
    def timeLimit(self):
        return self._timeLimit

    @timeLimit.setter
    def timeLimit(self, value):
        self._timeLimit = value
        self.updatePaintingValues()

    def updatePaintingValues(self):
        self._height = self.height()
        self._width = self.width()

        self._dX = self._width / (self._timeLimit * 1000)
        self._currentX = 0
        self._dY = self._height / 4096 / 2.1


    def addSamples(self, block):
        self._blocks = block
        self.update(self._currentX, 0, self._width, self._height)

    def paintEvent(self, QPaintEvent):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)

        for i in range(len(self._blocks)):
            # print("%d %d" % (self._blocks[i][0], self._blocks[i][1]))
            y1 = self._height / 2 - self._blocks[i][0] * self._dY
            y2 = self._height - self._blocks[i][1] * self._dY
            x = self._currentX + self._dX

            painter.drawLine(self._currentX, self._currentY1, x, y1)
            painter.drawLine(self._currentX, self._currentY2, x, y2)

            self._currentX = x
            self._currentY1 = y1
            self._currentY2 = y2

            if self._currentX >= self._width:
                self._currentX = 0
        self._blocks = []

    def resizeEvent(self, QResizeEvent):
        self.updatePaintingValues()
