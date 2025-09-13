import struct


class ICMPDecoder:
    def __init__(self, buffer: bytes):
        self._buffer: bytes = buffer
        self.header = struct.unpack('<BBHHH', self._buffer)
        self.type = self.header[0]
        self.code = self.header[1]
        self.sum = self.header[2]
        self.id = self.header[3]
        self.seq = self.header[4]





