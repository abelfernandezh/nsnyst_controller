from numpy import array, float64


class Test:
    pass


class ProtocolRecord:
    def __init__(self, name):
        self.name = name

    def to_json(self):
        pass


class ProtocolsDBIndex:
    def __init__(self, protocol_records):
        self.protocol_records = protocol_records


class RecordsDBIndex:
    records = []

    def __init__(self, records: Record):
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

    def __init__(self, record_name, protocol_name, date, tests: Test):
        self.record_name = record_name
        self.protocol_name = protocol_name
        self.date = date
        self.tests = tests

    def to_json(self) -> object:
        pass

    def get_test(self, index) -> Test:
        pass

    def add_test(self, test):
        pass

    def remove_test(self, index):
        pass
