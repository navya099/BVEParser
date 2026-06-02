import chardet
import os
from enum import IntEnum
from typing import Optional


class TextEncoding:
    class Encoding(IntEnum):
        Unknown = 0
        IBM855 = 855
        IBM866 = 866
        SHIFT_JIS = 932
        EUC_KR = 949
        BIG5 = 950
        UTF16_LE = 1200
        UTF16_BE = 1201
        WIN1251 = 1251
        WIN1252 = 1252
        WIN1253 = 1253
        WIN1255 = 1255
        MAC_CYRILLIC = 10007
        UTF32_LE = 12000
        UTF32_BE = 12001
        ASCII = 20127
        KOI8_R = 20866
        EUC_JP = 20932
        ISO8859_2 = 28592
        ISO8859_5 = 28595
        ISO8859_7 = 28597
        ISO8859_8 = 28598
        ISO2022_JP = 50220
        ISO2022_KR = 50225
        ISO2022_CN = 50227
        HZ_GB_2312 = 52936
        GB18030 = 54936
        UTF7 = 65000
        UTF8 = 65001

    @staticmethod
    def get_encoding_from_bytes(data: bytes) -> 'TextEncoding.Encoding':
        # BOM 검사 (가장 신뢰도 높은 방식)
        if data.startswith(b'\xef\xbb\xbf'):
            return TextEncoding.Encoding.UTF8
        if data.startswith(b'\xff\xfe'):
            return TextEncoding.Encoding.UTF16_LE
        if data.startswith(b'\xfe\xff'):
            return TextEncoding.Encoding.UTF16_BE
        if data.startswith(b'\xff\xfe\x00\x00'):
            return TextEncoding.Encoding.UTF32_LE
        if data.startswith(b'\x00\x00\xfe\xff'):
            return TextEncoding.Encoding.UTF32_BE

        # chardet으로 감지
        result = chardet.detect(data)
        encoding_name = result['encoding']

        if encoding_name is None:
            return TextEncoding.Encoding.Unknown

        try:
            # 표준 이름 매핑
            return TextEncoding.Encoding[encoding_name.upper().replace('-', '_')]
        except KeyError:
            return TextEncoding.Encoding.Unknown

    @staticmethod
    def convert_to_system_encoding(encoding_enum: 'TextEncoding.Encoding', default_encoding: Optional[str] = None) -> str:
        if encoding_enum == TextEncoding.Encoding.Unknown:
            return default_encoding or 'utf-8'

        try:
            return encoding_enum.name.replace('_', '-')
        except Exception:
            return default_encoding or 'utf-8'

    @staticmethod
    def get_system_encoding_from_bytes(data: bytes, default_encoding: Optional[str] = None) -> str:
        encoding_enum = TextEncoding.get_encoding_from_bytes(data)
        return TextEncoding.convert_to_system_encoding(encoding_enum, default_encoding)

    @staticmethod
    def get_system_encoding_from_file(file_path: str, default_encoding: Optional[str] = None) -> str:
        try:
            with open(file_path, 'rb') as f:
                data = f.read()
            return TextEncoding.get_system_encoding_from_bytes(data, default_encoding)
        except Exception:
            return default_encoding or 'utf-8'

    @staticmethod
    def get_system_encoding_from_folder_and_file(folder: str, filename: str, default_encoding: Optional[str] = None) -> str:
        full_path = os.path.join(folder, filename)
        return TextEncoding.get_system_encoding_from_file(full_path, default_encoding)
