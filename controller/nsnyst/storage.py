from numpy import array, int16, ndarray
from datetime import date, datetime
import json
from os.path import dirname, join
from os import makedirs, remove, rmdir
from PyQt4.QtCore import QThread
from nsnyst.core import user_settings
import pickle
from nsnyst.stimulation import StimulusType, Protocol, SaccadicStimulus, PursuitStimulus, Channel
from collections import OrderedDict


class Test:
    HORIZONTAL_CHANNEL = 'HorizontalChannel'
    VERTICAL_CHANNEL = 'VerticalChannel'
    STIMULUS_CHANNEL = 'StimulusChannel'

    oid = None
    test_type = None
    channels = None

    def __init__(self, test_type: StimulusType=StimulusType.Saccadic, channels: dict=None, oid: int=-1):
        self.test_type = test_type
        self.oid = oid
        if channels is None:
            self.channels = dict()
        else:
            self.channels = channels

    def __setitem__(self, key, value):
        if type(key) is str:
            if key == Test.HORIZONTAL_CHANNEL or key == Test.VERTICAL_CHANNEL or key == Test.STIMULUS_CHANNEL:
                if isinstance(value, list):
                    self.channels[key] = array(value, int16)
                elif isinstance(value, ndarray):
                    self.channels[key] = value
                else:
                    raise ValueError('El valor proporciondo no es válido')
            else:
                raise KeyError('El canal especificado no es válido')

    def __getitem__(self, item):
        if type(item) is str and item in self.channels:
            return self.channels[item]
        else:
            raise KeyError('La prueba no contiene el canal especificado')


class Subject(object):
    """ Sujeto

    Encapsula todos los datos de un sujeto al que se le realizan estudios de movimientos oculares.
    """

    UNKNOWN_GENDER = 0
    MALE_GENDER = 1
    FEMALE_GENDER = 2

    UNKNOWN_STATUS = 0
    CONTROL = 1
    PRESINTOMATIC = 2
    SICK = 3

    UNKNOWN_HANDEDNESS = 0
    RIGTH = 1
    LEFT = 2
    AMBIDEXTER = 3

    code = 0000
    parent = None
    first_name = None
    last_name = None
    gender = None
    status = None
    molecular_diagnose = None
    clinical_diagnose = None
    handedness = 0
    family = None
    generation = None
    register_date = None
    born_date = None
    comments = None
    updated = None

    def __init__(self, first_name: str = 'Unknown', last_name: str = 'Unknown',
                 oid: int = -1, parent=None, gender: int = UNKNOWN_GENDER,
                 status: int = UNKNOWN_STATUS, handedness: int = UNKNOWN_HANDEDNESS,
                 register_date: datetime = datetime.now(), info: dict=None,
                 **parameters):
        """Constructor

        :param oid:
        :param parent:
        :param first_name: Nombre del paciente
        :param last_name: Apellidos del paciente
        :param gender: Género del paciente
        :param status: Estado del paciente
        :param parameters: Parámetros adicionales del paciente
        """
        if info is not None:
            self.load(info)
            return
        self.code = oid
        self.parent = None
        self.first_name = first_name
        self.last_name = last_name
        self.gender = gender
        self.status = status
        self.molecular_diagnose = None
        self.clinical_diagnose = None
        self.handedness = handedness
        self.family = None
        self.generation = None
        self.register_date = register_date
        self.born_date = None
        self.comments = None
        self.updated = datetime.now()

    def __str__(self):
        return self.first_name

    @property
    def information(self) -> OrderedDict:
        info = OrderedDict()
        info['first_name'] = self.first_name
        info['last_name'] = self.last_name
        info['code'] = self.code
        info['gender'] = self.gender
        info['status'] = self.status
        info['molecular_diagnose'] = self.molecular_diagnose
        info['clinical_diagnose'] = self.clinical_diagnose
        info['handedness'] = self.handedness
        info['family'] = self.family
        info['generation'] = self.generation
        info['register_date'] = self.register_date.toordinal()
        info['born_date'] = self.born_date.toordinal()
        info['comments'] = self.comments
        if 'updated' in info.keys():
            info['updated'] = self.updated.toordinal()
        else:
            info['updated'] = datetime.now().toordinal()
        return info

    def load(self, info: dict):
        self.first_name = info['first_name']
        self.last_name = info['last_name']
        self.code = info['code']
        self.gender = info['gender']
        self.status = info['status']
        self.molecular_diagnose = info['molecular_diagnose']
        self.clinical_diagnose = info['clinical_diagnose']
        self.handedness = info['handedness']
        self.family = info['family']
        self.generation = info['generation']
        self.register_date = datetime.fromordinal(info['register_date'])
        self.born_date = datetime.fromordinal(info['born_date'])
        self.comments = info['comments']
        if 'updated' in info.keys():
            self.updated = datetime.fromordinal(info['updated'])
        else:
            self.updated = datetime.now()


