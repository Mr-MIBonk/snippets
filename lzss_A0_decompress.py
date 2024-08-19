import argparse
from pathlib import Path
import struct

def bits(byte):
    return (
        (byte >> 7) & 1,
        (byte >> 6) & 1,
        (byte >> 5) & 1,
        (byte >> 4) & 1,
        (byte >> 3) & 1,
        (byte >> 2) & 1,
        (byte >> 1) & 1,
        (byte) & 1,
    )

def decompress_raw_lzss10(indata):
    data = bytearray()
    it = iter(indata)

    def writebyte(b):
        data.append(b)

    def readbyte():
        return next(it)

    def readshort():
        a = next(it)
        b = next(it)
        return (a << 8) | b

    def copybyte():
        data.append(next(it))

    try:
        while True:
            b = readbyte()
            flags = bits(b)
            for flag in flags:
                if flag == 0:
                    copybyte()
                elif flag == 1:
                    sh = readshort()
                    count = sh >> 10
                    disp = sh & 0x3FF
                    for _ in range(count):
                        writebyte(data[-disp])
                else:
                    raise ValueError(flag)
    except StopIteration:
        # End of input data reached
        pass

    return data

def main():
    parser = argparse.ArgumentParser(description="Decompress an LZSS A0 compressed file.")
    parser.add_argument("input_file", type=str, help="Input file path")
    parser.add_argument("output_file", type=str, help="Output file path")
    args = parser.parse_args()

    input_data = Path(args.input_file).read_bytes()
    decompressed_data = decompress_raw_lzss10(input_data)

    with open(args.output_file, 'wb') as file:
        file.write(decompressed_data)

if __name__ == "__main__":
    main()
