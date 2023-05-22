"""
 blog: https://junostudio.tistory.com/
 git: https://github.com/junostudio3/j18
 j18 Main

"""

from enum import Enum
import locale
import os
from getpass import getpass

from jlib.seafile import jSeaFile, jSeaFileProgress
from j18config import j18Config
from jconsole.worker import jConsoleWorker, jConsoleParseResult
from environment import Environment
from res import res_from

class error_code(Enum):
    success = 0,
    valid_failed = 1,
    command_failed = 2,

class ConsolePorgress:
    def __init__(self):
        self.max_charector_count = 40
        self.pos = 0
        self.update_line_by_step = False

    def SetStartSummary(self, is_download:bool, total_size):
        if is_download:
            jConsoleWorker.PrintLn("download total data size = " + str(total_size))
        else:
            jConsoleWorker.PrintLn("upload total data size = " + str(total_size))

    def Start(self, file_name, total_size):
        self.total_size = total_size
        self.file_name = file_name
        self.pos = 0
        self.progress_pos = 0
        self.__DisplayProgress()

    def Proc(self, pos):
        old_progress = self.progress_pos
        self.UpdatePos(pos)
        if old_progress == self.progress_pos: return    # 너무 자주 갱신하지 말자. 깜빡거려서 보기 안 좋을 수 있으므로 #

        if self.update_line_by_step == False:
            jConsoleWorker.Print('\r')

        self.pos = pos
        self.__DisplayProgress()

    def End(self):
        if self.update_line_by_step == False:
            jConsoleWorker.Print('\r')

        self.UpdatePos(self.total_size)
        self.__DisplayProgress()

        if self.update_line_by_step == False:
            jConsoleWorker.PrintLn()

    def UpdatePos(self, pos):
        self.pos = pos
        self.progress_pos = 0
        if self.total_size > 0:
            self.progress_pos = int(self.pos * self.max_charector_count / self.total_size)

    def __DisplayProgress(self):
        jConsoleWorker.Print('[')

        for i in range(self.max_charector_count):
            if i < self.progress_pos:
                jConsoleWorker.Print('=')
            else:
                jConsoleWorker.Print(' ')

        percent = self.pos * 100.00 / self.total_size
        jConsoleWorker.Print(f'] {percent:.2f}%% ({self.pos} / {self.total_size}) ' + self.file_name)
        if self.update_line_by_step:
            jConsoleWorker.PrintLn()

