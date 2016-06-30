from os.path import dirname
from math import tan, atan, degrees, atan2, radians
import random

from PyQt4.QtGui import QMainWindow, QToolBar, QDialog, QAction, QFormLayout, QLineEdit, QCheckBox, QSpinBox, QComboBox, \
    QStackedWidget, QWidget, QLabel, QPushButton, QHBoxLayout, QTextEdit, QVBoxLayout, QDesktopWidget, QMessageBox, \
    QListWidget, QDialogButtonBox, QListWidgetItem, QDesktopWidget, QMessageBox, QPainter, QColor, \
    QBrush, QFileDialog
from PyQt4.QtCore import QSize, Qt, QPointF, QThread, pyqtSignal, QTime
import artwork.icons as fa

from stimulation import Channel, SaccadicStimulus, PursuitStimulus, Protocol, StimulusType
from core import user_settings
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
        self.pursuit_velocity = QSpinBox()
        self.pursuit_velocity.setMaximumWidth(100)

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
        self.fixation_duration.setMaximumWidth(100)
        self.fixation_amplitude = QSpinBox()
        self.fixation_amplitude.setMaximumWidth(100)
        self.fixation_variation = QSpinBox()
        self.fixation_variation.setMaximumWidth(100)

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

        self.button_box.addButton('', QDialogButtonBox.AcceptRole).setIcon(fa.icon('fa.save'))
        self.button_box.addButton('', QDialogButtonBox.RejectRole).setIcon(fa.icon('fa.remove'))

        self.main_layout.addLayout(self.h_layout)
        self.main_layout.addWidget(self.button_box)

        self.setLayout(self.main_layout)

        self.generic.type.currentIndexChanged.connect(self.on_index_change)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

    def accept(self):
        super(CreateStimuliWidget, self).accept()

        name = self.generic.name
        duration = self.generic.duration
        channel = self.generic.channels
        if channel is None:
            channel = Channel.Both_Channels

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

    def on_index_change(self):
        self.advanced_properties_stack.setCurrentIndex(self.generic.type.currentIndex())
        self.stimulus_type = StimulusType(self.generic.type.currentIndex())


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
        self.protocol_notes = QTextEdit()
        self.protocol_notes.setMaximumHeight(50)
        self.protocol_distance = QSpinBox()
        self.protocol_distance.setRange(100, 5000)
        self.protocol_distance.setValue(400)

        self.f_layout.addRow('Nombre', self.protocol_name)
        self.f_layout.addRow('Notas', self.protocol_notes)
        self.f_layout.addRow('Distancia', self.protocol_distance)

        self.add_stimulus_button = QPushButton(fa.icon('fa.plus'), '')
        self.add_stimulus_button.clicked.connect(self.add_stimulus)
        self.save_button = QPushButton(fa.icon('fa.save'), '')
        self.save_button.clicked.connect(self.accepted)

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

    def accepted(self):
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

        edit_stimulus = CreateStimuliWidget()
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
        create_stimulus = CreateStimuliWidget()

        if create_stimulus.exec() == QDialog.Accepted:
            self.stimuli_list.append(create_stimulus.stimulus)
            stimulus_widget = StimulusWidget(create_stimulus.stimulus)
            self.v_stimuli_layout.addWidget(stimulus_widget)
            stimulus_widget.delete_stimulus.clicked.connect(self.delete_stimulus)
            stimulus_widget.edit_stimulus.clicked.connect(self.edit_stimulus)


