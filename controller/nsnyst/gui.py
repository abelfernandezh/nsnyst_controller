from os.path import dirname

from PyQt4.QtGui import QMainWindow, QToolBar, QDialog, QAction, QFormLayout, QLineEdit, QCheckBox, QSpinBox, QComboBox, \
    QStackedWidget, QWidget, QLabel, QPushButton, QHBoxLayout, QTextEdit, QDialogButtonBox, QVBoxLayout, QListWidget,\
    QListWidgetItem, QFileDialog
from PyQt4.QtCore import QSize, Qt
import artwork.icons as fa
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
        protocol = Protocol('Prueba', 'Proasdad')
        protocol.add_stimulus(stimulus)
        protocol.save()
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
