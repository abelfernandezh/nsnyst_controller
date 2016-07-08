from os.path import dirname, join
from math import tan, atan, degrees, atan2, radians
import random

from PyQt4.QtGui import QMainWindow, QToolBar, QDialog, QAction, QFormLayout, QLineEdit, QCheckBox, QSpinBox, QComboBox, \
    QStackedWidget, QWidget, QLabel, QPushButton, QHBoxLayout, QTextEdit, QVBoxLayout, QDesktopWidget, QMessageBox, \
    QListWidget, QDialogButtonBox, QListWidgetItem, QDesktopWidget, QMessageBox, QPainter, QColor, \
    QBrush, QFileDialog, QSizePolicy, QIcon
from PyQt4.QtCore import QSize, Qt, QPointF, QThread, pyqtSignal, QTime
import artwork.icons as fa
from stimulation import Channel, SaccadicStimulus, PursuitStimulus, Protocol, StimulusType, Stimulus
from core import user_settings
from visualization import SignalsRenderer
from adquisition import Adquirer, SerialHelper
from storage import Record, Test, RecordsDBIndex, ProtocolsDBIndex


class GenericParametersWidget(QWidget):
    def __init__(self, parent=None):
        super(GenericParametersWidget, self).__init__(parent)
        self.f_layout = QFormLayout()
        self.type = QComboBox()
        self.type.addItem('Prueba Sacádica')
        self.type.addItem('Prueba de Persecución')
        self.f_layout.addRow('Tipo de Prueba', self.type)
        self.stimulus_name = QLineEdit()
        self.stimulus_name.setPlaceholderText('Nombre del estímulo')
        self.f_layout.addRow('Nombre', self.stimulus_name)
        self.horizontal_channel = QCheckBox()
        self.horizontal_channel.setChecked(True)
        self.f_layout.addRow('Canal Horizontal', self.horizontal_channel)
        self.vertical_channel = QCheckBox()
        self.f_layout.addRow('Canal Vertical', self.vertical_channel)
        self.stimulus_duration = QSpinBox()
        self.stimulus_duration.setRange(1, 500)
        self.stimulus_duration.setValue(15)
        self.stimulus_duration.setMaximumWidth(100)
        self.stimulus_duration.setSuffix(' s')
        self.f_layout.addRow('Duración', self.stimulus_duration)

        self.setLayout(self.f_layout)

    @property
    def name(self):
        return self.stimulus_name.text()

    @property
    def duration(self):
        return self.stimulus_duration.value()

    @property
    def channels(self):
        if self.vertical_channel.isChecked() and self.horizontal_channel.isChecked():
            return Channel.Both_Channels
        if self.vertical_channel.isChecked():
            return Channel.Vertical_Channel
        if self.horizontal_channel.isChecked():
            return Channel.Horizontal_Channel
        return None


class PursuitStimuliParametersWidget(QWidget):
    def __init__(self, parent=None):
        super(PursuitStimuliParametersWidget, self).__init__(parent)
        self.pursuit_amplitude = QSpinBox()
        self.pursuit_amplitude.setMaximumWidth(100)
        self.pursuit_amplitude.setValue(45)
        self.pursuit_amplitude.setSuffix(' º')

        self.pursuit_velocity = QSpinBox()
        self.pursuit_velocity.setMaximumWidth(100)
        self.pursuit_velocity.setValue(30)
        self.pursuit_velocity.setSuffix(' º/s')

        self.f_layout = QFormLayout()
        self.f_layout.addRow('Amplitud', self.pursuit_amplitude)
        self.f_layout.addRow('Velocidad', self.pursuit_velocity)
        self.setLayout(self.f_layout)

    @property
    def velocity(self):
        return self.pursuit_velocity.value()

    @property
    def amplitude(self):
        return self.pursuit_amplitude.value()


