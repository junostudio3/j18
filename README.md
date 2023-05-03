# j18 v0.0.0.9
- Prompt 에서 Seafile 클라우드에 명령을 내리기 위한 프로그램입니다.
- 매크로 등을 사용하여 편리하게 자동화에 사용할 만한 프로그램을 개발하는게 목표입니다.

## 사용법
- [main.md](./document/main.md)

## 설치
- 다음의 라이브러리의 설치가 필요하다 (Apache Software License 2.0)
- pip3 insall requests
- pip3 install requests_toolbelt

## PyInstaller 를 이용하여 직접 실행파일 만드는 법
- Linux or Mac
    ```
    pyinstaller --onefile --add-data="resource/*:resource" -n j18 j18.py
    ```
- Windows
    ```
    pyinstaller --onefile --add-data="resource/*;resource" -n j18 j18.py
    ```