class ProtocolsDBIndex:
    protocols_record = None

    def __init__(self, protocols_record: list=None):
        if protocols_record is None:
            if not self.load_from_json():
                self.protocols_record = []
        else:
            self.protocols_record = protocols_record

    def add_protocol(self, protocol: Protocol):
        if protocol.name not in self.protocols_record:
            self.protocols_record.append(protocol.name)
        path = user_settings.value('workspace_path', dirname(__file__))
        makedirs(join(path, 'ProtocolsDB'), exist_ok=True)
        with open(join(path, 'ProtocolsDB', protocol.name + '.json'), 'w') as ofile:
            json.dump(protocol.information, ofile, sort_keys=False, indent=4)
        self.write_to_json()

    def get_protocol(self, key) -> Protocol:
        if type(key) is int:
            filename = self.protocols_record[key]
        elif type(key) is str and key in self.protocols_record:
            filename = key
        else:
            raise KeyError('No se encuentra el protocolo especificado. key = (' + str(key) + ')')
        path = user_settings.value('workspace_path', dirname(__file__))
        with open(join(path, 'ProtocolsDB', filename + '.json'), 'r') as ifile:
            info = json.load(ifile)
        name = info['name']
        notes = info['notes']
        distance = info['distance']
        protocol = Protocol(name, notes, distance)
        for s in info['stimuli']:
            name = s[1]['name']
            duration = s[1]['duration']
            channel = Channel(s[1]['channel'])
            amplitude = s[1]['amplitude']
            if s[0] == StimulusType.Saccadic.name:
                fixation_duration = s[1]['fixation_duration']
                variation = s[1]['variation']
                stimulus = SaccadicStimulus(name, duration, amplitude, variation, fixation_duration, channel)
            elif s[0] == StimulusType.Pursuit.name:
                velocity = s[1]['velocity']
                stimulus = PursuitStimulus(name, duration, amplitude, velocity, channel)
            else:
                raise ImportError('Tipo de estímulo incorrecto! Error al cargar.')
            protocol.add_stimulus(stimulus)

        return protocol

    def remove_protocol(self, key):
        if type(key) is int:
            name = self.protocols_record[key]
        elif type(key) is str and key in self.protocols_record:
            name = key
        else:
            raise KeyError('No se encuentra el protocolo especificado.')
        path = user_settings.value('workspace_path', dirname(__file__))
        remove(join(path, 'ProtocolsDB', name + '.json'))
        self.protocols_record.remove(name)
        self.write_to_json()

    def edit_protocol(self, key):
        pass

    def write_to_json(self):
        path = user_settings.value('workspace_path', dirname(__file__))
        with open(join(path, 'ProtocolsDbIndex.json'), 'w') as ofile:
            json.dump(self.protocols_record, ofile, indent=4)

    def load_from_json(self) -> bool:
        path = user_settings.value('workspace_path', dirname(__file__))
        try:
            with open(join(path, 'ProtocolsDbIndex.json'), 'r') as ifile:
                self.protocols_record = json.load(ifile)
        except FileNotFoundError:
            return False
        return True

    def __iter__(self):
        return self.protocols_record.__iter__()

    def __contains__(self, item):
        return item in self.protocols_record

    def __len__(self):
        return len(self.protocols_record)


class Record:
    def __init__(self, record_name: str='', protocol_name: str='', tests_names: list=None,
                 record_date: date=date.today()):
        self.record_name = record_name
        self.protocol_name = protocol_name
        self.date = record_date
        if tests_names is None:
            self.tests_names = []
        else:
            self.tests_names = tests_names

    @property
    def information(self):
        record = OrderedDict()
        record['record_name'] = self.record_name
        record['protocol_name'] = self.protocol_name
        record['date'] = self.date.toordinal()
        record['tests_names'] = self.tests_names
        return record

    def dumps(self) -> str:
        return self.information

    def loads(self, info):
        self.record_name = info['record_name']
        self.protocol_name = info['protocol_name']
        self.date = date.fromordinal(info['date'])
        self.tests_names = info['tests_names']

    def get_test(self, key) -> Test:
        if type(key) is int:
            filename = self.tests_names[key]
        elif type(key) is str and key in self.tests_names:
            filename = key
        else:
            raise KeyError('No se encuentra el protocolo especificado.')
        path = self.get_path
        with open(join(path, filename), 'rb') as ifile:
            test = pickle.load(ifile)
            return test

    def set_subject(self, subject: Subject):
        path = self.get_path
        filename = join(path, 'RecordsDB', 'Registro-' + self.record_name + '_Protocolo-' + self.protocol_name)
        makedirs(filename, exist_ok=True)

        filename = join(filename, 'subject.json')
        with open(filename, 'w') as ofile:
            json.dump(subject.information, ofile, indent=4)

    def get_subject(self) -> Subject:
        path = self.get_path
        filename = join(path, 'RecordsDB', 'Registro-' + self.record_name + '_Protocolo-' + self.protocol_name,
                        'subject.json')
        with open(filename, 'r') as ifile:
            info = json.load(ifile)
        return Subject(info=info)

    def add_test(self, test: Test):
        test_name = str(len(self.tests_names)) + '_' + test.test_type.name + 'Test'  # !!! stName
        path = self.get_path
        filename = join('RecordsDB', 'Registro-' + self.record_name + '_Protocolo-' + self.protocol_name)
        makedirs(join(path, filename), exist_ok=True)
        filename = join(filename, test_name + '.test')
        with open(join(path, filename), 'wb') as ofile:
            pickle.dump(test, ofile, pickle.HIGHEST_PROTOCOL)

        self.tests_names.append(filename)

    def remove_test(self, index):
        remove(join(self.get_path, self.tests_names[index]))
        self.tests_names.remove(self.tests_names[index])

    def delete(self):
        for i in range(len(self.tests_names)):
            self.remove_test(i)
        path = self.get_path
        rmdir(join(path, 'RecordsDB', 'Registro-' + self.record_name + '_Protocolo-' + self.protocol_name))

    @property
    def get_path(self):
        """
        Devuelve la ruta de trabajo.
        """
        path = user_settings.value('workspace_path', dirname(__file__))
        return path

    @property
    def name(self):
        return self.record_name

    def __iter__(self):
        return self.tests_names.__iter__()

    def __len__(self):
        return len(self.tests_names)


