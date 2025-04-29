import struct


class FileFormats:

    @staticmethod
    def IsNautilusFile(path: str) -> bool:
        """
        Whether the file is a Nautilus-encrypted file.
        """
        try:
            with open(path, 'rb') as stream:
                if os.path.getsize(path) < 32:
                    return False
                read_bytes = stream.read(16)
                # struct.unpack은 바이너리를 언팩하는 함수
                return (
                        struct.unpack('<I', read_bytes[0:4])[0] == 0x554c544e and
                        struct.unpack('<I', read_bytes[4:8])[0] == 0x4d524453 and
                        struct.unpack('<I', read_bytes[8:12])[0] == 0x14131211 and
                        struct.unpack('<I', read_bytes[12:16])[0] == 0x00811919
                )
        except Exception:
            return False
