from RouteLoader import RouteLoader

def console_progress(percent):
    print(f"\r진행률: {percent}%", end="", flush=True)

def main():
    path = input("루트 파일 경로를 입력하세요: ").strip()
    if not path:
        print("파일이 선택되지 않았습니다.")
        return

    loader = RouteLoader(path)
    success, error = loader.load(progress_callback=console_progress)
    print()  # 다음 줄로 이동

    if success:
        print("루트 로딩 성공!")
    else:
        print(f"루트 로딩 실패: {error}")

if __name__ == "__main__":
    main()
