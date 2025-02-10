"""
 blog: https://junostudio.tistory.com/
 git: https://github.com/junostudio3/j18
 j18 Main

"""

from enum import Enum
import locale
import os
from getpass import getpass

from jconsole.parser import JConsoleParser as jCP
from jconsole.parser import JConsoleParseResult as jCPResult
from seafile import JSeaFile, JSeaFileProgress
from environment import Environment
from res import LoadResourceText
from j18console.config import J18Config
from j18console.progress import ConsolePorgress


class ErrorCode(Enum):
    success = 0
    too_much_command = 1
    unknown_argument = 2
    option_is_wrong = 3
    valid_failed = 4
    command_failed = 5
    option_duplication = 6


class J18Main (jCP):
    def __init__(self):
        super().__init__()
        self.progressDownload = ConsolePorgress(True)
        self.progressUpload = ConsolePorgress(False)
        self.seafile = JSeaFile()
        self.config = J18Config()
        self.target = "/"
        self.dest = os.getcwd()
        self.skip_same_file = False
        self.add_commandlink('--help', self.__command_help)
        self.add_commandlink('--version', self.__command_version)
        self.add_commandlink('--show-config', self.__command_showconfig)
        self.add_commandlink('--get-token', self.__command_gettoken)
        self.add_commandlink('--get-repo-list', self.__command_getrepolist)
        self.add_commandlink('--filedetail', self.__command_filedetail)
        self.add_commandlink('--download', self.__command_download)
        self.add_commandlink('--mkdir', self.__command_create_directory)
        self.add_commandlink('--ls', self.__command_ls)
        self.add_commandlink('--upload', self.__command_upload)
        self.add_commandlink('--validate', self.command_validate)

    def apply_options(self):
        # 다음순서 Option을 체크하며 순서대로 읽는다
        options: dict = {
            "-skip-same-file": self.__applyoption_skipsamefile,
            "-update-line-by-step": self.__applyoption_updatelinebystep,
            "-r": self.__applyoption_repository,
            "-t": self.__applyoption_target,
            "-d": self.__applyoption_destination,
            "-s": self.__applyoption_server,
            "-c": self.__applyoption_connection
            }

        for option, function in options.items():
            res = self.check_option(option)
            if res.result != jCPResult.OK:
                jCP.printerrorln(ErrorCode.option_duplication.value,
                                 res.message)
                return False

            if not res.is_exist:
                continue

            if not function(res.option_value):
                jCP.printerrorln(ErrorCode.option_is_wrong.value,
                                 'option is wrong: ' + option)
                return False

        if len(self.check_waiting_options) == 0:
            return True

        option_key = self.check_waiting_options[0].key

        jCP.printerrorln(ErrorCode.unknown_argument.value,
                         "unkown argument: " + option_key)
        return False

    def __command_help(self):
        version = Environment.version
        jCP.print(f'j18 version {version} copyright(c) 2023. ')
        jCP.println('juno-studio all rights reserved.')
        jCP.println()

        current_locale = str(locale.getlocale()[0])

        # Windows에서는 locale 이름이 다르다
        if current_locale == "Korean_Korea":
            current_locale = "ko_KR"

        text = LoadResourceText(f"help_{current_locale}.txt")
        if text == "":
            text = LoadResourceText("help_en_US.txt")

        jCP.println(text)

        return ErrorCode.success

    def __command_version(self):
        jCP.println(Environment.version)
        return ErrorCode.success

    def __command_showconfig(self):
        try:
            with open(os.path.expanduser("~/.j18/") + "config",
                      "r",
                      encoding='UTF8') as config_file:
                jCP.println(config_file.read())
        except Exception:
            jCP.println("Config file not found")
        return ErrorCode.success

    def __command_gettoken(self):
        if self.config.address == "":
            jCP.printerrorln(-1, 'The following options are required.')
            jCP.printerrorln(-1, 'option: -s:{ServerName}')
            return ErrorCode.valid_failed

        user_name = input("user_name:")
        password = getpass("password:")
        token = self.seafile.get_api_token(user_name, password)
        if token == "":
            jCP.printerrorln(-1, 'get-token failed')
            return ErrorCode.command_failed

        jCP.println('token:' + token)
        return ErrorCode.success

    def __command_getrepolist(self):
        if self.config.address == "":
            jCP.println('[error:xxxx] The following options are required.')
            jCP.println('[error:xxxx] option: -s:{ServerName}')
            return ErrorCode.valid_failed

        items = self.seafile.get_repositorylist()
        if items is None:
            jCP.printerrorln(-1, 'Get Repository List Failed')
            return ErrorCode.command_failed

        for item in items:
            jCP.println(item.name + "(" + item.permission + ") -> " + item.id)

        return ErrorCode.success

    def __command_filedetail(self):
        info = self.seafile.get_filedetail(self.target)
        if info is not None:
            jCP.println(" ID: " + info.id)
            jCP.println(" Last Modifier Name: " + info.last_modifier_name)
            jCP.println(" Last Modified: " + str(info.last_modified))
            jCP.println(" Size: " + str(info.size))
            return ErrorCode.success
        else:
            jCP.printerrorln(-1, 'File not found : ' + self.target)
            return ErrorCode.command_failed

    def __command_download(self):
        progress = JSeaFileProgress(self.progressDownload)

        if self.seafile.download(self.target,
                                 self.dest,
                                 self.skip_same_file,
                                 progress):
            jCP.println("download success")
            return ErrorCode.success
        else:
            jCP.println("\n[error:xxxx] download failed")
            return ErrorCode.command_failed

    def __command_create_directory(self):
        success = self.seafile.create_directory(self.target)
        if success:
            jCP.println("Success")
            return ErrorCode.success
        else:
            jCP.printerrorln(-1, 'Failed to Create Directory : ' + self.target)
            return ErrorCode.command_failed

    def __command_ls(self):
        items = self.seafile.get_listitems_in_directory(self.target)
        if items is None:
            folder = self.target
            jCP.printerrorln(-1, f"Get Item List (Target Directory={folder})")
            return ErrorCode.command_failed

        if len(items) != 0:
            for item in items:
                if item.is_directory:
                    jCP.println("[D] " + item.name)
                else:
                    jCP.println(f"[F] {item.name} ({item.size} bytes)")

        return ErrorCode.success

    def __command_upload(self):
        link: str = self.seafile.get_uploadlink(self.target)
        if link is None:
            jCP.printerrorln(-1, 'get upload file link failed')
            return ErrorCode.command_failed

        progress = JSeaFileProgress(self.progressUpload)

        if JSeaFile.uploadfile(link, self.target, self.dest, progress):
            jCP.println("upload success")
            return ErrorCode.success
        else:
            jCP.println()
            jCP.printerrorln(-1, 'upload failed')
            return ErrorCode.command_failed

    def command_validate(self, show_success_message: bool = True):
        if self.seafile.check_address() is False:
            address = self.config.address
            jCP.printerrorln(1, f'Connect Failed (Address:{address})')
            return ErrorCode.valid_failed

        if self.config.token != '':
            # Token이 세팅되어 있으니 Token 문제 없나 체크
            if self.seafile.check_token() is False:
                token = self.config.token
                jCP.printerrorln(2, f'Permission declined (Token:{token})')
                return ErrorCode.valid_failed

            # Repos가 세팅되어 있으니 Repos 체크
            if self.config.repos_id != '':
                found = False
                for item in self.seafile.get_repositorylist():
                    if item.id == self.config.repos_id:
                        found = True
                        break

                if found is False:
                    repos_id = self.config.repos_id
                    jCP.printerrorln(3, f'Repos not found (Repos:{repos_id})')
                    return ErrorCode.valid_failed

        if show_success_message:
            jCP.println("OK")

        return ErrorCode.success

    def __applyoption_skipsamefile(self, value: str):
        self.skip_same_file = True
        return True

    def __applyoption_updatelinebystep(self, value: str):
        self.progressDownload.update_line_by_step = True
        self.progressUpload.update_line_by_step = True
        return True

    def __applyoption_repository(self, value: str):
        if self._set_repository(value) is False:
            return False
        return True

    def __applyoption_target(self, value: str):
        self.target = value
        return True

    def __applyoption_destination(self, value: str):
        self.dest = os.path.expanduser(value)
        return True

    def __applyoption_server(self, value: str):
        if self._set_server(value) is False:
            return False
        return True

    def __applyoption_connection(self, value: str):
        if self._set_server_and_repository(value) is False:
            return False
        return True

    def _set_server(self, argument: str):
        self.config.set_server(argument)
        if self.config.address == '':
            jCP.println('[error:0004] Unknown Server Name: ' + argument)
            return False

        self.seafile.set_address(self.config.address)
        self.seafile.set_api_token(self.config.token)

        if self.config.address == '':
            jCP.println('[ER] Addess is empty: ')
            return False

        return True

    def _set_repository(self, argument: str):
        self.config.set_repository(argument)
        if self.config.repos_id == '':
            jCP.println('[error:0005] Unknown Repository Name: ' + argument)
            return False

        self.seafile.set_repository_id(self.config.repos_id)
        return True

    def _set_server_and_repository(self, argument: str):
        self.config.set_server_and_repository(argument)
        if self.config.address == '':
            jCP.println('[error:xxxx] -c:{ConnectionName}')
            jCP.println('[error:xxxx] Unknown Connection Name: ' + argument)
            return False

        self.seafile.set_address(self.config.address)
        self.seafile.set_api_token(self.config.token)

        if self.config.address == '':
            jCP.println('[error:xxxx] Addess is empty: ')
            return False

        if self.config.repos_id == '':
            jCP.println('[error:xxxx] Repository ID is empty: ')
            return False

        self.seafile.set_repository_id(self.config.repos_id)
        return True


def run():
    main = J18Main()
    result = main.check_arguments()

    if result == jCPResult.TOO_MOUCH_COMMAND:
        jCP.printerrorln(ErrorCode.too_much_command.value,
                         'limit to only use a single command ')
        return

    if result == jCPResult.UNKNOWN_ARGUMENT:
        jCP.printerrorln(ErrorCode.unknown_argument.value,
                         'unknown argument')
        return

    if result == jCPResult.UNKNOWN_COMMAND:
        jCP.printerrorln(ErrorCode.unknown_argument.value,
                         'unknown command: ' + main.command)
        return

    if main.apply_options() is False:
        return

    if main.execute_command() == ErrorCode.command_failed:
        main.command_validate(False)


if __name__ == "__main__":
    run()
