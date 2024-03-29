""" nsnyst.adquisition

This module is in charge of the communications with the amplifier device.
"""

__author__ = 'Carlos Cano Domingo <carcandom@uma.es>'

from numpy import zeros, int16, ndarray
from multiprocessing import Queue
from serial import Serial
from serial.tools import list_ports
from time import sleep
from PyQt4.QtCore import QThread, pyqtSignal


class Adquirer(QThread):
    """ Signal acquisition from the amplifier
    """
    read_data = pyqtSignal(ndarray)

    ADC_START_COMMAND = b'S'
    ADC_STOP_COMMAND = b'F'
    ADC_TIMEOUT = 0.02

    SERIAL_BAUDRATE = 115200
    SERIAL_TIMEOUT = 1000

    RECORDER_BLOCKSIZE = 20
    RECORDER_STOP_COMMAND = 2

    OK_EXIT_CODE = 0
    STOPPED_EXIT_CODE = 1
    PORT_NOT_OPENED_EXIT_CODE = 2
    READ_ERROR_EXIT_CODE = 3

    def __init__(self, port: str, blockcount: int = 1, timelimit: int = 5):
        """ Constructor

        :port: Input device port
        :blockcount: Number of blocks in the buffer
        :timelimit: Acquisition length in seconds

        Buffer length is defined by the value of blockcount * RECORDER_BLOCKSIZE.
        """
        super(Adquirer, self).__init__()
        self.q = Queue()
        self.port = port
        self.data = zeros([blockcount * Adquirer.RECORDER_BLOCKSIZE, 2], dtype=int16)
        self.blockcount = blockcount
        self.countlimit = timelimit / Adquirer.ADC_TIMEOUT
        self.total = 0
        self.num = 50
        self.exit_code = Adquirer.OK_EXIT_CODE

    def stop(self):
        """ Stop adquisition
        """
        self.q.put(Adquirer.RECORDER_STOP_COMMAND)

    def run(self):
        """ Start adquisition
        """
        self.exit_code = Adquirer.OK_EXIT_CODE
        serial = Serial(self.port,
                        baudrate=Adquirer.SERIAL_BAUDRATE,
                        timeout=Adquirer.SERIAL_TIMEOUT)

        if serial.isOpen():
            sleep(1)
            serial.flush()
            serial.write(Adquirer.ADC_START_COMMAND)

            current = 0

            while True:
                dat = serial.read(60)
                if not len(dat) == 60:
                    self.exit_code = Adquirer.READ_ERROR_EXIT_CODE
                    break

                if not self.q.empty():
                    if self.q.get() == Adquirer.RECORDER_STOP_COMMAND:
                        self.exit_code = Adquirer.STOPPED_EXIT_CODE
                        break

                self.total += 1

                for i in range(0, len(dat), 3):
                    c1 = (dat[i] << 4) | ((dat[i + 1] & 0xF0) >> 4)
                    c0 = (((dat[i + 1]) & 0xF) << 8) | (dat[i + 2])
                    self.data[current][0] = c0
                    self.data[current][1] = c1
                    current += 1

                if current == self.blockcount * Adquirer.RECORDER_BLOCKSIZE:
                    self.read_data.emit(self.data)
                    current = 0

                if self.total == self.countlimit:
                    break

            serial.write(Adquirer.ADC_STOP_COMMAND)
            serial.close()

        else:
            self.exit_code = Adquirer.PORT_NOT_OPENED_EXIT_CODE

        if self.exit_code == Adquirer.READ_ERROR_EXIT_CODE:
            raise Exception('Adquirer read error')

        if self.exit_code == Adquirer.PORT_NOT_OPENED_EXIT_CODE:
            raise Exception('Port not opened error')

    def was_recording_ok(self):
        """ Returns if the recording was successfull or not
        """
        return (self.exit_code == Adquirer.OK_EXIT_CODE) or (self.exit_code == Adquirer.STOPPED_EXIT_CODE)


class SerialHelper:

    @staticmethod
    def getAvailablePorts():
        ports = []
        for port in list_ports.comports():
            ports.append(port.device)

        return ports


if __name__ == "__main__":

    import sys
    from PyQt4.QtCore import QCoreApplication

    # Example block
    # f = open('data_out.txt', 'wt')

    def sample_handler(data):
        # print(len(data))
        for i in range(len(data)):
            print("%d %d" % (data[i][0], data[i][1]))
            # f.write('%d %d\n' % (data[i][0], data[i][1]))


    app = QCoreApplication(sys.argv)
    p = Adquirer(port='COM1', timelimit=4)
    p.read_data.connect(sample_handler)
    p.start()
    # p.wait()
    # f.close()
    app.exec_()
