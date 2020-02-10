from intelhex import IntelHex


def reset_bytes(eol: bytes = b'\x71') -> bytes:
    return b'\xF0\x00\x20\x29\x00' + eol


def eight_to_seven(data: bytearray) -> bytes:
    '''Seven bytes of eight-bit data converted to eight bytes of seven-bit data.'''
    result = [
                          data[0] >> 1,
        (data[0] << 6) + (data[1] >> 2),
        (data[1] << 5) + (data[2] >> 3),
        (data[2] << 4) + (data[3] >> 4),
        (data[3] << 3) + (data[4] >> 5),
        (data[4] << 2) + (data[5] >> 6),
        (data[5] << 1) + (data[6] >> 7),
        data[6]
    ]

    for i in range(0, len(result)):
        result[i] &= 0x7F
    
    return ''.join(map(chr, result)).encode()


def block(ihex: IntelHex, offset: int, byte_width: int) -> bytes:
    payload = b''
    
    for i in range(0, byte_width, 7):
        payload += eight_to_seven(ihex.tobinarray(offset + i, size=7))

    return payload[:(1 + (byte_width * 8) // 7)]


def convert_ihex_syx(source, byte_width: int = 32) -> bytearray:
    ihex = IntelHex(source)
    
    syx = bytearray()

    # HEADER
    syx.extend(reset_bytes())
    syx.extend(b'\x00\x51')  # id
    syx.extend(b'\x00' + ihex.gets(ihex.minaddr() + 0x102, 1))
    syx.extend(b'\x00' + ihex.gets(ihex.minaddr() + 0x101, 1))
    syx.extend(b'\x00' + ihex.gets(ihex.minaddr() + 0x100, 1))
    syx.append(0xF7)

    # PAYLOAD
    for i in range(ihex.minaddr() + byte_width, ihex.maxaddr(), byte_width):
        syx.extend(reset_bytes(eol=b'\x72'))
        syx.extend(block(ihex, i, byte_width))
        syx.append(0xF7)
    
    syx.extend(reset_bytes(eol=b'\x73'))
    syx.extend(block(ihex, ihex.minaddr(), byte_width))
    syx.append(0xF7)

    # CHECKSUM
    syx.extend(reset_bytes(eol=b'\x76'))
    syx.extend(b'\x00' + b'Firmware')
    syx.extend(b'\x00\x00\x00\x00\x00\x00\x00\x00')
    syx.append(0xF7)

    return syx


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(
        description='Convert Launchpad Pro  firmware from ihex to syx format')
    parser.add_argument('source', type=argparse.FileType('r'),
        help='ihex format file path')
    parser.add_argument('destination', type=argparse.FileType('wb'),
        help='syx format file path')

    args = parser.parse_args()

    args.destination.write(convert_ihex_syx(args.source))
