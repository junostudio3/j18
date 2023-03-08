
# error code
- 출력으로 '[error{xxxx}] message' 형태의 출력이 나오면 code에 따라 원인을 파악할 수 있습니다. error code 는 다음과 같습니다.
    |code|message|comment|
    |----|----|----|
    |0001|Connection failed|주소나 포트가 잘못되어 서버에 접속할 수 없습니다.|
    |0002|Permission declined|해당 API Token이 잘못 되어  접속 권한이 없습니다.|
    |0003|Repos not found|접근 가능한 Repository 중 해당 ID를 찾을 수 없습니다.|
    |0004|Unknown Server Name|config에서 해당 server name을 찾을 수 없습니다.|
    |0005|Unknown Repository Name|config에서 해당 repository name을 찾을 수 없습니다.|
    |xxxx|Undefined error|아직 정의되어 있지 않는 메시지입니다.|

[main 페이지로 이동](main.md)