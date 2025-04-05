import hashlib
import os

class Path:
    InvalidPathChars = [':', '*', '?', '"', '<', '>', '|']
    PathSeparationChars = ['/', '\\']

    @staticmethod
    def get_checksum(file_path: str) -> str:
        if not file_path or not os.path.isfile(file_path):
            return ''

        sha256 = hashlib.sha256()

        with open(file_path, 'rb') as f:
            for block in iter(lambda: f.read(4096), b''):
                sha256.update(block)

        return sha256.hexdigest().upper()
