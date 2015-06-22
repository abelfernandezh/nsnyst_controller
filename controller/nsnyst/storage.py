from numpy import array, float64
from datetime import date
import json


class Test:
    HORIZONTAL_CHANNEL = 'HorizontalChannel'
    VERTICAL_CHANNEL = 'VerticalChannel'
    STIMULUS_CHANNEL = 'StimulusChannel'

    oid = None
    channels = None

    def __init__(self, channels: dict=None, oid: int=-1):
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

    def dumps(self) -> str:
        return json.dumps(self.information, indent=4)

    def loads(self, s: str):
        info = json.loads(s)
        self.oid = info['oid']
        channels = info['channels']
        for k in channels.keys():
            self.channels[k] = array(channels[k], float64)

    @property
    def information(self):
        channels = {}
        for k in self.channels.keys():
            channels[k] = (self.channels[k]).tolist()
        info = {'oid': self.oid, 'channels': channels}
        return info


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


class RecordsDBIndex:
    records = []

    def __init__(self, records: list=None):
        self.records = records

    def to_json(self):
        pass

    def add_record(self, record):
        pass

    def remove_record(self, index):
        pass

    def write_to_file(self):
        pass


class Record:
    tests = []

    def __init__(self, record_name: str='', protocol_name: str='', tests: list=[], record_date: date=date.today()):
        self.record_name = record_name
        self.protocol_name = protocol_name
        self.date = record_date
        self.tests = tests

    @property
    def information(self):
        record = {
            'record_name': self.record_name,
            'protocol_name': self.protocol_name,
            'date': self.date.toordinal(),
            'tests': []
        }
        tests = []
        for t in self.tests:
            tests.append(t.dumps())
        record['tests'] = tests
        return record

    def dumps(self) -> str:
        return json.dumps(self.information, indent=4)

    def loads(self, s: str):
        info = json.loads(s)
        self.record_name = info['record_name']
        self.protocol_name = info['protocol_name']
        self.date = date.fromordinal(info['date'])
        tests = info['tests']
        for t in tests:
            test = Test()
            test.loads(t)
            self.tests.append(test)

    def get_test(self, index) -> Test:
        pass

    def add_test(self, test):
        pass

    def remove_test(self, index):
        pass
