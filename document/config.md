
# config
- config는 j18이 접속 관련한 정보를 참고하는 파일입니다.
- j18을 사용하려면 해당 파일을 먼저 만들어야 합니다.

## 경로
- 유저폴더/.j18/config
    - linux / mac
        - ~/.j18/config
    - windows
        - C:/Users/[사용자ID]/.j18/config

## 사용법
- 접속할 Seafile 서버 주소 정보를 갖는다. 해당 일반적인 config (ini) 파일의 구조를 가집니다.
- 다음의 형태로 접속할 서버의 정보를 기입해 놓습니다.
- token을 모른다면 비워두고 밑에 [--get-token](command_get-token.md) 명령을 통해 token을 얻은 후 다시 기입합니다.
    ```
    [server_{Server이름}]
    address = https://address:port
    token = #########

    [repos_{저장소명}]
    id = --------

    [connection_{접속명}]
    server = {Server이름}
    repos = {저장소명}
    ```

[main 페이지로 이동](main.md)