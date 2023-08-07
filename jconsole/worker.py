"""
 version 0.1
 blog: https://junostudio.tistory.com/
 git: https://github.com/junostudio3/jconsole
    jConsoleWorker
    - Argument Parsing
      @ 인자로 받은 argument를 이용하여 다음의 변수를 세팅한다 @

      1. result
      2. command
      3. options

    - Function #1
      PrintErrorLn, PrintLn, Print
      Console에 내용을 출력하기 위한 함수
      이 함수들은 내용을 매번 flush 한다
"""

import sys
from enum import Enum

class jConsoleParseResult(Enum):
  OK = 1
  TOO_MOUCH_COMMAND = 2
  UNKNOWN_ARGUMENT = 3

class jConsoleOption:
  def __init__(self):
    self.key:str = ""
    self.value:str = ""

class jConsoleWorker:
  def __init__(self):
    self.__arguments : list[str] = []
    for index in range(len(sys.argv) - 1):
      self.__arguments.append(sys.argv[index + 1])

    self.result:jConsoleParseResult = jConsoleParseResult.OK
    self.command:str = ''
    self.options:list[jConsoleOption] = []

    if self._FindCommand():
      self._FindOptions()

  def PrintErrorLn(error_code:int, text:str):
    if error_code >= 0:
      __class__.PrintLn('[error:' + '{0:04d}'.format(error_code) + '] ' + text)
    else:
      __class__.PrintLn('[error:xxxx] ' + text)

  def PrintLn(text:str = ''):
    print(text, flush=True)

  def Print(text:str):
    print(text, end='', flush=True)

  def _FindCommand(self):
    # command argument를 찾는다
    found_command:bool = False
    self.command = '--help'
    for arg_index in range(1, len(self.__arguments)):
      argument = self.__arguments[arg_index].lower()
      if argument[:2] != '--':
        continue

      self.command = argument
      if found_command == True:
        # Command가 하나 이상 존재한다
        self.result = jConsoleParseResult.TOO_MOUCH_COMMAND
        return False

      found_command = True
    return True

  def _FindOptions(self):
    arg_index = 0

    for argument in self.__arguments:
      if argument[:2] == '--':
          # 명령은 넘어가자
          continue
      
      if argument[:1] != '-':
          # 모르는 양식이다
          self.result = jConsoleParseResult.UNKNOWN_ARGUMENT
          return False
      
      option = jConsoleOption()
      option.key = argument.lower()

      sub_option_index = argument.find(':')
      if sub_option_index >= 0:
        option.key = argument[:sub_option_index].lower()
        option.value = argument[sub_option_index + 1:]

      self.options.append(option)

    return True