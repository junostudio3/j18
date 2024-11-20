"""
 version 0.1
 blog: https://junostudio.tistory.com/
 git: https://github.com/junostudio3/jconsole
    jConsoleRunner
    - Console 프로그램을 실행 후 결과를 얻어오기 위한 클래스
"""
import platform
import subprocess as subp


class jConsoleRunner:
    def __init__(self):
        self.processor: subp.Popen = None

    def Execute(self, executeFilePath: str, arguments: list[str]):
        self.processor = None

        args: list = []
        args.append(executeFilePath)
        for argument in arguments:
            args.append(argument)

        if platform.system() == "Windows":
            self.processor = subp.Popen(args,
                                        stdout=subp.PIPE,
                                        bufsize=0,
                                        creationflags=subp.CREATE_NO_WINDOW)
        else:
            self.processor = subp.Popen(args,
                                        stdout=subp.PIPE,
                                        bufsize=0)

        return self.processor is not None

    def IsRunning(self):
        return self.processor is not None

    def Terminate(self):
        if self.processor is None:
            return

        self.processor.kill()
        self.processor = None

    def ReadOutput(self) -> str:
        while True:
            line: bytes = self.processor.stdout.readline()

            if line is None or line == b'':
                if self.processor.poll() is not None:
                    # 중간에 프로세스를 종료당함
                    self.processor = None
                    return None
                continue

            return line.decode('utf-8')