class SaccadicStimuliParametersWidget(QWidget):
    def __init__(self, parent=None):
        super(SaccadicStimuliParametersWidget, self).__init__(parent)
        self.fixation_duration = QSpinBox()
        self.fixation_duration.setRange(1, 2000)
        self.fixation_duration.setValue(400)
        self.fixation_duration.setSuffix(' ms')

        self.fixation_amplitude = QSpinBox()
        self.fixation_amplitude.setRange(1, 150)
        self.fixation_amplitude.setValue(60)
        self.fixation_amplitude.setSuffix(' º')

        self.fixation_variation = QSpinBox()
        self.fixation_variation.setRange(1, 1000)
        self.fixation_variation.setValue(50)
        self.fixation_variation.setSuffix(' ms')

        self.f_layout = QFormLayout()
        self.f_layout.addRow('Duración de la fijación', self.fixation_duration)
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
        self.stimulus = None
        self.generic = GenericParametersWidget()
        self.saccadic_features = SaccadicStimuliParametersWidget()
        self.pursuit_features = PursuitStimuliParametersWidget()
        self.stimulus_type = StimulusType.Saccadic

        self.setMinimumWidth(400)

        self.h_layout = QHBoxLayout()
        self.main_layout = QVBoxLayout()

        self.advanced_properties_stack = QStackedWidget()
        self.advanced_properties_stack.addWidget(self.saccadic_features)
        self.advanced_properties_stack.addWidget(self.pursuit_features)

        self.h_layout.addWidget(self.generic)
        self.h_layout.addWidget(self.advanced_properties_stack)
        self.advanced_properties_stack.setCurrentIndex(0)

        self.button_box = QDialogButtonBox()

        self.button_box.addButton('', QDialogButtonBox.AcceptRole).setIcon(QIcon(join('icons', 'save.svg')))
        self.button_box.addButton('', QDialogButtonBox.RejectRole).setText('Cancelar')

        self.main_layout.addLayout(self.h_layout)
        self.main_layout.addWidget(self.button_box)

        self.setLayout(self.main_layout)

        self.generic.type.currentIndexChanged.connect(self.on_index_change)
        self.button_box.accepted.connect(self.save_button_pressed)
        self.button_box.rejected.connect(self.reject)

    def save_button_pressed(self):
        if not self.stimulus_is_valid():
            return

        name = self.generic.name
        duration = self.generic.duration
        channel = self.generic.channels

        if self.stimulus_type == StimulusType.Saccadic:
            f_amplitude = self.saccadic_features.amplitude
            f_duration = self.saccadic_features.duration
            f_variation = self.saccadic_features.variation
            stimulus_data = SaccadicStimulus(name, duration, f_amplitude, f_variation, f_duration, channel)
        else:
            p_amplitude = self.pursuit_features.amplitude
            velocity = self.pursuit_features.velocity
            stimulus_data = PursuitStimulus(name, duration, p_amplitude, velocity, channel)

        self.stimulus = stimulus_data
        self.accept()

    def on_index_change(self):
        self.advanced_properties_stack.setCurrentIndex(self.generic.type.currentIndex())
        self.stimulus_type = StimulusType(self.generic.type.currentIndex())

    def stimulus_is_valid(self) -> bool:
        messages = []
        if self.generic.name == '' or self.generic.name.isspace():
            messages.append('No se ha especificado un nombre válido')
        else:
            for s in self.generic.name.split(' '):
                if not s == '' and not s.isalnum():
                    messages.append('No ha especificado un nombre válido')
                    break
        if self.generic.channels is None:
            if len(messages) == 0:
                messages.append('No ha seleccionado ningún canal')
            else:
                messages.append('ni ha seleccionado ningún canal')

        if len(messages) == 0:
            return True
        else:
            s = 'Falta información:'
            for i in messages:
                s += '\n\t' + i
            QMessageBox.warning(self, "Datos insuficientes", s)
            return False


class StimulusWidget(QWidget):
    def __init__(self, stimulus, parent=None):
        super(StimulusWidget, self).__init__(parent)
        self.stimulus = stimulus
        self.marked_for_deletion = False
        self.marked_for_edition = False
        self.h_layout = QHBoxLayout()
        self.stimulus_name = QLabel(stimulus.name)
        self.separator = QLabel('-->')
        self.stimulus_type = QLabel()
        if type(stimulus) == SaccadicStimulus:
            self.stimulus_type.setText('Estímulo Sacádico')
        else:
            self.stimulus_type.setText('Estímulo de Persecución')
        fa_delete = fa.icon('fa.trash')
        fa_edit = fa.icon('fa.pencil')
        self.edit_stimulus = QPushButton(fa_edit, '')
        self.delete_stimulus = QPushButton(fa_delete, '')
        self.delete_stimulus.clicked.connect(self.remove)
        self.edit_stimulus.clicked.connect(self.edit)
        self.h_layout.addWidget(self.stimulus_name)
        self.h_layout.addWidget(self.separator)
        self.h_layout.addWidget(self.stimulus_type)
        self.h_layout.addWidget(self.edit_stimulus)
        self.h_layout.addWidget(self.delete_stimulus)

        self.setLayout(self.h_layout)

    def remove(self):
        self.marked_for_deletion = True

    def edit(self):
        self.marked_for_edition = True


