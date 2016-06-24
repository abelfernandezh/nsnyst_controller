from numpy import array, float64
from datetime import date
import json
from os.path import dirname, join
from os import makedirs, remove, rmdir
from core import user_settings
import pickle
from stimulation import StimulusType


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


class ProtocolRecord:
    def __init__(self, name):
        self.name = name

    def to_json(self) -> str:
        return json.dumps(self.information, indent=4)

    @property
    def information(self):
        info = {'name': self.name}
        return info


class ProtocolsDBIndex:
    def __init__(self, protocol_records):
        self.protocol_records = protocol_records


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
        record = {
            'record_name': self.record_name,
            'protocol_name': self.protocol_name,
            'date': self.date.toordinal(),
            'tests_names': self.tests_names
        }
        return record

    def dumps(self) -> str:
        return json.dumps(self.information, indent=4)

    def loads(self, s: str):
        info = json.loads(s)
        self.record_name = info['record_name']
        self.protocol_name = info['protocol_name']
        self.date = date.fromordinal(info['date'])
        self.tests_names = info['tests_names']

    def get_test(self, index) -> Test:
        path = self.get_path
        filename = self.tests_names[index]
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


class RecordsDBIndex:
    records = []

    def __init__(self, records: list=None):
        if records is None:
            self.records = []
        else:
            self.records = records

    def get_record(self, index) -> Record:
        return self.records[index]

    def add_record(self, record: Record):
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
        with open(join(path, 'RecordsDbIndex.json'), 'r') as ifile:
            info = json.load(ifile)
        for i in info:
            r = Record()
            r.loads(i)
            self.records.append(r)

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


