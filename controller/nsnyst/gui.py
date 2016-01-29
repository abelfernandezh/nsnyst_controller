from os.path import dirname
from math import tan, atan, degrees, atan2, radians
import random

from PyQt4.QtGui import QMainWindow, QToolBar, QDialog, QAction, QFormLayout, QLineEdit, QCheckBox, QSpinBox, QComboBox, \
    QStackedWidget, QWidget, QLabel, QPushButton, QHBoxLayout, QTextEdit
from PyQt4.QtCore import QSize
import artwork.icons as fa
from stimulation import Channel, SaccadicStimulus, Protocol

from nsnyst.stimulation import Channel, SaccadicStimulus, Protocol
from nsnyst.core import user_settings


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
        self.saccadic_amplitude = QLineEdit()
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
        self.stimulus = None
        self.generic = GenericParametersWidget()
        self.fixation_features = FixationStimuliParametersWidget()
        self.saccadic_features = SaccadicStimuliParametersWidget()
        self.stimulus_type = StimulusType.Saccadic

        self.setMinimumWidth(400)

        self.h_layout = QHBoxLayout()
        self.main_layout = QVBoxLayout()

        self.advanced_properties_stack = QStackedWidget()
        self.advanced_properties_stack.addWidget(self.saccadic_features)
        self.advanced_properties_stack.addWidget(self.fixation_features)

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

        name = self.generic.stimulus_name.text()
        print('duration' + str(self.generic.stimulus_duration))
        duration = self.generic.stimulus_duration.value()
        channel = 0
        h = self.generic.horizontal_channel.isChecked()
        v = self.generic.vertical_channel.isChecked()
        if not h and v:
            channel = Channel.Vertical_Channel
        if not v and h:
            channel = Channel.Horizontal_Channel

        if self.stimulus_type == StimulusType.Fixation:
            f_amplitude = self.fixation_features.fixation_amplitude.value()
            f_duration = self.fixation_features.fixation_duration.value()
            f_variation = self.fixation_features.fixation_variation.value()
            stimulus_data = FixationStimulus(name, duration, f_amplitude, f_duration, f_variation, channel)
        else:
            s_amplitude = self.saccadic_features.saccadic_amplitude.text()
            velocity = self.saccadic_features.saccadic_velocity.value()
            stimulus_data = SaccadicStimulus(name, duration, s_amplitude, velocity, channel)

        self.stimulus = stimulus_data
        if type(self.stimulus) is SaccadicStimulus:
            print(self.stimulus.name, self.stimulus.duration, self.stimulus.amplitude, self.stimulus.velocity, self.stimulus.channel)
        else:
            print(self.stimulus.name, self.stimulus.duration, self.stimulus.amplitude, self.stimulus.fixation_duration, self.stimulus.variation, self.stimulus.channel)

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
            self.stimulus_type.setText('Estímulo de Fijación')
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

        self.protocol_name = QLineEdit()
        self.protocol_notes = QTextEdit()
        self.protocol_notes.setMaximumHeight(50)

        self.f_layout.addRow('Nombre', self.protocol_name)
        self.f_layout.addRow('Notas', self.protocol_notes)

        self.add_stimulus_button = QPushButton(fa.icon('fa.plus'), '')
        self.add_stimulus_button.clicked.connect(self.add_stimulus)

        self.main_layout.addLayout(self.f_layout)
        self.main_layout.addLayout(self.v_stimuli_layout)
        self.main_layout.addWidget(self.add_stimulus_button)

        self.setLayout(self.main_layout)

    @property
    def name(self):
        return self.protocol_name.text()

    @property
    def notes(self):
        return self.protocol_notes.toPlainText()

    def save(self):
        pass

    def delete_stimulus(self):
        for i in range(self.v_stimuli_layout.count()):
            widget = self.v_stimuli_layout.itemAt(i).widget()
            if widget.marked_for_deletion:
                index = self.v_stimuli_layout.indexOf(widget)
                self.stimuli_list.pop(index)
                widget.setParent(None)
                break

    def edit_stimulus(self):
        self.index = -1
        for i in range(self.v_stimuli_layout.count()):
            widget = self.v_stimuli_layout.itemAt(i).widget()
            if widget.marked_for_edition:
                self.index = self.v_stimuli_layout.indexOf(widget)
                widget.marked_for_edition = False
                break

        edit_stimulus = CreateStimuliWidget()
        edit_stimulus.setWindowTitle('Editar estímulo')
        edit_stimulus

        stimulus = self.stimuli_list[self.index]
        stimulus_type = 0
        if type(stimulus) is FixationStimulus:
            stimulus_type = 1

        edit_stimulus.generic.type.setCurrentIndex(stimulus_type)
        edit_stimulus.generic.stimulus_name.setText(stimulus.name)
        edit_stimulus.generic.vertical_channel.setChecked(True)
        edit_stimulus.generic.horizontal_channel.setChecked(True)
        if stimulus.channel == Channel.Horizontal_Channel:
            edit_stimulus.generic.vertical_channel.setChecked(False)
        elif stimulus.channel == Channel.Vertical_Channel:
            edit_stimulus.generic.horizontal_channel.setChecked(False)
        edit_stimulus.generic.stimulus_duration = stimulus.duration

        if type(stimulus) is FixationStimulus:
            arg = stimulus.fixation_duration
            print('arg = ', str(arg))
            edit_stimulus.fixation_features.fixation_duration.setValue(arg)
            edit_stimulus.fixation_features.fixation_variation.setValue(stimulus.amplitude)
            edit_stimulus.fixation_features.fixation_variation.setValue(stimulus.variation)
        else:
            edit_stimulus.saccadic_features.saccadic_amplitude.setText(stimulus.amplitude)
            edit_stimulus.saccadic_features.saccadic_velocity.setValue(stimulus.velocity)

        if edit_stimulus.exec() == QDialog.Accepted:
            self.stimuli_list[self.index] = edit_stimulus.stimulus
            widget.separator = 'xcv'


    def add_stimulus(self):
        create_stimulus = CreateStimuliWidget()

        if create_stimulus.exec() == QDialog.Accepted:
            self.stimuli_list.append(create_stimulus.stimulus)
            stimulus_widget = StimulusWidget(create_stimulus.stimulus)
            self.v_stimuli_layout.addWidget(stimulus_widget)
            stimulus_widget.delete_stimulus.clicked.connect(self.delete_stimulus)
            stimulus_widget.edit_stimulus.clicked.connect(self.edit_stimulus)
            print(create_stimulus.saccadic_features.saccadic_velocity.value())


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
        stimuli_test = SaccadicStimulus('Sacádica 30', 20000, 60, 20, 3000)
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

        self.main_layout = QFormLayout()
        self.main_layout.addRow("Ruta de trabajo:", self.container_layout)
        self.setLayout(self.main_layout)

    def _search_path(self):
        path = QFileDialog.getExistingDirectory(self, "Workspace",
                                                user_settings.value('workspace_path', dirname(__file__)))

        if path:
            self.workspace_path.setText(path)

    def save(self):
        user_settings.setValue('workspace_path', self.workspace_path.text())


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
        self.contents_widget.setMaximumWidth(100)
        self.contents_widget.setMinimumWidth(100)
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

        self.add_item("Workspace", fa.icon('fa.folder'), WorkspaceSettingsWidget())

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
        self.create_protocol = CreateProtocolWidget()
        self.stimulator = StimulatorWidget(268, 476)
        self.stimulator.show_stimulator()
        self.tool_bar = QToolBar()
        self.tool_bar.setIconSize(QSize(48, 48))

        self.create_protocol = CreateProtocolWidget()

        fa_icon = fa.icon('fa.television')
        self.add_stimuli_action = QAction(fa_icon, 'Crear nuevo estímulo', self.tool_bar)
        self.add_stimuli_action.triggered.connect(self.create_protocol.exec)
        self.tool_bar.addAction(self.add_stimuli_action)

        self.settings_dialog = SettingsDialog()
        self.settings_action = QAction(fa.icon('fa.cog'), 'Configuración', self.tool_bar)
        self.settings_action.triggered.connect(self.settings_dialog.exec)
        self.tool_bar.addAction(self.settings_action)

        self.addToolBar(self.tool_bar)

    def closeEvent(self, *args, **kwargs):
        self.stimulator.close()
