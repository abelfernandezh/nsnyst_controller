from PyQt4.QtGui import QMainWindow, QToolBar, QDialog, QAction, QFormLayout, QLineEdit, QCheckBox, QSpinBox, QComboBox, \
    QStackedWidget, QWidget, QFrame, QSizePolicy, QPushButton
from PyQt4.QtCore import QSize
import controller.artwork.icons as fa


class CreateStimuliWidget(QDialog):
    def __init__(self, parent=None):
        super(QDialog, self).__init__(parent)
        self.setWindowTitle('Crear nuevo estímulo')

        self.setMinimumWidth(400)

        self.h_layout = QFormLayout()

        self.name_input = QLineEdit()
        self.h_layout.addRow('Nombre', self.name_input)
        self.horizontal_channel = QCheckBox()
        self.h_layout.addRow('Canal Horizontal', self.horizontal_channel)
        self.vertical_channel = QCheckBox()
        self.h_layout.addRow('Canal Vertical', self.vertical_channel)
        self.duration = QSpinBox()
        self.duration.setRange(1, 500)
        self.duration.setMaximumWidth(100)
        self.h_layout.addRow('Duración', self.duration)
        self.type = QComboBox()
        self.type.addItem('Prueba Sacádica')
        self.type.addItem('Prueba de Persecución')
        self.h_layout.addRow('Tipo de Prueba', self.type)

        self.saccadic_amplitude = QSpinBox()
        self.saccadic_amplitude.setMaximumWidth(100)
        self.saccadic_velocity = QSpinBox()
        self.saccadic_velocity.setMaximumWidth(100)

        self.saccadic_stack = QWidget()

        self.s_layout = QFormLayout()

        self.s_layout.addRow('Velocidad', self.saccadic_velocity)
        self.s_layout.addRow('Amplitud', self.saccadic_amplitude)

        self.saccadic_stack.setLayout(self.s_layout)

        self.fixation_stack = QWidget()
        self.f_layout = QFormLayout()

        self.fixation_duration = QSpinBox()
        self.fixation_duration.setMaximumWidth(100)
        self.fixation_amplitude = QSpinBox()
        self.fixation_amplitude.setMaximumWidth(100)
        self.fixation_variation = QSpinBox()
        self.fixation_variation.setMaximumWidth(100)

        self.f_layout.addRow('Duración', self.fixation_duration)
        self.f_layout.addRow('Amplitud', self.fixation_amplitude)
        self.f_layout.addRow('Variación', self.fixation_variation)

        self.fixation_stack.setLayout(self.f_layout)

        self.advanced_properties_stack = QStackedWidget()
        self.advanced_properties_stack.addWidget(self.saccadic_stack)
        self.advanced_properties_stack.addWidget(self.fixation_stack)

        self.h_line = QFrame()
        self.h_line.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.h_layout.addRow(self.h_line)

        self.h_layout.addRow('Detalles', self.advanced_properties_stack)
        self.advanced_properties_stack.setCurrentIndex(0)
        self.setLayout(self.h_layout)

        def save_stimuli(self):
            pass

        fa_save = fa.icon('fa.save')
        self.save_button = QPushButton(fa_save, 'Guardar')
        self.save_button.setMaximumWidth(100)
        self.h_layout.addRow(self.save_button)

        def on_index_change(self):
            self.advanced_properties_stack.setCurrentIndex(self.type.currentIndex())

        self.type.currentIndexChanged.connect(on_index_change)


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)

        self.showMaximized()
        self.setWindowTitle('NSNyst Controller')

        self.create_stimuli = CreateStimuliWidget()

        self.tool_bar = QToolBar()
        self.tool_bar.setIconSize(QSize(48, 48))

        fa_icon = fa.icon('fa.television')
        self.add_stimuli_action = QAction(fa_icon, 'Crear nuevo estímulo', self.tool_bar)
        self.add_stimuli_action.triggered.connect(self.create_stimuli.show)

        self.tool_bar.addAction(self.add_stimuli_action)

        self.addToolBar(self.tool_bar)
