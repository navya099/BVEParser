import hashlib
import os


class Path:
    InvalidPathChars = [':', '*', '?', '"', '<', '>', '|']
    PathSeparationChars = ['/', '\\']
    InvalidFileNameChars = {
        "'", '<', '>', '|', '\0', '\u0001', '\u0002', '\u0003', '\u0004', '\u0005',
        '\u0006', '\a', '\b', '\t', '\n', '\v', '\f', '\r', '\u000e', '\u000f',
        '\u0010', '\u0011', '\u0012', '\u0013', '\u0014', '\u0015', '\u0016', '\u0017', '\u0018', '\u0019',
        '\u001a', '\u001b', '\u001c', '\u001d', '\u001e', '\u001f', ':', '*', '?', '\\',
        '/'
    }

    @staticmethod
    def get_checksum(file_path: str) -> str:
        if not file_path or not os.path.isfile(file_path):
            return ''

        sha256 = hashlib.sha256()

        with open(file_path, 'rb') as f:
            for block in iter(lambda: f.read(4096), b''):
                sha256.update(block)

        return sha256.hexdigest().upper()

    @staticmethod
    def is_absolute_path(path: str) -> bool:
        if len(path) < 1:
            return False
        if path[0] == Path.PathSeparationChars or path[0] == Path.PathSeparationChars[1]:
            # e.g.
            #  \Test\Foo.txt(Windows)
            # / Test / Foo.txt(Windows, Unix)
            return True
        if len(path) < 3:
            return False

        if path[1] == ':' and path[2] == Path.PathSeparationChars[0] or path[2] == Path.PathSeparationChars[1]:
            # e.g.
            #  C:\Test\Foo.txt (Windows)
            #  C:/Test/Foo.txt (Windows)
            return True
        return False

    @staticmethod
    def contains_invalid_chars(expression: str) -> bool:
        if not Path.is_absolute_path(expression):
            if any(char in Path.InvalidPathChars for char in expression):
                return True

        for char in expression:
            if char in Path.InvalidFileNameChars and char in Path.InvalidPathChars:
                return True

        return False
