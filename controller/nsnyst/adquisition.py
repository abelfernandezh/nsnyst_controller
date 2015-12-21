""" nsnyst.adquisition

This module is in charge of the communications with the amplifier device.
"""

__author__ = 'Carlos Cano Domingo <carcandom@uma.es>'

from numpy import zeros, int16
from multiprocessing import Queue, Process
from serial import Serial
from time import sleep


class Adquirer(Process):
    """ Signal acquisition from the amplifier
    """

    ADC_START_COMMAND = 'S'
    ADC_STOP_COMMAND = 'F'
    ADC_TIMEOUT = 0.02

    SERIAL_BAUDRATE = 115200
    SERIAL_TIMEOUT = 1000

    RECORDER_BLOCKSIZE = 20
    RECORDER_STOP_COMMAND = 2

    OK_EXIT_CODE = 0
    STOPPED_EXIT_CODE = 1
    PORT_NOT_OPENED_EXIT_CODE = 2
    READ_ERROR_EXIT_CODE = 3

    def __init__(self, port: str, handler: callable, blockcount:int=1, timelimit:int=5):
        """ Constructor

        :port: Input device port
        :handler: Data handler function
        :blockcount: Number of blocks in the buffer
        :timelimit: Acquisition length in seconds

        Buffer length is defined by the value of blockcount * RECORDER_BLOCKSIZE.
        """
        self.q = Queue()
        self.port = port
        self.handler = handler
        self.data = zeros([blockcount * Recorder.RECORDER_BLOCKSIZE, 2], dtype=int16)
        self.blockcount = blockcount
        self.countlimit = timelimit / Recorder.ADC_TIMEOUT
        self.total = 0
        self.num = 50
        self.exit_code = Recorder.OK_EXIT_CODE

        Process.__init__(self)

    def stop(self):
        """ Stop adquisition
        """
        self.q.put(Recorder.RECORDER_STOP_COMMAND)

    def run(self):
        """ Start adquisition
        """
        self.exit_code = Recorder.OK_EXIT_CODE
        serial = Serial(self.port,
                        baudrate=Recorder.SERIAL_BAUDRATE,
                        timeout=Recorder.SERIAL_TIMEOUT)

        if serial.isOpen():
            sleep(1)
            serial.flush()
            serial.write(Recorder.ADC_START_COMMAND)

            current = 0

            while True:
                dat = serial.read(60)
                if not len(dat) == 60:
                    self.exit_code = Recorder.READ_ERROR_EXIT_CODE
                    break

                if not self.q.empty():
                    if self.q.get() == Recorder.RECORDER_STOP_COMMAND:
                        self.exit_code = Recorder.STOPPED_EXIT_CODE
                        break

                self.total += 1

                for i in range(0, len(dat), 3):
                    c1 = (ord(dat[i]) << 4) | ((ord(dat[i+1]) & 0xF0) >> 4)
                    c0 = (((ord(dat[i + 1])) & 0xF) << 8) | (ord(dat[i + 2]))
                    self.data[current][0] = c0
                    self.data[current][1] = c1
                    current += 1

                if current == self.blockcount * Recorder.RECORDER_BLOCKSIZE:
                    self.handler(self.data)
                    current = 0

                if self.total == self.countlimit:
                    break

            serial.write(Recorder.ADC_STOP_COMMAND)
            serial.close()

        else:
            self.exit_code = Recorder.PORT_NOT_OPENED_EXIT_CODE

        if self.exit_code == Recorder.READ_ERROR_EXIT_CODE:
            raise Exception('Recorder read error')

        if self.exit_code == Recorder.PORT_NOT_OPENED_EXIT_CODE:
            raise Exception('Port not opened error')

    def was_recording_ok(self):
        """ Returns if the recording was successfull or not
        """
        return (self.exit_code == Recorder.OK_EXIT_CODE) or (self.exit_code == Recorder.STOPPED_EXIT_CODE)


# Example block

f = open('data_out.txt', 'wt')

def sample_handler(data):
    for i in range(len(data)):
        f.write('%d %d\n' % (data[i][0], data[i][1]))
        #print ("%s %s" % (hex(data[i][0]),(hex(data[i][1]))))


if __name__ == "__main__":
    p = Recorder(port='COM9', handler=sample_handler, timelimit=120)
    p.start()
    p.join()
    f.close()
