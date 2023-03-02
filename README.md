# j18 v0.0.0.1
- Prompt 에서 Seafile 클라우드에 명령을 내릴 수 있는 프로그램 개발이 목표이다.
- 매크로 등을 만들어서 Seafile 에 명령을 좀 더 쉽게 줄 수 있는 프로그램을 개발하고자 한다.

# 유저폴더/.j18/config
접속할 Seafile 서버 주소 정보를 갖는다. 해당 일반적인 config (ini) 파일의 구조를 가진다.
다음의 형태로 접속할 서버의 정보를 기입해 놓는다. token을 모른다면 비워두고 밑에 --get-token 명령을 통해 token을 얻은 후 다시 기입한다.

```
[server_{Server이름}]
address = https://address:port
token = #########

[repos_{저장소명}]
id = #########

[connection_{접속명}]
server = {Server이름}
repos = {저장소명}
```

# Arguments
## -s
접속할 Seafile 서버 이름을 넣는다. 보통 필수적인 argument이다. 호출전에 config에 서버정보를 미리 기입해 놓아야 한다.
```
j18 -s{Server이름}
```

## -r
접속할 Repository 이름을 넣는다. 보통 필수적인 argument이다. 호출전에 config에 Repository 정보를 미리 기입해 놓아야 한다.
```
j18 -r{Repository명}
```

## -c
접속할 Seafile 서버와 Repository을 한쌍으로 묶어 놓은 접속명을 통해 -s -r 옵션을 동시 실행한다. 호출전에 config에 접속명 정보를 미리 기입해 놓아야 한다.
```
j18 -rs{접속명}
```

## -t
명령을 수행할 Repository의 Target Path를 지정한다. 미지정시 / (루트) 가 선택된다.
```
j18 -t{경로}
```

## -d
원격지와 연동할 local 경로를 지정한다. 미지정시 작업디렉토리가 선택된다.
```
j18 -d{경로}
```

## --show-config
config 파일 내용을 보여줍니다
```
j18 --show-config
```

## --get-token
token은 j18의 다음의 명령을 이용하여 얻는 것이 가능하다. -s 옵션 사용이 필수이다. 명령 수행시 ID와 PASSWORD를 입력을 묻게 되고 이 과정을 통해 token이 생성된다. 이 토큰을 j18.cfg에 넣으면 된다.
```
j18 -s{Server이름} --get-token
```

## --get-repo-list
접근 가능한 repository 리스트를 얻는다. 이것으로 repository의 id를 얻을 수 있다.
```
j18 -s{Server이름} --get-repo-list
```

## --filedetail
선택된 repository의 Target(File)의 상세 정보를 얻는다
```
j18 -c{접속명} -t{원격지경로} --filedetail
```

## --download
선택된 Repository의 Target(File)을 download 한다
```
j18 -c{접속명} -t{원격지경로} -d{Local경로} --download
```

## --ls
선택된 Repository의 Target(Directory)의 Item 리스트를 얻는다
```
j18 -c{접속명} --ls
```