class RecordsDBIndex:
    records = []

    def __init__(self, records: list=None):
        if records is None:
            if not self.load_from_json():
                self.records = []
        else:
            self.records = records

    def get_record(self, index) -> Record:
        return self.records[index]

    def add_record(self, record: Record):
        for rec in self.records:
            #
            if record.protocol_name == rec.protocol_name and record.record_name == rec.record_name:
                print("Registro preexistente. Ya existía una registro del mismo nombre para este protocolo. " +
                      "Sus pruebas se combinaron en el mismo directorio")
                # raise Warning("Registro preexistente. Ya existía una registro del mismo nombre para este protocolo."+
                #               "Sus pruebas se combinarán en el mismo directorio")
                record.tests_names.extend(rec.tests_names)
                rec.tests_names = list(sorted(set(record.tests_names)))
                rec.date = record.date
                self.write_to_json()
                return
        #
        self.records.append(record)
        self.write_to_json()

    def remove_record(self, index):
        self.records[index].delete()
        self.records.remove(self.records[index])
        self.write_to_json()

    def write_to_json(self):
        path = self.get_path
        with open(join(path, 'RecordsDbIndex.json'), 'w') as ofile:
            json.dump(self.information, ofile, indent=4)

    def load_from_json(self):
        path = self.get_path
        try:
            with open(join(path, 'RecordsDbIndex.json'), 'r') as ifile:
                info = json.load(ifile)
        except FileNotFoundError:
            return False

        self.records.clear()
        for i in info:
            r = Record()
            r.loads(i)
            self.records.append(r)
        return True

    @property
    def information(self):
        info = []
        for r in self.records:
            info.append(r.dumps())
        return info

    @property
    def get_path(self):
        path = user_settings.value('workspace_path', dirname(__file__))
        return path

    def __iter__(self):
        return self.records.__iter__()

    def __contains__(self, item):
        records_names = []
        for r in self.records:
            records_names.append(r.record_name)
        return item in records_names


class Storager(QThread):
    stimulus_channel = []
    horizontal_channel = []
    vertical_channel = []

    def __init__(self, record_name: str, protocol_name: str, subject: Subject, record_date: date=date.today()):
        super(Storager, self).__init__()

        self.record_name = record_name
        self.record_date = record_date
        ind = ProtocolsDBIndex()
        self.protocol = ind.get_protocol(protocol_name)
        self.subject = subject
        self.record = Record(record_name, protocol_name, record_date=record_date)

    def receive_data(self, block):
        for i in range(len(block)):
            self.horizontal_channel.append(block[i][0])
            self.vertical_channel.append(block[i][1])
            self.stimulus_channel.append(block[i][2])

    def on_stimulus_end(self):
        test_index = len(self.record)
        if type(self.protocol.stimuli[test_index]) == SaccadicStimulus:
            test_type = StimulusType.Saccadic
        else:
            test_type = StimulusType.Pursuit
        test = Test(test_type)
        test[Test.HORIZONTAL_CHANNEL] = self.horizontal_channel
        test[Test.VERTICAL_CHANNEL] = self.vertical_channel
        test[Test.STIMULUS_CHANNEL] = self.stimulus_channel
        self.horizontal_channel = []
        self.vertical_channel = []
        self.stimulus_channel = []
        self.record.add_test(test)

    def on_record_end(self):
        if len(self.record) == 0:
            return
        self.record.set_subject(self.subject)
        ind = RecordsDBIndex()
        ind.add_record(self.record)
        self.quit()
