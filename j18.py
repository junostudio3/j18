"""
 blog: https://junostudio.tistory.com/
 git: https://github.com/junostudio3/j18
 j18 Main

"""

from enum import Enum
import locale
import os
import sys
from getpass import getpass

from jlib.seafile import jSeaFile, jSeaFileProgress
from j18config import j18Config
from console import Console
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
            Console.PrintLn("download total data size = " + str(total_size))
        else:
            Console.PrintLn("upload total data size = " + str(total_size))

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
            Console.Print('\r')

        self.pos = pos
        self.__DisplayProgress()

    def End(self):
        if self.update_line_by_step == False:
            Console.Print('\r')

        self.UpdatePos(self.total_size)
        self.__DisplayProgress()

        if self.update_line_by_step == False:
            Console.PrintLn()

    def UpdatePos(self, pos):
        self.pos = pos
        self.progress_pos = 0
        if self.total_size > 0:
            self.progress_pos = int(self.pos * self.max_charector_count / self.total_size)

    def __DisplayProgress(self):
        Console.Print('[')

        for i in range(self.max_charector_count):
            if i < self.progress_pos:
                Console.Print('=')
            else:
                Console.Print(' ')

        percent = self.pos * 100.00 / self.total_size
        Console.Print(f'] {percent:.2f}%% ({self.pos} / {self.total_size}) ' + self.file_name)
        if self.update_line_by_step:
            Console.PrintLn()

