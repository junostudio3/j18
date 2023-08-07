"""
 version 0.1
 blog: https://junostudio.tistory.com/
 git: https://github.com/junostudio3/jconsole
    jConsoleRunner
    - Console 프로그램을 실행 후 결과를 얻어오기 위한 클래스
"""
import platform
import subprocess

class jConsoleRunner:
  def __init__(self):
    self.processor:subprocess.Popen = None

  def Execute(self, execute_file_path:str, arguments:list[str]):
    self.processor = None

    p_args:list = []
    p_args.append(execute_file_path)
    for argument in arguments:
      p_args.append(argument)

    if platform.system() == "Windows":
        self.processor = subprocess.Popen(p_args, stdout=subprocess.PIPE, bufsize=0, creationflags=subprocess.CREATE_NO_WINDOW)
    else:
        self.processor = subprocess.Popen(p_args, stdout=subprocess.PIPE, bufsize=0)

    return self.processor != None
  
  def IsRunning(self):
    return self.processor != None
  
  def Terminate(self):
    if self.processor == None: return

    self.processor.kill()
    self.processor = None
  
  def ReadOutput(self) -> str:
    while True:
      line: bytes = self.processor.stdout.readline()

      if line == None or line == b'':
        if self.processor.poll() is not None:
          # 중간에 프로세스를 종료당함
          self.processor = None
          return None
        continue
      
      return line.decode('utf-8')
