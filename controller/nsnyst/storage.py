from numpy import array, float64
from datetime import date
import json
from os.path import dirname, join
from os import makedirs, remove, rmdir
from core import user_settings
import pickle
from stimulation import StimulusType, Protocol, SaccadicStimulus, PursuitStimulus, Channel
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
            self.channels = {}
        else:
            self.channels = channels

    def __setitem__(self, key, value):
        if type(key) is str:
            if key == Test.HORIZONTAL_CHANNEL or key == Test.VERTICAL_CHANNEL or key == Test.STIMULUS_CHANNEL:
                self.channels[key] = array(value, float64)
            else:
                raise KeyError('El canal especificado no es válido')

    def __getitem__(self, item):
        if type(item) is str and item in self.channels:
            return self.channels[item]
        else:
            raise KeyError('La prueba no contiene el canal especificado')


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
            raise KeyError('No se encuentra el protocolo especificado.')
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
