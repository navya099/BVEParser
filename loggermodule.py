import logging
import os

# 디렉토리 존재 여부 확인 및 생성
log_directory = r"c:\temp"
if not os.path.exists(log_directory):
    os.makedirs(log_directory)

# 전역 로거 설정
logger = logging.getLogger("my_app")  # 특정한 로거 이름 사용
logger.setLevel(logging.DEBUG)  # 로깅 레벨 설정

# 파일 핸들러 추가
file_handler = logging.FileHandler(r"c:\temp\log.csv", mode ='w')
file_handler.setLevel(logging.DEBUG)

# 로그 포맷 설정
formatter = logging.Formatter("%(asctime)s,%(levelname)s,%(message)s", datefmt="%H:%M:%S")
file_handler.setFormatter(formatter)

# 핸들러 중복 추가 방지
if not logger.handlers:
    logger.addHandler(file_handler)  # 파일 핸들러만 추가