class ProtocolsManagement(QDialog):
    def __init__(self, parent=None):
        super(ProtocolsManagement, self).__init__(parent)
        self.setWindowTitle('Gestión de Protocolos')

        self.main_layout = QVBoxLayout()
        self.protocols_layout = QVBoxLayout()
        self.buttons_layout = QHBoxLayout()

        self.label = QLabel('Protocolos\t\t\tNotas')

        self.protocols_list = QListWidget()
        self.update_list()
        self.protocols_layout.addWidget(self.protocols_list)

        self.add_protocol_button = QPushButton('+')
        self.add_protocol_button.clicked.connect(self.add_protocol)
        self.remove_protocol_button = QPushButton('-')
        self.remove_protocol_button.clicked.connect(self.remove_protocol)
        self.start_test_button = QPushButton('Start test')
        self.start_test_button.clicked.connect(self.start_test)
        self.buttons_layout.addWidget(self.add_protocol_button)
        self.buttons_layout.addWidget(self.remove_protocol_button)
        self.buttons_layout.addWidget(self.start_test_button)

        self.main_layout.addWidget(self.label)
        self.main_layout.addLayout(self.protocols_layout)
        self.main_layout.addLayout(self.buttons_layout)
        self.setLayout(self.main_layout)

        self.stimulator = None

    def start_test(self):
        selected = self.protocols_list.selectedItems()
        if len(selected) == 0:
            QMessageBox.warning(self, "Error de selección",
                                "Debe seleccionar un protocolo.")
            return
        name = selected[0].text().split('\t')[0]
        ind = ProtocolsDBIndex()
        protocol = ind.get_protocol(name)

        self.stimulator = StimulatorWidget(protocol.stimuli[0], protocol.distance)
        self.stimulator.show_stimulator()

        # for stimulus in protocol.stimuli:
        #     stimulator = StimulatorWidget(stimulus, protocol.distance)
        #     stimulator.show_stimulator()

    def add_protocol(self):
        cpw = CreateProtocolWidget(self)
        cpw.exec()
        self.update_list()

    def remove_protocol(self):
        selected = self.protocols_list.selectedItems()
        if len(selected) == 0:
            QMessageBox.warning(self, "Error de selección",
                                "Debe seleccionar un protocolo.")
            return
        name = selected[0].text().split('\t')[0]
        ind = ProtocolsDBIndex()
        ind.remove_protocol(name)
        self.update_list()

    def update_list(self):
        self.protocols_list.clear()
        ind = ProtocolsDBIndex()
        for p in ind:
            notes = ind.get_protocol(p).notes
            lwi = QListWidgetItem()
            lwi.setText(p + "\t---\t" + notes)
            self.protocols_list.addItem(lwi)


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
    def __init__(self, stimulus=None, distance=None, parent=None):
        super(StimulatorWidget, self).__init__(parent)
        if stimulus is None:
            return
        self.screen = QDesktopWidget().screenGeometry(1)
        self.move(self.screen.left(), self.screen.top())
        self.height = self.screen.height()
        self.width = self.screen.width()
        self.resize(self.screen.width(), self.screen.height())
        self.screen_2_height_mm = user_settings.value('screen_height', 0)
        self.screen_2_width_mm = user_settings.value('screen_width', 0)
        # stimuli_test = SaccadicStimulus('Sacádica 30', 20000, 60, 20, 1000)
        # stimuli_test2 = PursuitStimulus('Persecución 60', 10000, 45, 30)
        self.stimulus = stimulus
        self.stimulus.duration *= 1000
        # self.protocol = Protocol('Protocolo de Prueba', 'Este es un protocolo para probar el estímulo', 300)
        # self.protocol.add_stimulus(self.stimulus)
        self.pixel_size = self.screen_2_width_mm / self.screen.width()
        self.sac_shift_factor = 1
        # print(tan(radians(stimuli_test.amplitude/2)) * self.protocol.distance)
        self.time_since_start = 0
        self.distance = distance
        self.semi_length = tan(radians(self.stimulus.amplitude / 2)) * self.distance / 2

        self.thread = RepaintThread(self.stimulus)
        self.thread.start()
        self.thread.paintStimulus.connect(self.show_paint)
        self.thread.stopStimulus.connect(self.stop_paint)
        self.should_paint = True

        self.previous_point = [0, 0]
        self.current_point = [self.screen.width() / 2 - 15 + self.get_shift(), self.screen.height() / 2]

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
        self.close()

    def paint_stimuli(self, protocol):
        pass

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

        self.search_path_button = QPushButton("Seleccionar")
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

        self.main_layout = QFormLayout()
        self.main_layout.addRow("Largo del monitor:", self.screen_width)
        self.main_layout.addRow("Alto del monitor:", self.screen_height)
        self.main_layout.addRow("Ruta de trabajo:", self.container_layout)
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

        self.add_item("Entorno de trabajo", fa.icon('fa.folder'), WorkspaceSettingsWidget())

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
        self.protocols_management = ProtocolsManagement(self)
        # self.stimulator = StimulatorWidget()
        # self.stimulator.show_stimulator()

        # r = Record('Rec_name', 'protocol')
        # s = Record('another rec', 'prot name')
        # t = Test()
        # u = Test()
        # t[Test.HORIZONTAL_CHANNEL] = [1, 2, 3, 4]
        # u[Test.VERTICAL_CHANNEL] = [4.0, 2, 3, 4]
        # r.add_test(t)
        # s.add_test(u)
        # db = RecordsDBIndex()
        # db.add_record(r)
        # db.add_record(s)
        # db.write_to_json()
        # db = None
        # db_loaded = RecordsDBIndex()
        # for r in db_loaded:
        #     # print("\nRecord: ", r.name, ' ********* ', len(r.tests_names), ' tests.')
        #     for test_name in r:
        #         te = r.get_test(test_name)
        #         # print(te.channels, te.test_type.name)

        self.tool_bar = QToolBar()
        self.tool_bar.setIconSize(QSize(48, 48))

        fa_icon = fa.icon('fa.television')
        self.add_stimuli_action = QAction(fa_icon, 'Gestionar protocolos', self.tool_bar)
        self.add_stimuli_action.triggered.connect(self.protocols_management.exec)
        self.tool_bar.addAction(self.add_stimuli_action)

        self.settings_dialog = SettingsDialog()
        self.settings_action = QAction(fa.icon('fa.cog'), 'Configuración', self.tool_bar)
        self.settings_action.triggered.connect(self.settings_dialog.exec)
        self.tool_bar.addAction(self.settings_action)

        self.addToolBar(self.tool_bar)

    # def closeEvent(self, *args, **kwargs):
    #     self.stimulator.close()
