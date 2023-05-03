"""
 blog: https://junostudio.tistory.com/
 git: https://github.com/junostudio3/j18
    j18 Console
    작업 내용을 Console에 출력하기 위한 class 이다. 이것이 하는 일은 거의 매번 flush 한다는 것 뿐이다.
    flush을 해주어야 j18의 내용을 읽어들일 때 즉각즉각 읽을 수 있기 때문에 실수 하지 않기 위해 출력은
    해당 클래스를 사용하는 방향으로 진행하였다.

"""

class Console:
    def PrintLn(text:str = ''):
        print(text, flush=True)

    def Print(text:str):
        print(text, end='', flush=True)