class StimuliList(QWidget):
    def __init__(self, stimuli_list, parent=None):
        super(StimuliList, self).__init__(parent)


class CreateProtocolWidget(QDialog):
    def __init__(self, parent=None):
        super(CreateProtocolWidget, self).__init__(parent)
        self.setWindowTitle('Crear protocolo')

        self.stimuli_list = []

        self.f_layout = QFormLayout()
        self.main_layout = QVBoxLayout()
        self.v_stimuli_layout = QVBoxLayout()
        self.buttons_layout = QHBoxLayout()

        self.protocol_name = QLineEdit()
        self.protocol_name.setPlaceholderText('Nombre del protocolo')
        self.protocol_notes = QTextEdit()
        self.protocol_notes.setMaximumHeight(50)
        self.protocol_distance = QSpinBox()
        self.protocol_distance.setRange(100, 5000)
        self.protocol_distance.setMaximumWidth(100)
        self.protocol_distance.setValue(400)
        self.protocol_distance.setSuffix(' mm')

        self.f_layout.addRow('Nombre', self.protocol_name)
        self.f_layout.addRow('Notas', self.protocol_notes)
        self.f_layout.addRow('Distancia', self.protocol_distance)

        self.add_stimulus_button = QPushButton(QIcon(join('icons', 'add.svg')), '')
        self.add_stimulus_button.clicked.connect(self.add_stimulus)
        self.save_button = QPushButton(QIcon(join('icons', 'save.svg')), '')
        self.save_button.clicked.connect(self.save_button_pressed)

        self.buttons_layout.addWidget(self.save_button)
        self.buttons_layout.addWidget(self.add_stimulus_button)

        self.main_layout.addLayout(self.f_layout)
        self.main_layout.addLayout(self.v_stimuli_layout)
        self.main_layout.addLayout(self.buttons_layout)

        self.setLayout(self.main_layout)

    @property
    def name(self):
        return self.protocol_name.text()

    @property
    def notes(self):
        return self.protocol_notes.toPlainText()

    @property
    def distance(self):
        return self.protocol_distance.value()

    def save_button_pressed(self):
        if not self.protocol_is_valid():
            return
        msgbox = QMessageBox(QMessageBox.Question, 'Guardar protocolo', "Una vez guardado, el protocolo "
                                                                        "no podrá ser modificado.", parent=self)
        msgbox.setInformativeText("¿Desea guardar el protocolo?")
        save = QPushButton('Guardar')
        msgbox.addButton(save, QMessageBox.AcceptRole)
        msgbox.addButton(QPushButton('Cancelar'), QMessageBox.RejectRole)
        msgbox.setDefaultButton(save)
        msgbox.setParent(self)

        if msgbox.exec_() == QMessageBox.RejectRole:
            return

        protocol = Protocol(self.name, self.notes, self.distance)
        protocol.stimuli = self.stimuli_list
        ind = ProtocolsDBIndex()
        ind.add_protocol(protocol)

        self.accept()

    def delete_stimulus(self):
        for i in range(self.v_stimuli_layout.count()):
            widget = self.v_stimuli_layout.itemAt(i).widget()
            if widget.marked_for_deletion:
                index = self.v_stimuli_layout.indexOf(widget)
                self.stimuli_list.pop(index)
                widget.setParent(None)
                break

    def edit_stimulus(self):
        index = -1
        for i in range(self.v_stimuli_layout.count()):
            widget = self.v_stimuli_layout.itemAt(i).widget()
            if widget.marked_for_edition:
                index = self.v_stimuli_layout.indexOf(widget)
                widget.marked_for_edition = False
                break

        edit_stimulus = CreateStimuliWidget(self)
        edit_stimulus.setWindowTitle('Editar estímulo')
        stimulus = self.stimuli_list[index]
        stimulus_type = 0
        if type(stimulus) is PursuitStimulus:
            stimulus_type = 1

        edit_stimulus.generic.type.setCurrentIndex(stimulus_type)
        edit_stimulus.generic.stimulus_name.setText(stimulus.name)
        edit_stimulus.generic.vertical_channel.setChecked(True)
        edit_stimulus.generic.horizontal_channel.setChecked(True)
        if stimulus.channel == Channel.Horizontal_Channel:
            edit_stimulus.generic.vertical_channel.setChecked(False)
        elif stimulus.channel == Channel.Vertical_Channel:
            edit_stimulus.generic.horizontal_channel.setChecked(False)
        edit_stimulus.generic.stimulus_duration.setValue(stimulus.duration)

        if type(stimulus) is SaccadicStimulus:
            edit_stimulus.saccadic_features.fixation_duration.setValue(stimulus.fixation_duration)
            edit_stimulus.saccadic_features.fixation_amplitude.setValue(stimulus.amplitude)
            edit_stimulus.saccadic_features.fixation_variation.setValue(stimulus.variation)
        else:
            edit_stimulus.pursuit_features.pursuit_amplitude.setValue(stimulus.amplitude)
            edit_stimulus.pursuit_features.pursuit_velocity.setValue(stimulus.velocity)

        if edit_stimulus.exec() == QDialog.Accepted:
            self.stimuli_list[index] = edit_stimulus.stimulus
            widget.stimulus_name.setText(edit_stimulus.stimulus.name)
            if type(edit_stimulus.stimulus) == SaccadicStimulus:
                widget.stimulus_type.setText('Estímulo Sacádico')
            else:
                widget.stimulus_type.setText('Estímulo de Persecución')

    def add_stimulus(self):
        create_stimulus = CreateStimuliWidget(parent=self)

        if create_stimulus.exec() == QDialog.Accepted:
            self.stimuli_list.append(create_stimulus.stimulus)
            stimulus_widget = StimulusWidget(create_stimulus.stimulus)
            self.v_stimuli_layout.addWidget(stimulus_widget)
            stimulus_widget.delete_stimulus.clicked.connect(self.delete_stimulus)
            stimulus_widget.edit_stimulus.clicked.connect(self.edit_stimulus)

    def protocol_is_valid(self) -> bool:
        messages = []
        if self.name == '' or self.name.isspace():
            messages.append('No se ha especificado un nombre válido')
        else:
            for s in self.name.split(' '):
                if not s == '' and not s.isalnum():
                    messages.append('No se ha especificado un nombre válido')
                    break

        if len(self.stimuli_list) == 0:
            if len(messages) == 0:
                messages.append('No se ha agregado ningún estímulo')
            else:
                messages.append('ni se ha agregado ningún estímulo')

        if self.name in ProtocolsDBIndex():
            QMessageBox.warning(self, 'Nombre incorrecto', 'Ya existe un protocolo con ese nombre. Debe '
                                                           'seleccionar otro.')
            return False
        if len(messages) == 0:
            return True
        else:
            s = 'Falta información:'
            for i in messages:
                s += '\n\t' + i
            QMessageBox.warning(self, "Datos insuficientes", s)
            return False


