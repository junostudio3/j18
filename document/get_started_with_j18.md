
# 처음 시작하기

- j18을 사용하려면 먼저 수동으로 사용자폴더/.j18/config 란 파일을 만드셔야 합니다.
- 메모장 같은 것으로 config 파일을 만드셔서 다음과 같이 먼저 접속한 서버를 등록하는 작업을 진행합니다.
    ```
    [server_test1]
    address = http://xxxxxx:port
    ```
- 위처럼 파일을 만들고 나시면 이제부터는 test1이라는 이름으로 해당 server를 접속하실 수 있게 됩니다.
- 하지만 아직 server의 접속 권한이 없는 상태입니다.
- 다음의 명령을 주면 해당 server에 접속하기 위한 token 을 얻을 수 있습니다.
    ```
    $ j18 -s:test1 --get-token

    user_name: ########
    password: ########
    token: ---------------------------------
    ```

- config 파일에 token 부분을 copy하여 다음과 같이 붙여 넣고 다시 저장합니다.
    ```
    [server_test1]
    address = http://xxxxxx:port
    token = ---------------------------------
    ```

- 이제 접속 권한은 얻으셨습니다. 이제 저장소에 접근할 수 있어야 합니다.
- 다음의 명령을 주면 해당 server에서 접속할 수 있는 repository list를 얻을 수 있습니다.
- 앞에 이름은 web상에서 보이는 저장소 이름이며 rw는 권한 정보입니다. -> 옆의 내용이 저장소의 id입니다.
    ```
    $ j18 -s:test1 --get-repo-list
    내 라이브러리(rw) -> xxxxxxxx-xxxx-xxxx-xxxxxxxxxxxx
    ```
- 이 repository_id를 copy합니다. 이제 config 파일에 repository_id를 넣어주셔야 합니다.
    ```
    [server_test1]
    address = http://xxxxxx:port
    token = ---------------------------------

    [repos_my]
    id = xxxxxxxx-xxxx-xxxx-xxxxxxxxxxxx

    [connection_link1]
    server = test1
    repos = my
    ```

- j18을 이용하여 저장소 접근시 [-s](option_s.md) 옵션으로 server를 선택하고, [-r](option_r.md) 옵션으로 repository를 선택할 수 있습니다.
- 하지만 매번 쓰면 불편하여, 위처럼 connection이란 것을 만들고, server와 repos를 지정해 두면 [-c:{접속명}](option_c.md)으로 한번에 접속할 수 있습니다. 저는 link1이라는 이름으로 만들었습니다. 이제 준비 과정이 모두 끝났습니다.

# 기능
- 현재 j18로 사용가능한 명령은 다음의 총 세가지 뿐입니다.

- [--ls](command_ls.md) 명령을 통해 폴더의 하위 목록 정보를 볼 수 있습니다.
    ```
    j18 -c:{접속명} -t:"seafile 폴더경로" --ls
    ```
- [--filedetail](command_filedetail.md) 명령을 통해 파일의 자세한 정보를 볼 수 있습니다.
    ```
    j18 -c:{접속명} -t:"seafile 파일경로" --filedetail
    ```
- [--download](command_download.md) 명령을 통해 파일을 다운 받습니다. [-d](option_d.md) 옵션 생략시 j18을 실행한 경로에 다운받습니다.

    ```
    j18 -c:{접속명} -t:"seafile 파일경로" -d:"내 pc 폴더" --download
    ```

[main 페이지로 이동](main.md)