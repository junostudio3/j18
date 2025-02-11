"""
 version 0.2
 blog: https://junostudio.tistory.com/
 git: https://github.com/junostudio3/jconsole
    JConsoleParser
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


class JConsoleParseResult(Enum):
    OK = 1
    TOO_MOUCH_COMMAND = 2
    UNKNOWN_ARGUMENT = 3
    UNKNOWN_COMMAND = 4
    OPTION_DUPLICATION = 5  # 옵션이 중복됨


class JConsoleCheckOptionResult:
    def __init__(self):
        self.isexist: bool = False
        self.message: str = ""
        self.option_value: str = ""
        self.result: JConsoleParseResult = JConsoleParseResult.OK

    def set_error(self, message: str, result: JConsoleParseResult):
        self.message: str = message
        self.result: JConsoleParseResult = result


class JConsoleOption:
    def __init__(self):
        self.key: str = ""
        self.value: str = ""


class JConsoleParser:
    def __init__(self):
        self.__arguments: list[str] = []
        for index in range(len(sys.argv) - 1):
            self.__arguments.append(sys.argv[index + 1])

        self.result: JConsoleParseResult = JConsoleParseResult.OK
        self.command: str = ''
        self.options: list[JConsoleOption] = []
        self.check_waiting_options: list[JConsoleOption] = []
        self.__command_link_: dict = {}

    @classmethod
    def printerrorln(cls, error_code: int, text: str):
        if error_code >= 0:
            cls.println(f'[error:{error_code:04d}] {text}')
        else:
            cls.println('[error:xxxx] ' + text)

    @classmethod
    def println(cls, text: str = ''):
        print(text, flush=True)

    @classmethod
    def print(cls, text: str):
        print(text, end='', flush=True)

    def add_commandlink(self, command: str, function):
        self.__command_link_[command] = function

    def check_arguments(self):
        if not self._check_grammar():
            return JConsoleParseResult.UNKNOWN_ARGUMENT

        candidate_command_list = self._collect_command()
        if len(candidate_command_list) == 0:
            # command가 없다면 --help 동작으로 동작
            self.command = '--help'
        elif len(candidate_command_list) == 1:
            self.command = candidate_command_list[0]
        else:
            # Command가 하나 이상 존재한다
            return JConsoleParseResult.TOO_MOUCH_COMMAND

        self.check_waiting_options = self._collect_option()

        if self.command not in self.__command_link_:
            return JConsoleParseResult.UNKNOWN_COMMAND

        return JConsoleParseResult.OK

    def check_option(self, option_key: str) -> JConsoleCheckOptionResult:
        res = JConsoleCheckOptionResult()
        for item in self.check_waiting_options[:]:  # list 복사해서 for
            if item.key == option_key:
                if res.isexist:
                    # 이미 찾은 옵션을 또 찾았다
                    res.set_error("Duplication Option <" + item.key + ">",
                                  JConsoleParseResult.OPTION_DUPLICATION)
                    return res
                self.options.append(item)
                self.check_waiting_options.remove(item)
                res.option_value = item.value
                res.isexist = True

        return res

    def execute_command(self):
        if self.command in self.__command_link_:
            self.__command_link_[self.command]()

    def _check_grammar(self):
        for argument in self.__arguments:
            if argument[:2] == '--':
                continue

            if argument[:1] != '-':
                return False
        return True

    def _collect_command(self):
        # command argument를 찾는다
        command_list: list[str] = []
        for arg_index in range(1, len(self.__arguments)):
            argument = self.__arguments[arg_index].lower()
            if argument[:2] != '--':
                continue

            command_list.append(argument)
        return command_list

    def _collect_option(self):
        option_list: list[JConsoleOption] = []

        for argument in self.__arguments:
            if argument[:2] == '--':
                # 명령은 넘어가자
                continue

            option = JConsoleOption()
            option.key = argument.lower()

            sub_option_index = argument.find(':')
            if sub_option_index >= 0:
                option.key = argument[:sub_option_index].lower()
                option.value = argument[sub_option_index + 1:]

            option_list.append(option)

        return option_list
