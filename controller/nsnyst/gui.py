from PyQt4.QtGui import QMainWindow, QToolBar, QDialog, QAction, QFormLayout, QLineEdit, QCheckBox, QSpinBox, QComboBox, \
    QStackedWidget, QWidget, QLabel, QPushButton, QHBoxLayout, QTextEdit, QDesktopWidget, QMessageBox, QPainter, QColor, \
    QBrush
from PyQt4.QtCore import QSize, Qt, QPointF, QThread, pyqtSignal
import artwork.icons as fa
from stimulation import Channel, SaccadicStimulus, Protocol
from math import tan, atan, degrees, atan2, radians
import random


class GenericParametersWidget(QWidget):
    def __init__(self, parent=None):
        super(GenericParametersWidget, self).__init__(parent)
        self.f_layout = QFormLayout()
        self.type = QComboBox()
        self.type.addItem('Prueba Sacádica')
        self.type.addItem('Prueba de Persecución')
        self.f_layout.addRow('Tipo de Prueba', self.type)
        self.stimulus_name = QLineEdit()
        self.f_layout.addRow('Nombre', self.stimulus_name)
        self.horizontal_channel = QCheckBox()
        self.f_layout.addRow('Canal Horizontal', self.horizontal_channel)
        self.vertical_channel = QCheckBox()
        self.f_layout.addRow('Canal Vertical', self.vertical_channel)
        self.stimulus_duration = QSpinBox()
        self.stimulus_duration.setRange(1, 500)
        self.stimulus_duration.setMaximumWidth(100)
        self.f_layout.addRow('Duración', self.stimulus_duration)

        self.setLayout(self.f_layout)

    @property
    def name(self):
        return self.stimulus_name.value()

    @property
    def duration(self):
        return self.stimulus_duration.value()

    @property
    def channels(self):
        if self.vertical_channel.isChecked() and self.horizontal_channel.isChecked():
            return 0
        if self.vertical_channel.isChecked():
            return Channel.Vertical_Channel
        if self.horizontal_channel.isChecked():
            return Channel.Horizontal_Channel


class SaccadicStimuliParametersWidget(QWidget):
    def __init__(self, parent=None):
        super(SaccadicStimuliParametersWidget, self).__init__(parent)
        self.saccadic_amplitude = QSpinBox()
        self.saccadic_amplitude.setMaximumWidth(100)
        self.saccadic_velocity = QSpinBox()
        self.saccadic_velocity.setMaximumWidth(100)

        self.f_layout = QFormLayout()
        self.f_layout.addRow('Amplitud', self.saccadic_amplitude)
        self.f_layout.addRow('Velocidad', self.saccadic_velocity)
        self.setLayout(self.f_layout)

    @property
    def velocity(self):
        return self.saccadic_velocity.value()

    @property
    def amplitude(self):
        self.saccadic_amplitude.value()


class FixationStimuliParametersWidget(QWidget):
    def __init__(self, parent=None):
        super(FixationStimuliParametersWidget, self).__init__(parent)
        self.fixation_duration = QSpinBox()
        self.fixation_duration.setMaximumWidth(100)
        self.fixation_amplitude = QSpinBox()
        self.fixation_amplitude.setMaximumWidth(100)
        self.fixation_variation = QSpinBox()
        self.fixation_variation.setMaximumWidth(100)

        self.f_layout = QFormLayout()
        self.f_layout.addRow('Duración', self.fixation_duration)
        self.f_layout.addRow('Amplitud', self.fixation_amplitude)
        self.f_layout.addRow('Variación', self.fixation_variation)
        self.setLayout(self.f_layout)

    @property
    def duration(self):
        return self.fixation_duration.value()

    @property
    def amplitude(self):
        return self.fixation_amplitude.value()

    @property
    def variation(self):
        return self.fixation_variation.value()


class CreateStimuliWidget(QDialog):
    def __init__(self, parent=None):
        super(CreateStimuliWidget, self).__init__(parent)
        self.setWindowTitle('Crear nuevo estímulo')
        self.generic = GenericParametersWidget()
        self.fixation_features = FixationStimuliParametersWidget()
        self.saccadic_features = SaccadicStimuliParametersWidget()

        self.setMinimumWidth(400)

        self.h_layout = QHBoxLayout()

        self.advanced_properties_stack = QStackedWidget()
        self.advanced_properties_stack.addWidget(self.fixation_features)
        self.advanced_properties_stack.addWidget(self.saccadic_features)

        self.h_layout.addWidget(self.generic)
        self.h_layout.addWidget(self.advanced_properties_stack)
        self.advanced_properties_stack.setCurrentIndex(0)
        self.setLayout(self.h_layout)

        fa_save = fa.icon('fa.save')
        self.save_button = QPushButton(fa_save, 'Guardar')
        self.save_button.setMaximumWidth(100)

        self.generic.type.currentIndexChanged.connect(self.on_index_change)

    def save_stimuli(self):
        pass

    def on_index_change(self):
        self.advanced_properties_stack.setCurrentIndex(self.generic.type.currentIndex())