class j18Main(jConsoleWorker):
    def __init__(self):
        self.console_progress = ConsolePorgress()
        self.seafile = jSeaFile()
        self.config = j18Config()
        self.target = "/"
        self.dest = os.getcwd()
        self.skip_same_file = False
        super().__init__()

    def GetOptions(self):
        # 실행 환경 관련 인자를 먼저 불러온다
        for option in self.options:
            key = option.key
            sub_option = option.value
            if key == "-skip-same-file":
                self.skip_same_file = True
            elif key == "-update-line-by-step":
                self.console_progress.update_line_by_step = True

            elif key == '-r':
                if self.SetRepository(sub_option) == False: return False

            elif key == "-t":
                self.target = sub_option

            elif key == "-d":
                self.dest = os.path.expanduser(sub_option)

            elif key == "-s":
                if self.SetServer(sub_option) == False: return False

            elif key == "-c":
                if self.SetServerAndRepository(sub_option) == False: return False
            else:
                jConsoleWorker.PrintLn('[ER] Unknown option: ' + key)
                return False

        return True

    def Do(self):
        if self.result == jConsoleParseResult.OK:
            command:str = self.command

            # 먼저 찾은 명령을 수행하고 끝낸다
            if command == '--version': return self.CommandVersion()
            if command == '--help': return self.CommandHelp()
            if command == '--show-config': return self.ShowConfig()
            if command == '--get-token': return self.CommandGetToken()
            if command == '--get-repo-list': return self.CommandGetRepoList()
            if command == '--filedetail': return self.CommandFileDetail()
            if command == '--download': return self.CommandDownload()
            if command == '--mkdir': return self.CommandCreateDirectory()
            if command == '--ls': return self.CommandLs()
            if command == '--upload': return self.CommandUpload()
            if command == '--validate': return self.CommandValidate()
        
            jConsoleWorker.PrintLn('[ER] Unknown Command: ' + command)
            return error_code.valid_failed
        elif self.result == jConsoleParseResult.TOO_MOUCH_COMMAND:
            jConsoleWorker.PrintLn('[ER] too mouch command')
            return error_code.valid_failed
            pass
        elif self.result == jConsoleParseResult.UNKNOWN_ARGUMENT:
            jConsoleWorker.PrintLn('[ER] Unknown argument')
            return error_code.valid_failed
            pass
        return error_code.valid_failed

    def GetArgOption(argument:str, option_head:str):
        head = argument[:len(option_head)].lower()
        if head != option_head: return None

        return argument[len(option_head):]

    def SetServer(self, argument:str):
        self.config.SetServer(argument)
        if self.config.address == '':
            jConsoleWorker.PrintErrorLn(4, 'Unknown Server Name: ' + argument)
            return False
        
        self.seafile.SetAddress(self.config.address)
        self.seafile.SetApiToken(self.config.token)

        if self.config.address == '':
            jConsoleWorker.PrintLn('[ER] Addess is empty: ')
            return False
        
        return True
    
    def SetRepository(self, argument:str):
        self.config.SetRepository(argument)
        if self.config.repos_id == '':
            jConsoleWorker.PrintErrorLn(5, 'Unknown Repository Name: ' + argument)
            return False
        
        self.seafile.SetRepositoryId(self.config.repos_id)
        return True
    
    def SetServerAndRepository(self, argument:str):
        self.config.SetServerAndRepository(argument)
        if self.config.address == '':
            jConsoleWorker.PrintErrorLn(-1, '--c{ConnectionName}')
            jConsoleWorker.PrintErrorLn(-1, 'Unknown Connection Name: ' + argument)
            return False
        
        self.seafile.SetAddress(self.config.address)
        self.seafile.SetApiToken(self.config.token)

        if self.config.address == '':
            jConsoleWorker.PrintLn('[error:xxxx] Addess is empty: ')
            return False
        
        if self.config.repos_id == '':
            jConsoleWorker.PrintLn('[error:xxxx] Repository ID is empty: ')
            return False
        
        self.seafile.SetRepositoryId(self.config.repos_id)
        return True

    def CommandVersion(self):
        jConsoleWorker.PrintLn(Environment.version)
        return error_code.success
    
    def CommandHelp(self):
        jConsoleWorker.PrintLn('j18 version ' + Environment.version + ' copyright(c) 2023. juno-studio all rights reserved.')
        jConsoleWorker.PrintLn()

        try:
            current_locale = str(locale.getlocale()[0])

            # Windows에서는 locale 이름이 다르다
            if current_locale == "Korean_Korea": current_locale = "ko_KR"

            help_file_path = res_from("resource/help_" + current_locale + ".txt")
            with open (help_file_path, "r", encoding='UTF8') as help_file:
                jConsoleWorker.PrintLn(help_file.read())
        except:
            with open (res_from("resource/help_en_US.txt"), "r", encoding='UTF8') as help_file:
                jConsoleWorker.PrintLn(help_file.read())

        return error_code.success

    def ShowConfig(self):
        try:
            current_locale = locale.getlocale()
            with open (os.path.expanduser("~/.j18/") + "config", "r", encoding='UTF8') as config_file:
                jConsoleWorker.PrintLn(config_file.read())
        except:
            jConsoleWorker.PrintLn("Config file not found")
        return error_code.success
    
    def CommandGetToken(self):
        if self.config.address == "":
            jConsoleWorker.PrintErrorLn(-1, 'The following options are required.')
            jConsoleWorker.PrintErrorLn(-1, 'option: --s{ServerName}')
            return error_code.valid_failed
        
        user_name = input("user_name:")
        password = getpass("password:")
        token = self.seafile.GetApiToken(user_name, password)
        if token == "":
            jConsoleWorker.PrintErrorLn(-1, 'get-token failed')
            return error_code.command_failed
        
        jConsoleWorker.PrintLn('token:' + token)
        return error_code.success

    def CommandGetRepoList(self):
        if self.config.address == "":
            jConsoleWorker.PrintLn('[error:xxxx] The following options are required.')
            jConsoleWorker.PrintLn('[error:xxxx] option: --s{ServerName}')
            return error_code.valid_failed
        
        items = self.seafile.GetRepositoryList()
        if items == None:
            jConsoleWorker.PrintErrorLn(-1, 'Get Repository List Failed')
            return error_code.command_failed
        
        for item in items:
            jConsoleWorker.PrintLn(item.name + "(" + item.permission + ") -> " + item.id)

        return error_code.success
    
    def CommandLs(self):
        items = self.seafile.GetListItemsInDirectory(self.target)
        if items == None:
            jConsoleWorker.PrintErrorLn(-1, f"Get Item List (Target Directory={self.target})")
            return error_code.command_failed
        
        if len(items) != 0:
            for item in items:
                if item.is_directory:
                    jConsoleWorker.PrintLn("[D] " + item.name)
                else:
                    jConsoleWorker.PrintLn("[F] " + item.name + " (" + str(item.size) + " bytes)")

        return error_code.success

    def CommandFileDetail(self):
        info = self.seafile.GetFileDetail(self.target)
        if info != None:
            jConsoleWorker.PrintLn(" ID: " + info.id)
            jConsoleWorker.PrintLn(" Last Modifier Name: " + info.last_modifier_name)
            jConsoleWorker.PrintLn(" Last Modified: " + str(info.last_modified))
            jConsoleWorker.PrintLn(" Size: " + str(info.size))
            return error_code.success
        else:
            jConsoleWorker.PrintErrorLn(-1, 'File not found : ' + self.target)
            return error_code.command_failed

    def CommandCreateDirectory(self):
        success = self.seafile.CreateDirectory(self.target)
        if success:
            jConsoleWorker.PrintLn("Success")
            return error_code.success
        else:
            jConsoleWorker.PrintErrorLn(-1, 'Failed to Create Directory : ' + self.target)
            return error_code.command_failed

    def CommandDownload(self):
        progress = jSeaFileProgress(self.console_progress)

        if self.seafile.Download(self.target, self.dest, self.skip_same_file, progress):
            jConsoleWorker.PrintLn("download success")
            return error_code.success
        else:
            jConsoleWorker.PrintLn()
            jConsoleWorker.PrintErrorLn(-1, 'download failed')
            return error_code.command_failed

    def CommandUpload(self):
        link:str = self.seafile.GetUploadFileLink(self.target)
        if link == None:
            jConsoleWorker.PrintErrorLn(-1, 'get upload file link failed')
            return error_code.command_failed        

        progress = jSeaFileProgress(self.console_progress)

        if jSeaFile.UploadFile(link, self.target, self.dest, progress):
            jConsoleWorker.PrintLn("upload success")
            return error_code.success
        else:
            jConsoleWorker.PrintLn()
            jConsoleWorker.PrintErrorLn(-1, 'upload failed');
            return error_code.command_failed        

    def CommandValidate(self, show_success_message = True):
        if self.seafile.CheckAddress() == False:
            jConsoleWorker.PrintErrorLn(1, 'Connect Failed (Check Address:' + self.config.address + ')')
            return error_code.valid_failed
        
        if self.config.token != '':
            # Token이 세팅되어 있으니 Token 문제 없나 체크
            if self.seafile.CheckToken() == False:
                jConsoleWorker.PrintErrorLn(2, 'Permission declined (Check Token:' + self.config.token + ')')
                return error_code.valid_failed
            
            # Repos가 세팅되어 있으니 Repos 체크
            if self.config.repos_id != '':
                found = False
                for item in self.seafile.GetRepositoryList():
                    if item.id == self.config.repos_id:
                        found = True
                        break
                
                if found == False:
                    jConsoleWorker.PrintErrorLn(3, 'Repos not found (Check Repos:' + self.config.repos_id + ')')
                    return error_code.valid_failed
                
        if show_success_message:
            jConsoleWorker.PrintLn("OK")
        
        return error_code.success

if __name__ == "__main__":
    main = j18Main()
    if main.GetOptions() == True:
        if main.Do() == error_code.command_failed:
            main.CommandValidate(False)