class ProtocolsListWidget(QListWidget):
    def __init__(self, parent=None):
        super(ProtocolsListWidget, self).__init__(parent)
        self.update_list()

    def update_list(self):
        self.clear()
        ind = ProtocolsDBIndex()
        for p in ind:
            notes = ind.get_protocol(p).notes
            lwi = QListWidgetItem()
            lwi.setText(p + "\t---\t" + notes)
            self.addItem(lwi)

    def selected(self) -> str:
        selected = self.selectedItems()
        if len(selected) == 0:
            QMessageBox.warning(self, "Error de selección",
                                "Debe seleccionar un protocolo.")
            return None
        name = selected[0].text().split('\t')[0]
        return name


class ProtocolsManagementDialog(QDialog):
    def __init__(self, parent=None):
        super(ProtocolsManagementDialog, self).__init__(parent)
        self.setWindowTitle('Gestión de Protocolos')

        self.main_layout = QVBoxLayout()
        self.protocols_layout = QVBoxLayout()
        self.buttons_layout = QHBoxLayout()

        self.label = QLabel('Protocolos\t\t\tNotas')

        self.protocols_list = ProtocolsListWidget()
        self.protocols_layout.addWidget(self.protocols_list)

        self.add_protocol_button = QPushButton()
        self.add_protocol_button.setIcon(QIcon(join('icons', 'add.svg')))
        self.add_protocol_button.setIconSize(QSize(20, 20))
        self.add_protocol_button.setToolTip('Agregar protocolo')
        self.add_protocol_button.clicked.connect(self.add_protocol)

        self.remove_protocol_button = QPushButton()
        self.remove_protocol_button.setIcon(QIcon(join('icons', 'delete.svg')))
        self.remove_protocol_button.setIconSize(QSize(20, 20))
        self.remove_protocol_button.setToolTip('Eliminar protocolo')
        self.remove_protocol_button.clicked.connect(self.remove_protocol)

        self.clone_protocol_button = QPushButton()
        self.clone_protocol_button.setIcon(QIcon(join('icons', 'clone.svg')))
        self.clone_protocol_button.setIconSize(QSize(20, 20))
        self.clone_protocol_button.setToolTip('Clonar protocolo')
        self.clone_protocol_button.clicked.connect(self.clone_protocol)

        self.buttons_layout.addWidget(self.add_protocol_button)
        self.buttons_layout.addWidget(self.remove_protocol_button)
        self.buttons_layout.addWidget(self.clone_protocol_button)

        self.main_layout.addWidget(self.label)
        self.main_layout.addLayout(self.protocols_layout)
        self.main_layout.addLayout(self.buttons_layout)
        self.setLayout(self.main_layout)

    def add_protocol(self):
        cpw = CreateProtocolWidget(self)
        cpw.exec()
        self.protocols_list.update_list()

    def remove_protocol(self):
        name = self.protocols_list.selected()
        if name is None:
            return

        msgbox = QMessageBox(QMessageBox.Question, 'Confirmación de eliminación',
                             'Está a punto de eliminar un prtocolo. Esta acción no puede deshacerse.', parent=self)
        msgbox.setInformativeText("¿Desea eliminar el protocolo?")
        save = QPushButton('Eliminar')
        msgbox.addButton(save, QMessageBox.AcceptRole)
        msgbox.addButton(QPushButton('Cancelar'), QMessageBox.RejectRole)
        msgbox.setDefaultButton(save)
        msgbox.setParent(self)

        if msgbox.exec_() == QMessageBox.RejectRole:
            return

        ind = ProtocolsDBIndex()
        ind.remove_protocol(name)
        self.protocols_list.update_list()

    def clone_protocol(self):
        name = self.protocols_list.selected()
        if name is None:
            return
        ind = ProtocolsDBIndex()
        protocol = ind.get_protocol(name)
        cpw = CreateProtocolWidget(self)
        cpw.setWindowTitle('Clonar protocolo')
        cpw.protocol_name.setText(protocol.name)
        cpw.protocol_notes.setText(protocol.notes)
        cpw.protocol_distance.setValue(protocol.distance)
        for stimulus in protocol.stimuli:
            cpw.stimuli_list.append(stimulus)
            stimulus_widget = StimulusWidget(stimulus)
            cpw.v_stimuli_layout.addWidget(stimulus_widget)
            stimulus_widget.delete_stimulus.clicked.connect(cpw.delete_stimulus)
            stimulus_widget.edit_stimulus.clicked.connect(cpw.edit_stimulus)

        cpw.exec_()
        self.protocols_list.update_list()