class StimulusWidget(QWidget):
    def __init__(self, stimulus, parent=None):
        super(StimulusWidget, self).__init__(parent)
        self.h_layout = QHBoxLayout()
        self.stimulus_name = QLabel(stimulus.name)
        self.separator = QLabel('-->')
        self.stimulus_type = QLabel()
        if type(stimulus) != SaccadicStimulus:
            self.stimulus_type.setText('Estímulo Sacádico')
        else:
            self.stimulus_type.setText('Estímulo de Fijación')
        fa_delete = fa.icon('fa.trash')
        fa_edit = fa.icon('fa.pencil')
        self.edit_stimulus = QPushButton(fa_edit, '')
        self.delete_stimulus = QPushButton(fa_delete, '')
        self.h_layout.addWidget(self.stimulus_name)
        self.h_layout.addWidget(self.separator)
        self.h_layout.addWidget(self.stimulus_type)
        self.h_layout.addWidget(self.edit_stimulus)
        self.h_layout.addWidget(self.delete_stimulus)

        self.setLayout(self.h_layout)


class StimuliList(QWidget):
    def __init__(self, stimuli_list, parent=None):
        super(StimuliList, self).__init__(parent)


class CreateProtocolWidget(QDialog):
    def __init__(self, parent=None):
        super(CreateProtocolWidget, self).__init__(parent)
        self.setWindowTitle('Crear protocolo')

        self.f_layout = QFormLayout()
        self.protocol_name = QLineEdit()
        self.protocol_notes = QTextEdit()
        self.protocol_notes.setMaximumHeight(50)

        stimulus = SaccadicStimulus('Ejemplo 1', 12, 12, 12, 1)
        protocol = Protocol('Prueba', 'Proasdad', 12)
        protocol.add_stimulus(stimulus)
        self.sti = StimulusWidget(stimulus)

        self.f_layout.addRow('Nombre', self.protocol_name)
        self.f_layout.addRow('Notas', self.protocol_notes)

        self.f_layout.addRow(self.sti)

        self.setLayout(self.f_layout)

    @property
    def name(self):
        return self.protocol_name.text()

    @property
    def notes(self):
        return self.protocol_notes.toPlainText()


class RepaintThread(QThread):
    paintStimulus = pyqtSignal()
    stopStimulus = pyqtSignal()

    def __init__(self, saccadic_stimulus):
        QThread.__init__(self)
        self.saccadic_stimulus = saccadic_stimulus
        self.real_duration = 0

    def run(self):
        while True:
            self.paintStimulus.emit()
            self.real_duration = self.saccadic_stimulus.fixation_duration + (random.randrange(
                    self.saccadic_stimulus.variation * 2)) - self.saccadic_stimulus.variation
            self.msleep(self.real_duration)
            self.saccadic_stimulus.duration -= self.real_duration

        if self.saccadic_stimulus.duration <= 0:
            self.stopStimulus.emit()


class StimulatorWidget(QWidget):
    def __init__(self, screen_2_height_mm, screen_2_width_mm, parent=None):
        super(StimulatorWidget, self).__init__(parent)
        self.screen = QDesktopWidget().screenGeometry(1)
        self.move(self.screen.left(), self.screen.top())
        self.height = self.screen.height()
        self.width = self.screen.width()
        self.resize(self.screen.width(), self.screen.height())
        stimuli_test = SaccadicStimulus('Sacádica 30', 10000, 60, 20, 2000)
        protocol = Protocol('Protocolo de Prueba', 'Este es un protocolo para probar el estímulo', 300)
        protocol.add_stimulus(stimuli_test)
        self.pixel_size = screen_2_width_mm / self.screen.width()
        self.diff = (tan(radians(stimuli_test.amplitude)) * protocol.distance)
        print(tan(radians(stimuli_test.amplitude)) * protocol.distance)

        self.thread = RepaintThread(stimuli_test)
        self.thread.start()
        self.thread.paintStimulus.connect(self.show_paint)
        self.thread.stopStimulus.connect(self.stop_paint)
        self.should_paint = True

    def paintEvent(self, event):
        qp = QPainter(self)
        qp.fillRect(0, 0, self.screen.width(), self.screen.height(), QColor(255, 255, 255))
        qp.setPen(QColor(25, 25, 112))
        qp.setBrush(QBrush(QColor(25, 25, 112)))
        if self.should_paint:
            qp.drawEllipse(self.screen.width() / 2 - 15 + self.diff, self.screen.height() / 2, 30, 30)

    def show_paint(self):
        self.diff *= -1
        self.update()

    def stop_paint(self):
        self.should_paint = False
        self.update()

    def paint_stimuli(self, protocol):
        pass

    def show_stimulator(self):
        if QDesktopWidget().numScreens() is 1:
            QMessageBox.warning(self, "Múltiples pantallas requeridas",
                                "Para ejecutar esta funcionalidad se necesita otro monitor. " +
                                "Conecte uno e intente de nuevo configurándolo como una pantalla extendida.")
        else:
            self.showFullScreen()


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.showMaximized()
        self.setWindowTitle('NSNyst Controller')
        self.create_protocol = CreateProtocolWidget()
        self.stimulator = StimulatorWidget(268, 476)
        self.stimulator.show_stimulator()
        self.tool_bar = QToolBar()
        self.tool_bar.setIconSize(QSize(48, 48))

        fa_icon = fa.icon('fa.television')
        self.add_stimuli_action = QAction(fa_icon, 'Crear nuevo estímulo', self.tool_bar)
        self.add_stimuli_action.triggered.connect(self.create_protocol.show)

        self.tool_bar.addAction(self.add_stimuli_action)

        self.addToolBar(self.tool_bar)

    def closeEvent(self, *args, **kwargs):
        self.stimulator.close()
