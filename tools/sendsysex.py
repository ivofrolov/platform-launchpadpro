import time
import rtmidi
from rtmidi import midiconstants


MESSAGE_TIME_GAP = 0.001 * 10


class BaseUploadError(Exception):
    pass


class NoAvailablePortsError(BaseUploadError):
    pass


class InvalidPortError(BaseUploadError):
    pass


def parse_sysex(data: bytes):
    start = 0
    for index, byte in enumerate(data):
        if byte == midiconstants.SYSTEM_EXCLUSIVE:
            start = index
        elif byte == midiconstants.END_OF_EXCLUSIVE:
            yield data[start : index + 1]


def send_sysex(port: int, text: str):
    midiout = rtmidi.MidiOut()

    try:
        midiout.open_port(port=port)
        for msg in parse_sysex(text):
            midiout.send_message(msg)
            time.sleep(MESSAGE_TIME_GAP)
    finally:
        midiout.close_port()


def find_port(spec: str) -> int:
    midiout = rtmidi.MidiOut()

    ports = midiout.get_ports()
    if len(ports) == 0:
        raise NoAvailablePortsError('No MIDI output ports found')

    for port, name in enumerate(ports):
        if spec in name:
            break
    else:
        available_ports = ', '.join([f'"{name}"' for name in ports])
        raise InvalidPortError(
            f'Invalid MIDI output port (use one of these available: {available_ports})'
        )

    return port


if __name__ == '__main__':
    import sys
    import logging
    import argparse

    logging.basicConfig(format='%(message)s', level=logging.INFO)

    parser = argparse.ArgumentParser(
        description='Send MIDI System Exclusive file to given device'
    )
    parser.add_argument(
        'source',
        type=argparse.FileType('rb', 0),
        nargs='?',
        help='syx format file path',
    )
    parser.add_argument('-p', '--port', help='MIDI output port name')

    args = parser.parse_args()

    try:
        port = find_port(spec=args.port)
        send_sysex(port=port, text=args.source.read())
    except BaseUploadError as exc:
        logging.error(exc)
        sys.exit(1)

    sys.exit(0)
