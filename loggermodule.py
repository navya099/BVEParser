import logging

# 전역 로거 설정
logger = logging.getLogger("my_app")  # 특정한 로거 이름 사용
logger.setLevel(logging.DEBUG)  # 로깅 레벨 설정

# 콘솔 핸들러 추가
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)

# 로그 포맷 설정
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
console_handler.setFormatter(formatter)

# 핸들러 중복 추가 방지
if not logger.handlers:
    logger.addHandler(console_handler)
