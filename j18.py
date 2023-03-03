"""
 blog: https://junostudio.tistory.com/
 git: https://github.com/sjh9763/j18
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

        # 실행 환경 관련 인자를 먼저 불러온다
        for arg_index in range(1, len(sys.argv)):
            if sys.argv[arg_index][:3] == "-r:":
                if self.SetRepository(sys.argv[arg_index][3:]) == False: return
                continue

            if sys.argv[arg_index] == "-skip-same-file":
                self.skip_same_file = True
                continue

            if sys.argv[arg_index][:3] == "-t:":
                self.target = sys.argv[arg_index][3:]
                continue

            if sys.argv[arg_index][:3] == "-d:":
                self.dest = os.path.expanduser(sys.argv[arg_index][3:])
                continue

            if sys.argv[arg_index][:3] == "-s:":
                if self.SetServer(sys.argv[arg_index][3:]) == False: return
                continue

            if sys.argv[arg_index][:3] == "-c:":
                if self.SetServerAndRepository(sys.argv[arg_index][3:]) == False: return
                continue

        # 실행 관련 인자들을 찾는다 먼저 찾은 명령을 수행하고 끝낸다
        for arg_index in range(1, len(sys.argv)):
            if sys.argv[arg_index] == '--help':
                break

            if sys.argv[arg_index] == '--show-config':
                try:
                    current_locale = locale.getlocale()
                    with open (os.path.expanduser("~/.j18/") + "config", "r", encoding='UTF8') as config_file:
                        print(config_file.read())
                except:
                    print("Config file not found")
                return

            if sys.argv[arg_index] == '--get-token':
                if self.CommandGetToken() == False: return
                return
            
            if sys.argv[arg_index] == '--get-repo-list':
                if self.CommandGetRepoList() == False: return
                return

            if sys.argv[arg_index] == '--filedetail':
                if self.CommandFileDetail() == False: return
                return

            if sys.argv[arg_index] == '--download':
                if self.CommandDownload() == False: return
                return

            if sys.argv[arg_index] == '--ls':
                if self.CommandLs() == False: return
                return
        
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
            return
        
        if len(items) != 0:
            for item in items:
                if item.is_directory:
                    print("[D] " + item.name)
                else:
                    print("[F] " + item.name)

    def CommandFileDetail(self):
        info = self.seafile.GetFileDetail(self.target)
        if info != None:
            print(" ID: " + info.id)
            print(" Last Modifier Name: " + info.last_modifier_name)
            print(" Last Modified: " + str(info.last_modified))
            print(" Size: " + str(info.size))
        else:
            print("[ER] File not found : " + self.target)

    def CommandDownload(self):
        progress = jSeaFileDownloadProgress(self.download_progress)

        if self.seafile.Download(self.target, self.dest, self.skip_same_file, progress):
            print("download success")
        else:
            print("\n[ER] download failed")

if __name__ == "__main__": j18Main()
