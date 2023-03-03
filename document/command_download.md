
# --download

- Target은 [-t 옵션](option_t.md)을 이용하여 지정합니다.
- [-c 옵션](option_c.md) 대신 [-s](option_s.md)와 [-r](option_r.md)을 써도 됩니다.
- [-d 옵션](option_d.md)로 다운받을 위치를 지정합니다.
- [-skip-same-file] 옵션을 사용하면 이미 받아진 파일은 다운로드에서 제외됩니다.
- 선택된 Repository의 Target(File)을 download 합니다.
    ```
    j18 -c:{접속명} -t:{원격지경로} -d:{Local경로} --download
    ```
- 만약 Target이 Folder라면 Folder 내의 파일을 재귀적으로 하나 하나 download 받습니다.

[main 페이지로 이동](main.md)