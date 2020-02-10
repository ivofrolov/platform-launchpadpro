from rtmidi import RtMidiError, InvalidPortError
from rtmidi.midiutil import list_output_ports, open_midioutput


def parse_sysex(data):
    start = 0
    for index, byte in enumerate(data):
        if byte == 0xF0:
            start = index
        elif byte == 0xF7:
            yield data[start:index+1]


if __name__ == '__main__':
    import sys
    import time
    import logging
    import argparse

    logging.basicConfig(format='{levelname}: {message}', style='{', level=logging.INFO)

    parser = argparse.ArgumentParser(
        description='Send MIDI System Exclusive file to given device')
    parser.add_argument('source', type=argparse.FileType('rb', 0), nargs='?',
        help='syx format file path')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-p', '--port',
        help='MIDI output port name')
    group.add_argument('-l', '--list', action='store_true',
        help='list available MIDI ports')

    args = parser.parse_args()

    if args.list:
        try:
            list_output_ports()
        except RtMidiError as e:
            logging.error(e)
            sys.exit(1)
        sys.exit(0)

    try:
        midiout, _ = open_midioutput(port=args.port, interactive=False)
    except InvalidPortError as e:
        logging.error('Invalid MIDI name or number (use -l option to list available ports)')
        sys.exit(2)
    except RtMidiError as e:
        logging.error(e)
        sys.exit(1)

    try:
        for msg in parse_sysex(args.source.read()):
            midiout.send_message(msg)
            time.sleep(0.001 * 10)
    finally:
        midiout.close_port()

    sys.exit(0)