class TestControllerDialog(QDialog):
    def __init__(self, parent=None):
        super(TestControllerDialog, self).__init__(parent)
        self.setWindowTitle('Test Controller')

        self.main_layout = QVBoxLayout()
        self.buttons_layout = QHBoxLayout()

        self.label = QLabel('Protocolos\t\t\tNotas')
        self.protocols_list = ProtocolsListWidget()

        self.start_test_button = QPushButton('')
        self.start_test_button.setIcon(QIcon(join('icons', 'start.svg')))
        # self.start_test_button.setIconSize(QSize(20, 20))
        self.start_test_button.setToolTip('Comenzar a registrar una prueba')
        self.start_test_button.clicked.connect(self.start_test)

        self.buttons_layout.addWidget(self.start_test_button)
        self.main_layout.addWidget(self.label)
        self.main_layout.addWidget(self.protocols_list)
        self.main_layout.addLayout(self.buttons_layout)
        self.setLayout(self.main_layout)

        self.stimulator = None

    def start_test(self):
        name = self.protocols_list.selected()
        if name is None:
            return
        ind = ProtocolsDBIndex()
        protocol = ind.get_protocol(name)

        self.stimulator = StimulatorWidget(protocol)
        self.stimulator.show_stimulator()


class RepaintThread(QThread):
    paintStimulus = pyqtSignal()
    stopStimulus = pyqtSignal()

    def __init__(self, stimulus):
        QThread.__init__(self)
        self.stimulus = stimulus

    def run(self):
        # time = QTime()
        # time.start()
        while self.stimulus.duration > 0:
            self.paintStimulus.emit()
            delay = self.get_delay()
            # print("Time elapsed: %d ms" % time.elapsed())
            self.msleep(delay)
            # time.restart()
            self.stimulus.duration -= delay
        self.stopStimulus.emit()

    def get_delay(self):
        if type(self.stimulus) == SaccadicStimulus:
            real_duration = self.stimulus.fixation_duration + (random.randrange(
                self.stimulus.variation * 2)) - self.stimulus.variation
            return real_duration
        else:
            return 8