class j18Main:
    def __init__(self):
        self.console_progress = ConsolePorgress()
        self.seafile = jSeaFile()
        self.config = j18Config()
        self.target = "/"
        self.dest = os.getcwd()
        self.skip_same_file = False
        self.arguments = sys.argv

    def GetOptions(self):
        # 실행 환경 관련 인자를 먼저 불러온다
        arg_index = 0

        while True:
            arg_index = arg_index + 1
            if arg_index >= len(self.arguments):
                break

            argument = self.arguments[arg_index]

            if argument[:2] == '--':
                # 명령을 일단 넘어가자
                continue

            if argument.lower() == "-skip-same-file":
                self.skip_same_file = True

            elif argument.lower() == "-update-line-by-step":
                self.console_progress.update_line_by_step = True

            elif (option := __class__.GetArgOption(argument, "-r:")) != None:
                if self.SetRepository(option) == False: return False

            elif (option := __class__.GetArgOption(argument, "-t:")) != None:
                self.target = option

            elif (option := __class__.GetArgOption(argument, "-d:")) != None:
                self.dest = os.path.expanduser(option)

            elif (option := __class__.GetArgOption(argument, "-s:")) != None:
                if self.SetServer(option) == False: return False

            elif (option := __class__.GetArgOption(argument, "-c:")) != None:
                if self.SetServerAndRepository(option) == False: return False
            else:
                Console.PrintLn('[ER] Unknown option: ' + argument)
                return False

            # 처리된 argument는 제거한다
            del self.arguments[arg_index]
            arg_index = arg_index - 1

        return True

    def Do(self):
        # command argument를 찾는다
        command:str = '--help'
        for arg_index in range(1, len(self.arguments)):
            argument = self.arguments[arg_index].lower()
            if argument[:2] == '--':
                command = argument
                break

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
        
        Console.PrintLn('[ER] Unknown Command: ' + command)
        return error_code.valid_failed

    def GetArgOption(argument:str, option_head:str):
        head = argument[:len(option_head)].lower()
        if head != option_head: return None

        return argument[len(option_head):]

    def SetServer(self, argument:str):
        self.config.SetServer(argument)
        if self.config.address == '':
            Console.PrintLn('[error:0004] Unknown Server Name: ' + argument)
            return False
        
        self.seafile.SetAddress(self.config.address)
        self.seafile.SetApiToken(self.config.token)

        if self.config.address == '':
            Console.PrintLn('[ER] Addess is empty: ')
            return False
        
        return True
    
    def SetRepository(self, argument:str):
        self.config.SetRepository(argument)
        if self.config.repos_id == '':
            Console.PrintLn('[error:0005] Unknown Repository Name: ' + argument)
            return False
        
        self.seafile.SetRepositoryId(self.config.repos_id)
        return True
    
    def SetServerAndRepository(self, argument:str):
        self.config.SetServerAndRepository(argument)
        if self.config.address == '':
            Console.PrintLn('[error:xxxx] --c{ConnectionName}')
            Console.PrintLn('[error:xxxx] Unknown Connection Name: ' + argument)
            return False
        
        self.seafile.SetAddress(self.config.address)
        self.seafile.SetApiToken(self.config.token)

        if self.config.address == '':
            Console.PrintLn('[error:xxxx] Addess is empty: ')
            return False
        
        if self.config.repos_id == '':
            Console.PrintLn('[error:xxxx] Repository ID is empty: ')
            return False
        
        self.seafile.SetRepositoryId(self.config.repos_id)
        return True

    def CommandVersion(self):
        Console.PrintLn(Environment.version)
        return error_code.success
    
    def CommandHelp(self):
        Console.PrintLn('j18 version ' + Environment.version + ' copyright(c) 2023. juno-studio all rights reserved.')
        Console.PrintLn()

        try:
            current_locale = str(locale.getlocale()[0])

            # Windows에서는 locale 이름이 다르다
            if current_locale == "Korean_Korea": current_locale = "ko_KR"

            help_file_path = res_from("resource/help_" + current_locale + ".txt")
            with open (help_file_path, "r", encoding='UTF8') as help_file:
                Console.PrintLn(help_file.read())
        except:
            with open (res_from("resource/help_en_US.txt"), "r", encoding='UTF8') as help_file:
                Console.PrintLn(help_file.read())

        return error_code.success

    def ShowConfig(self):
        try:
            current_locale = locale.getlocale()
            with open (os.path.expanduser("~/.j18/") + "config", "r", encoding='UTF8') as config_file:
                Console.PrintLn(config_file.read())
        except:
            Console.PrintLn("Config file not found")
        return error_code.success
    
    def CommandGetToken(self):
        if self.config.address == "":
            Console.PrintLn('[error:xxxx] The following options are required.')
            Console.PrintLn('[error:xxxx] option: --s{ServerName}')
            return error_code.valid_failed
        
        user_name = input("user_name:")
        password = getpass("password:")
        token = self.seafile.GetApiToken(user_name, password)
        if token == "":
            Console.PrintLn('[error:xxxx] get-token failed')
            return error_code.command_failed
        
        Console.PrintLn('token:' + token)
        return error_code.success

    def CommandGetRepoList(self):
        if self.config.address == "":
            Console.PrintLn('[error:xxxx] The following options are required.')
            Console.PrintLn('[error:xxxx] option: --s{ServerName}')
            return error_code.valid_failed
        
        items = self.seafile.GetRepositoryList()
        if items == None:
            Console.PrintLn("[error:xxxx] Get Repository List Failed")
            return error_code.command_failed
        
        for item in items:
            Console.PrintLn(item.name + "(" + item.permission + ") -> " + item.id)

        return error_code.success
    
    def CommandLs(self):
        items = self.seafile.GetListItemsInDirectory(self.target)
        if items == None:
            Console.PrintLn(f"[error:xxxx] Get Item List (Target Directory={self.target})")
            return error_code.command_failed
        
        if len(items) != 0:
            for item in items:
                if item.is_directory:
                    Console.PrintLn("[D] " + item.name)
                else:
                    Console.PrintLn("[F] " + item.name + " (" + str(item.size) + " bytes)")

        return error_code.success

    def CommandFileDetail(self):
        info = self.seafile.GetFileDetail(self.target)
        if info != None:
            Console.PrintLn(" ID: " + info.id)
            Console.PrintLn(" Last Modifier Name: " + info.last_modifier_name)
            Console.PrintLn(" Last Modified: " + str(info.last_modified))
            Console.PrintLn(" Size: " + str(info.size))
            return error_code.success
        else:
            Console.PrintLn("[error:xxxx] File not found : " + self.target)
            return error_code.command_failed

    def CommandCreateDirectory(self):
        success = self.seafile.CreateDirectory(self.target)
        if success:
            Console.PrintLn("Success")
            return error_code.success
        else:
            Console.PrintLn("[error:xxxx] Failed to Create Directory : " + self.target)
            return error_code.command_failed

    def CommandDownload(self):
        progress = jSeaFileProgress(self.console_progress)

        if self.seafile.Download(self.target, self.dest, self.skip_same_file, progress):
            Console.PrintLn("download success")
            return error_code.success
        else:
            Console.PrintLn("\n[error:xxxx] download failed")
            return error_code.command_failed

    def CommandUpload(self):
        link:str = self.seafile.GetUploadFileLink(self.target)
        if link == None:
            Console.PrintLn("[error:xxxx] get upload file link failed")
            return error_code.command_failed        

        progress = jSeaFileProgress(self.console_progress)

        if jSeaFile.UploadFile(link, self.target, self.dest, progress):
            Console.PrintLn("upload success")
            return error_code.success
        else:
            Console.PrintLn("\n[error:xxxx] upload failed")
            return error_code.command_failed        

    def CommandValidate(self, show_success_message = True):
        if self.seafile.CheckAddress() == False:
            Console.PrintLn('[error:0001] Connect Failed (Check Address:' + self.config.address + ')')
            return error_code.valid_failed
        
        if self.config.token != '':
            # Token이 세팅되어 있으니 Token 문제 없나 체크
            if self.seafile.CheckToken() == False:
                Console.PrintLn('[error:0002] Permission declined (Check Token:' + self.config.token + ')')
                return error_code.valid_failed
            
            # Repos가 세팅되어 있으니 Repos 체크
            if self.config.repos_id != '':
                found = False
                for item in self.seafile.GetRepositoryList():
                    if item.id == self.config.repos_id:
                        found = True
                        break
                
                if found == False:
                    Console.PrintLn('[error:0003] Repos not found (Check Repos:' + self.config.repos_id + ')')
                    return error_code.valid_failed
                
        if show_success_message:
            Console.PrintLn("OK")
        
        return error_code.success

if __name__ == "__main__":
    main = j18Main()
    if main.GetOptions() == True:
        if main.Do() == error_code.command_failed:
            main.CommandValidate(False)
