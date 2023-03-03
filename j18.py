"""
 blog: https://junostudio.tistory.com/
 git: https://github.com/junostudio3/j18
 j18 Main

"""

import locale
import os
import sys
from getpass import getpass

from jlib.seafile import jSeaFile, jSeaFileDownloadProgress
from j18config import j18Config
from environment import Environment
from res import res_from

class j18DownloadPorgress():
    def __init__(self):
        self.max_charector_count = 40
        self.pos = 0

    def SetStartSummary(self, total_size):
        print("download total data size = " + str(total_size))

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

        print('\r', end='')
        self.pos = pos
        self.__DisplayProgress()

    def End(self):
        print('\r', end='')
        self.UpdatePos(self.total_size)
        self.__DisplayProgress()
        print('')

    def UpdatePos(self, pos):
        self.pos = pos
        self.progress_pos = 0
        if self.total_size > 0:
            self.progress_pos = int(self.pos * self.max_charector_count / self.total_size)

    def __DisplayProgress(self):
        print('[', end='')

        for i in range(self.max_charector_count):
            if i < self.progress_pos:
                print('=', end='')
            else:
                print(' ', end='')

        percent = self.pos * 100.00 / self.total_size
        print(f'] {percent:.2f}%% ({self.pos} / {self.total_size}) ' + self.file_name, end='')

class j18Main():
    def __init__(self):
        self.download_progress = j18DownloadPorgress()
        self.seafile = jSeaFile()
        self.config = j18Config()
        self.target = "/"
        self.dest = os.getcwd()
        self.skip_same_file = False
        self.arguments = sys.argv

    def GetOptions(self):
        # 실행 환경 관련 인자를 먼저 불러온다
        arg_index = -1

        while True:
            arg_index = arg_index + 1
            if arg_index >= len(self.arguments):
                break

            argument = self.arguments[arg_index]

            if argument.lower() == "-skip-same-file":
                self.skip_same_file = True

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
                continue

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
        if command == '--ls': return self.CommandLs()
        
        print('[ER] Unknown Command: ' + command)
        return False

    def GetArgOption(argument:str, option_head:str):
        head = argument[:len(option_head)].lower()
        if head != option_head: return None

        return argument[len(option_head):]

    def SetServer(self, argument:str):
        self.config.SetServer(argument)
        if self.config.address == '':
            print('[ER] --s{ServerName}')
            print('[ER] Unknown Server Name: ' + argument)
            return False
        
        self.seafile.SetAddress(self.config.address)
        self.seafile.SetApiToken(self.config.token)

        if self.seafile.CheckAddress() == False:
            print("[ER] Connect Failed")
            return False
        
        return True
    
    def SetRepository(self, argument:str):
        self.config.SetRepository(argument)
        if self.config.repos_id == '':
            print('[ER] --s{ServerName}')
            print('[ER] Unknown Repository Name: ' + argument)
            return False
        
        self.seafile.SetRepositoryId(self.config.repos_id)
        return True
    
    def SetServerAndRepository(self, argument:str):
        self.config.SetServerAndRepository(argument)
        if self.config.address == '':
            print('[ER] --c{ConnectionName}')
            print('[ER] Unknown Connection Name: ' + argument)
            return False
        
        self.seafile.SetAddress(self.config.address)
        self.seafile.SetApiToken(self.config.token)

        if self.seafile.CheckAddress() == False:
            print("[ER] Connect Failed")
            return False
        
        if self.config.repos_id == '':
            print('[ER] Repository ID is empty: ')
            return False
        
        self.seafile.SetRepositoryId(self.config.repos_id)
        return True

    def CommandVersion(self):
        print(Environment.version)
        return True
    
    def CommandHelp(self):
        print("j18 version " + Environment.version + " copyright(c) 2023. juno-studio all rights reserved.")

        try:
            current_locale = str(locale.getlocale()[0])

            # Windows에서는 locale 이름이 다르다
            if current_locale == "Korean_Korea": current_locale = "ko_KR"

            help_file_path = res_from("resource/help_" + current_locale + ".txt")
            with open (help_file_path, "r", encoding='UTF8') as help_file:
                print(help_file.read())
        except:
            with open (res_from("resource/help_en_US.txt"), "r", encoding='UTF8') as help_file:
                print(help_file.read())

        return True

    def ShowConfig(self):
        try:
            current_locale = locale.getlocale()
            with open (os.path.expanduser("~/.j18/") + "config", "r", encoding='UTF8') as config_file:
                print(config_file.read())
        except:
            print("Config file not found")
        return True
    
    def CommandGetToken(self):
        if self.config.address == "":
            print('[ER] The following options are required.')
            print('[ER] option: --s{ServerName}')
            return False
        
        user_name = input("user_name:")
        password = getpass("password:")
        token = self.seafile.GetApiToken(user_name, password)
        if token == "":
            print('[ER] get-token failed')
            return False
        
        print('token:' + token)
        return True

    def CommandGetRepoList(self):
        if self.config.address == "":
            print('[ER] The following options are required.')
            print('[ER] option: --s{ServerName}')
            return False
        
        if self.seafile.CheckToken() == False:
            print("[ER] Permission declined")
            return
        
        items = self.seafile.GetRepositoryList()
        if items == None:
            print("[ER] Get Repository List Failed")
            return
        
        for item in items:
            print(item.name + "(" + item.permission + ") -> " + item.id)

        return True
    
    def CommandLs(self):
        items = self.seafile.GetListItemsInDirectory(self.target)
        if items == None:
            print(f"[ER] Get Item List (Target Directory={self.target})")
            return False
        
        if len(items) != 0:
            for item in items:
                if item.is_directory:
                    print("[D] " + item.name)
                else:
                    print("[F] " + item.name)

        return True

    def CommandFileDetail(self):
        info = self.seafile.GetFileDetail(self.target)
        if info != None:
            print(" ID: " + info.id)
            print(" Last Modifier Name: " + info.last_modifier_name)
            print(" Last Modified: " + str(info.last_modified))
            print(" Size: " + str(info.size))
            return True
        else:
            print("[ER] File not found : " + self.target)
            return False

    def CommandDownload(self):
        progress = jSeaFileDownloadProgress(self.download_progress)

        if self.seafile.Download(self.target, self.dest, self.skip_same_file, progress):
            print("download success")
            return True
        else:
            print("\n[ER] download failed")
            return False

if __name__ == "__main__":
    main = j18Main()
    if main.GetOptions() == True:
        main.Do()