class StimulatorWidget(QWidget):
    def __init__(self, protocol: Protocol, parent=None):
        super(StimulatorWidget, self).__init__(parent)
        self.screen = QDesktopWidget().screenGeometry(1)
        self.move(self.screen.left(), self.screen.top())
        self.height = self.screen.height()
        self.width = self.screen.width()
        self.resize(self.screen.width(), self.screen.height())
        self.screen_2_height_mm = user_settings.value('screen_height', 0)
        self.screen_2_width_mm = user_settings.value('screen_width', 0)
        self.pixel_size = self.screen_2_width_mm / self.screen.width()
        self.protocol = protocol
        self.distance = self.protocol.distance

        self.stimulus = None
        self.sac_shift_factor = 1
        self.time_since_start = 0
        self.semi_length = 0
        self.thread = None
        self.should_paint = True
        self.previous_point = [0, 0]
        self.current_point = []

        sti = protocol.stimuli[0]
        self.stop_paint()

    def get_shift(self):
        if type(self.stimulus) == SaccadicStimulus:
            self.sac_shift_factor *= -1
            diff_sac = tan(radians(self.stimulus.amplitude)) * self.distance
            return diff_sac * self.sac_shift_factor
        else:
            time_for_round = self.stimulus.amplitude / (self.stimulus.velocity / 1000)
            # alpha = (self.current_stimulus.velocity / 1000) * (self.time_since_start % time_for_round)
            # if int(self.time_since_start / time_for_round) % 2 == 1:
            #     alpha = self.current_stimulus.amplitude - alpha
            # print(alpha)
            # diff = -self.distance * tan(radians(self.current_stimulus.amplitude / 2 - alpha))
            pixels = 2 * self.semi_length / self.pixel_size
            pixels_per_ms = pixels / time_for_round
            t = self.time_since_start % time_for_round
            diff = pixels_per_ms * t
            if int(self.time_since_start / time_for_round) % 2 == 1:
                diff -= pixels / 2
            else:
                diff = pixels / 2 - diff
            self.time_since_start += 8
            return diff

    def paintEvent(self, event):
        qp = QPainter(self)
        qp.fillRect(0, 0, self.screen.width(), self.screen.height(), QColor(255, 255, 255))
        qp.setPen(QColor(25, 25, 112))
        qp.setBrush(QBrush(QColor(25, 25, 112)))
        if self.should_paint:
            shift = self.get_shift()
            x = self.screen.width() / 2 - 15 + shift
            y = self.screen.height() / 2
            qp.drawEllipse(x, y, 30, 30)

            self.previous_point = self.current_point
            self.current_point = [x, y]

    def show_paint(self):
        self.update()
        # if type(self.stimulus) is SaccadicStimulus:
        #     self.update(self.previous_point[0] - 15, self.previous_point[1], 60, 32)
        # self.update(self.current_point[0] - 15, self.current_point[1], 60, 32)

    def stop_paint(self):
        self.should_paint = False
        self.update()
        if len(self.protocol.stimuli) > 0:
            # show dialog, delay
            QMessageBox.information(None, "Aviso",
                                    "Comenzar prueba")
            stimulus = self.protocol.stimuli[0]
            self.protocol.stimuli.remove(stimulus)
            self.paint_stimulus(stimulus)
        else:
            self.close()

    def paint_stimulus(self, stimulus: Stimulus):
        self.stimulus = stimulus
        self.stimulus.duration *= 1000
        self.sac_shift_factor = 1
        self.time_since_start = 0
        self.semi_length = tan(radians(self.stimulus.amplitude / 2)) * self.distance / 2

        self.thread = RepaintThread(self.stimulus)
        self.thread.start()
        self.thread.paintStimulus.connect(self.show_paint)
        self.thread.stopStimulus.connect(self.stop_paint)
        self.should_paint = True

        self.previous_point = [0, 0]
        self.current_point = [self.screen.width() / 2 - 15 + self.get_shift(), self.screen.height() / 2]

    def show_stimulator(self):
        if QDesktopWidget().numScreens() is 1:
            QMessageBox.warning(self, "Múltiples pantallas requeridas",
                                "Para ejecutar esta funcionalidad se necesita otro monitor. " +
                                "Conecte uno e intente de nuevo configurándolo como una pantalla extendida.")
        else:
            self.showFullScreen()


