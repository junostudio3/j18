"""
 blog: https://junostudio.tistory.com/
 git: https://github.com/junostudio3/j18
 j18 Main

"""

from enum import Enum
import locale
import os
from getpass import getpass

from jconsole.parser import jConsoleParser as jCP
from jconsole.parser import jConsoleParseResult as jCPResult
from seafile import jSeaFile, jSeaFileProgress
from environment import Environment
from res import LoadResourceText
from j18console.config import j18Config
from j18console.progress import ConsolePorgress


class error_code(Enum):
    success = 0
    too_much_command = 1
    unknown_argument = 2
    option_is_wrong = 3
    valid_failed = 4
    command_failed = 5
    option_duplication = 6


class j18Main (jCP):
    def __init__(self):
        super().__init__()
        self.progressDownload = ConsolePorgress(True)
        self.progressUpload = ConsolePorgress(False)
        self.seafile = jSeaFile()
        self.config = j18Config()
        self.target = "/"
        self.dest = os.getcwd()
        self.skip_same_file = False
        self.AddCommandLink('--help', self.__CommandHelp)
        self.AddCommandLink('--version', self.__CommandVersion)
        self.AddCommandLink('--show-config', self.__CommandShowConfig)
        self.AddCommandLink('--get-token', self.__CommandGetToken)
        self.AddCommandLink('--get-repo-list', self.__CommandGetRepoList)
        self.AddCommandLink('--filedetail', self.__CommandFileDetail)
        self.AddCommandLink('--download', self.__CommandDownload)
        self.AddCommandLink('--mkdir', self.__CommandCreateDirectory)
        self.AddCommandLink('--ls', self.__CommandLs)
        self.AddCommandLink('--upload', self.__CommandUpload)
        self.AddCommandLink('--validate', self.CommandValidate)

    def ApplyOptions(self):
        # 다음순서 Option을 체크하며 순서대로 읽는다
        options: dict = {
            "-skip-same-file": self.__ApplyOptionSkipSameFile,
            "-update-line-by-step": self.__ApplyOptionUpdateLineByStep,
            "-r": self.__ApplyOptionRepository,
            "-t": self.__ApplyOptionTarget,
            "-d": self.__ApplyOptionDestination,
            "-s": self.__ApplyOptionServer,
            "-c": self.__ApplyOptionConnection
            }

        for option, function in options.items():
            res = self.CheckOption(option)
            if res.result != jCPResult.OK:
                jCP.PrintErrorLn(error_code.option_duplication.value,
                                 res.message)
                return False

            if not res.is_exist:
                continue

            if not function(res.option_value):
                jCP.PrintErrorLn(error_code.option_is_wrong.value,
                                 'option is wrong: ' + option)
                return False

        if len(self.check_waiting_options) == 0:
            return True

        optionKey = self.check_waiting_options[0].key

        jCP.PrintErrorLn(error_code.unknown_argument.value,
                         "unkown argument: " + optionKey)
        return False

    def __CommandHelp(self):
        version = Environment.version
        jCP.Print(f'j18 version {version} copyright(c) 2023. ')
        jCP.PrintLn('juno-studio all rights reserved.')
        jCP.PrintLn()

        currentLocale = str(locale.getlocale()[0])

        # Windows에서는 locale 이름이 다르다
        if currentLocale == "Korean_Korea":
            currentLocale = "ko_KR"

        text = LoadResourceText(f"help_{currentLocale}.txt")
        if text == "":
            text = LoadResourceText("help_en_US.txt")

        jCP.PrintLn(text)

        return error_code.success

    def __CommandVersion(self):
        jCP.PrintLn(Environment.version)
        return error_code.success

    def __CommandShowConfig(self):
        try:
            with open(os.path.expanduser("~/.j18/") + "config",
                      "r",
                      encoding='UTF8') as config_file:
                jCP.PrintLn(config_file.read())
        except Exception:
            jCP.PrintLn("Config file not found")
        return error_code.success

    def __CommandGetToken(self):
        if self.config.address == "":
            jCP.PrintErrorLn(-1, 'The following options are required.')
            jCP.PrintErrorLn(-1, 'option: -s:{ServerName}')
            return error_code.valid_failed

        user_name = input("user_name:")
        password = getpass("password:")
        token = self.seafile.GetApiToken(user_name, password)
        if token == "":
            jCP.PrintErrorLn(-1, 'get-token failed')
            return error_code.command_failed

        jCP.PrintLn('token:' + token)
        return error_code.success

    def __CommandGetRepoList(self):
        if self.config.address == "":
            jCP.PrintLn('[error:xxxx] The following options are required.')
            jCP.PrintLn('[error:xxxx] option: -s:{ServerName}')
            return error_code.valid_failed

        items = self.seafile.GetRepositoryList()
        if items is None:
            jCP.PrintErrorLn(-1, 'Get Repository List Failed')
            return error_code.command_failed

        for item in items:
            jCP.PrintLn(item.name + "(" + item.permission + ") -> " + item.id)

        return error_code.success

    def __CommandFileDetail(self):
        info = self.seafile.GetFileDetail(self.target)
        if info is not None:
            jCP.PrintLn(" ID: " + info.id)
            jCP.PrintLn(" Last Modifier Name: " + info.last_modifier_name)
            jCP.PrintLn(" Last Modified: " + str(info.last_modified))
            jCP.PrintLn(" Size: " + str(info.size))
            return error_code.success
        else:
            jCP.PrintErrorLn(-1, 'File not found : ' + self.target)
            return error_code.command_failed

    def __CommandDownload(self):
        progress = jSeaFileProgress(self.progressDownload)

        if self.seafile.Download(self.target,
                                 self.dest,
                                 self.skip_same_file,
                                 progress):
            jCP.PrintLn("download success")
            return error_code.success
        else:
            jCP.PrintLn("\n[error:xxxx] download failed")
            return error_code.command_failed

    def __CommandCreateDirectory(self):
        success = self.seafile.CreateDirectory(self.target)
        if success:
            jCP.PrintLn("Success")
            return error_code.success
        else:
            jCP.PrintErrorLn(-1, 'Failed to Create Directory : ' + self.target)
            return error_code.command_failed

    def __CommandLs(self):
        items = self.seafile.GetListItemsInDirectory(self.target)
        if items is None:
            folder = self.target
            jCP.PrintErrorLn(-1, f"Get Item List (Target Directory={folder})")
            return error_code.command_failed

        if len(items) != 0:
            for item in items:
                if item.is_directory:
                    jCP.PrintLn("[D] " + item.name)
                else:
                    jCP.PrintLn(f"[F] {item.name} ({item.size} bytes)")

        return error_code.success

    def __CommandUpload(self):
        link: str = self.seafile.GetUploadFileLink(self.target)
        if link is None:
            jCP.PrintErrorLn(-1, 'get upload file link failed')
            return error_code.command_failed

        progress = jSeaFileProgress(self.progressUpload)

        if jSeaFile.UploadFile(link, self.target, self.dest, progress):
            jCP.PrintLn("upload success")
            return error_code.success
        else:
            jCP.PrintLn()
            jCP.PrintErrorLn(-1, 'upload failed')
            return error_code.command_failed

    def CommandValidate(self, show_success_message: bool = True):
        if self.seafile.CheckAddress() is False:
            address = self.config.address
            jCP.PrintErrorLn(1, f'Connect Failed (Address:{address})')
            return error_code.valid_failed

        if self.config.token != '':
            # Token이 세팅되어 있으니 Token 문제 없나 체크
            if self.seafile.CheckToken() is False:
                token = self.config.token
                jCP.PrintErrorLn(2, f'Permission declined (Token:{token})')
                return error_code.valid_failed

            # Repos가 세팅되어 있으니 Repos 체크
            if self.config.repos_id != '':
                found = False
                for item in self.seafile.GetRepositoryList():
                    if item.id == self.config.repos_id:
                        found = True
                        break

                if found is False:
                    reposId = self.config.repos_id
                    jCP.PrintErrorLn(3, f'Repos not found (Repos:{reposId})')
                    return error_code.valid_failed

        if show_success_message:
            jCP.PrintLn("OK")

        return error_code.success

    def __ApplyOptionSkipSameFile(self, value: str):
        self.skip_same_file = True
        return True

    def __ApplyOptionUpdateLineByStep(self, value: str):
        self.progressDownload.update_line_by_step = True
        self.progressUpload.update_line_by_step = True
        return True

    def __ApplyOptionRepository(self, value: str):
        if self._SetRepository(value) is False:
            return False
        return True

    def __ApplyOptionTarget(self, value: str):
        self.target = value
        return True

    def __ApplyOptionDestination(self, value: str):
        self.dest = os.path.expanduser(value)
        return True

    def __ApplyOptionServer(self, value: str):
        if self._SetServer(value) is False:
            return False
        return True

    def __ApplyOptionConnection(self, value: str):
        if self._SetServerAndRepository(value) is False:
            return False
        return True

    def _SetServer(self, argument: str):
        self.config.SetServer(argument)
        if self.config.address == '':
            jCP.PrintLn('[error:0004] Unknown Server Name: ' + argument)
            return False

        self.seafile.SetAddress(self.config.address)
        self.seafile.SetApiToken(self.config.token)

        if self.config.address == '':
            jCP.PrintLn('[ER] Addess is empty: ')
            return False

        return True

    def _SetRepository(self, argument: str):
        self.config.SetRepository(argument)
        if self.config.repos_id == '':
            jCP.PrintLn('[error:0005] Unknown Repository Name: ' + argument)
            return False

        self.seafile.SetRepositoryId(self.config.repos_id)
        return True

    def _SetServerAndRepository(self, argument: str):
        self.config.SetServerAndRepository(argument)
        if self.config.address == '':
            jCP.PrintLn('[error:xxxx] -c:{ConnectionName}')
            jCP.PrintLn('[error:xxxx] Unknown Connection Name: ' + argument)
            return False

        self.seafile.SetAddress(self.config.address)
        self.seafile.SetApiToken(self.config.token)

        if self.config.address == '':
            jCP.PrintLn('[error:xxxx] Addess is empty: ')
            return False

        if self.config.repos_id == '':
            jCP.PrintLn('[error:xxxx] Repository ID is empty: ')
            return False

        self.seafile.SetRepositoryId(self.config.repos_id)
        return True


def Run():
    main = j18Main()
    result = main.CheckArguments()

    if result == jCPResult.TOO_MOUCH_COMMAND:
        jCP.PrintErrorLn(error_code.too_much_command.value,
                         'limit to only use a single command ')
        return

    if result == jCPResult.UNKNOWN_ARGUMENT:
        jCP.PrintErrorLn(error_code.unknown_argument.value,
                         'unknown argument')
        return

    if result == jCPResult.UNKNOWN_COMMAND:
        jCP.PrintErrorLn(error_code.unknown_argument.value,
                         'unknown command: ' + main.command)
        return

    if main.ApplyOptions() is False:
        return

    if main.ExecuteCommand() == error_code.command_failed:
        main.CommandValidate(False)


if __name__ == "__main__":
    Run()