class WorkspaceSettingsWidget(QWidget):
    def __init__(self, parent=None):
        super(WorkspaceSettingsWidget, self).__init__(parent)
        self.workspace_path = QLineEdit(user_settings.value('workspace_path', dirname(__file__)))
        self.workspace_path.setReadOnly(True)

        self.search_path_button = QPushButton(QIcon(join('icons', 'select_path.svg')), "Seleccionar")
        self.search_path_button.clicked.connect(self._search_path)

        self.container_layout = QHBoxLayout()
        self.container_layout.addWidget(self.workspace_path)
        self.container_layout.addWidget(self.search_path_button)

        self.screen_height = QSpinBox()
        self.screen_height.setSuffix(" mm")
        self.screen_height.setMaximum(10000)
        self.screen_height.setValue(user_settings.value('screen_height', 0))

        self.screen_width = QSpinBox()
        self.screen_width.setSuffix(" mm")
        self.screen_width.setMaximum(10000)
        self.screen_width.setValue(user_settings.value('screen_width', 0))

        self.visualization_time_limit = QSpinBox()
        self.visualization_time_limit.setSuffix(" s")
        self.visualization_time_limit.setValue(user_settings.value('signals_renderer_time_limit', 10))

        serial_port_name = user_settings.value('serial_port', '')
        self.serial_port = QComboBox()

        for index, port in zip(range(256), SerialHelper.getAvailablePorts()):
            self.serial_port.addItem(port)

            if serial_port_name == port:
                self.serial_port.setCurrentIndex(index)

        self.main_layout = QFormLayout()
        self.main_layout.addRow("Largo del monitor:", self.screen_width)
        self.main_layout.addRow("Alto del monitor:", self.screen_height)
        self.main_layout.addRow("Ruta de trabajo:", self.container_layout)
        self.main_layout.addRow("Tiempo de muestra en pantalla:", self.visualization_time_limit)
        self.main_layout.addRow("Puerto serial:", self.serial_port)
        self.setLayout(self.main_layout)

    def _search_path(self):
        path = QFileDialog.getExistingDirectory(self, "Ruta de trabajo",
                                                user_settings.value('workspace_path', dirname(__file__)))

        if path:
            self.workspace_path.setText(path)

    def save(self):
        user_settings.setValue('workspace_path', self.workspace_path.text())
        user_settings.setValue('screen_height', self.screen_height.value())
        user_settings.setValue('screen_width', self.screen_width.value())
        user_settings.setValue('signals_renderer_time_limit', self.visualization_time_limit.value())
        user_settings.setValue('serial_port', self.serial_port.currentText())


class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super(SettingsDialog, self).__init__(parent)
        self.setWindowTitle('Configuración')
        self.setMinimumSize(400, 300)
        self.resize(600, 450)

        self.contents_widget = QListWidget()
        self.contents_widget.setViewMode(QListWidget.IconMode)
        self.contents_widget.setIconSize(QSize(80, 80))
        self.contents_widget.setMovement(QListWidget.Static)
        self.contents_widget.setMaximumWidth(120)
        self.contents_widget.setMinimumWidth(120)
        self.contents_widget.setSpacing(5)
        self.contents_widget.setCurrentRow(0)

        self.pages_widget = QStackedWidget()

        self._horizontal_layout = QHBoxLayout()
        self._horizontal_layout.addWidget(self.contents_widget)
        self._horizontal_layout.addSpacing(20)
        self._horizontal_layout.addWidget(self.pages_widget)

        self._button_box = QDialogButtonBox()
        self._button_box.addButton('Aceptar', QDialogButtonBox.AcceptRole)
        self._button_box.addButton('Cancelar', QDialogButtonBox.RejectRole)

        self._button_box.accepted.connect(self.accepted)
        self._button_box.rejected.connect(self.reject)

        self._main_layout = QVBoxLayout()
        self._main_layout.addLayout(self._horizontal_layout)
        self._main_layout.addWidget(self._button_box)

        self.setLayout(self._main_layout)

        self.add_item("Entorno de trabajo", QIcon(join('icons', 'workspace.svg')), WorkspaceSettingsWidget())

    def accepted(self):
        for i in range(self.pages_widget.count()):
            self.pages_widget.widget(i).save()

        self.accept()

    def _change_page(self, current):
        index = self.contents_widget.row(current)
        self.pages_widget.setCurrentIndex(index)

    def add_item(self, text, icon, widget):
        button = QListWidgetItem(self.contents_widget)
        button.setText(text)
        button.setIcon(icon)
        button.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
        button.setTextAlignment(Qt.AlignHCenter)

        self.contents_widget.currentItemChanged.connect(self._change_page)
        self.pages_widget.addWidget(widget)


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.showMaximized()
        self.setWindowTitle('NSNyst Controller')

        self.tool_bar = QToolBar()
        self.tool_bar.setIconSize(QSize(48, 48))

        self.protocols_management = ProtocolsManagementDialog(self)
        self.protocols_action = QAction(QIcon(join('icons', 'protocols.svg')), 'Gestionar protocolos', self.tool_bar)
        self.protocols_action.triggered.connect(self.protocols_management.exec)
        self.tool_bar.addAction(self.protocols_action)

        self.settings_dialog = SettingsDialog()
        self.settings_action = QAction(QIcon(join('icons', 'settings.svg')), 'Configuración', self.tool_bar)
        self.settings_action.triggered.connect(self.settings_dialog.exec)
        self.tool_bar.addAction(self.settings_action)

        self.test_controller = TestControllerDialog(self)
        self.test_controller_action = QAction(QIcon(join('icons', 'start.svg')), 'Test controller', self.tool_bar)
        self.test_controller_action.triggered.connect(self.test_controller.exec)
        self.tool_bar.addAction(self.test_controller_action)

        self.addToolBar(self.tool_bar)

        serial_port = user_settings.value('serial_port', '')
        visualization_time_limit = user_settings.value('signals_renderer_time_limit', 10)

        self.central_widget = QWidget()
        self.central_widget_layout = QVBoxLayout()
        self.central_widget.setLayout(self.central_widget_layout)

        self.signals_renderer = SignalsRenderer(parent=self, timeLimit=visualization_time_limit)
        self.central_widget_layout.addWidget(self.signals_renderer)

        self.button_list_widget = QWidget()
        self.button_list_layout = QHBoxLayout()
        self.button_list_widget.setLayout(self.button_list_layout)
        self.button_list_widget.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)

        self.renderer_time_decrease_button = QPushButton()
        self.renderer_time_decrease_button.setIcon(fa.icon('fa.minus'))
        self.renderer_time_decrease_button.clicked.connect(self.renderer_time_decrease)

        self.renderer_time_increase_button = QPushButton()
        self.renderer_time_increase_button.setIcon(fa.icon('fa.plus'))
        self.renderer_time_increase_button.clicked.connect(self.renderer_time_increase)

        self.button_list_layout.addStretch()
        self.button_list_layout.addWidget(self.renderer_time_decrease_button)
        self.button_list_layout.addWidget(self.renderer_time_increase_button)

        self.central_widget_layout.addWidget(self.button_list_widget)

        self.setCentralWidget(self.central_widget)

        self.adquirer = Adquirer(port=serial_port, timelimit=115)
        self.adquirer.read_data.connect(self.signals_renderer.addSamples)
        self.adquirer.start()

    def closeEvent(self, *args, **kwargs):
        self.adquirer.stop()

    def renderer_time_decrease(self):
        if self.signals_renderer.timeLimit > 5:
            self.signals_renderer.timeLimit -= 5

    def renderer_time_increase(self):
        self.signals_renderer.timeLimit += 5
