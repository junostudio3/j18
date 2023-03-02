"""
 blog: https://junostudio.tistory.com/
 git: https://github.com/sjh9763/j18
    Seafile Web API를 이용하여 파일을 다운 받거나 정보를 얻는 등의 작업을 하기 위한 클래스이다
    API Documents: https://download.seafile.com/published/web-api/home.md
"""

from datetime import datetime, timedelta, timezone
import time
import os
import json
import urllib.request
import urllib.parse

class jSeaFileDownloadProgress:
    def __init__(self, target):
        self.target = target
        self.first_run = True

    def Doing(self, block_num, block_size, total_size):
        if self.first_run == True:
            self.target.Start(total_size)
            self.first_run = False

        downloaded = min(total_size, block_num * block_size)
        self.target.Proc(downloaded)

class jSeaRepositoryInfo:
    def __init__(self):
        self.id = ""
        self.name = ""
        self.permission = ""

class jSeaFileInfo:
    def __init__(self):
        self.id = ""
        self.last_modifier_name = ""
        self.last_modified:datetime  = None
        self.size = 0

class jSeaFileItem:
    def __init__(self, full_path:str, name:str, is_directory:bool):
        self.full_path = full_path
        self.name = name
        self.is_directory = is_directory

class jSeaFile:
    url:str = ""
    api_token:str = ""
    repo_id:str = ""
    KST = timezone(timedelta(hours=9))

    def SetAddress(self, url:str):
        self.url = url

    def SetApiToken(self, token):
        self.api_token = token

    def SetRepositoryId(self, repo_id):
        self.repo_id = repo_id

    def GetApiToken(self, user_name:str, password:str):
        try:
            post_data = urllib.parse.urlencode({'username':user_name, 'password':password}).encode('UTF-8')
            url = urllib.request.Request(self.url + '/api2/auth-token/', post_data)
            connection:urllib.request._UrlopenRet = urllib.request.urlopen(url)

            data = connection.read().decode("utf-8")
            json_object = json.loads(data)
            return json_object['token']
        except:
            return ""
        
    def CheckAddress(self):
        # Ping Pong Message를 통해 접속가능한가 체크한다
        if self.Ping() != "pong":
            return False
        return True
    
    def CheckToken(self):
        # Auth Ping Pong Message를 통해 접속가능한가 체크한다
        if self.AuthPing() != "pong":
            return False
        return True

    def IsExistDirectory(self, dir_path:str):
        # /dir/detail 명령이 동작하지 않아서 /dir/ 명령을 사용했다
        json_object = self.__GetResponseJsonUsingToken('/api2/repos/' + self.repo_id + '/dir/', {'p':dir_path})
        if json_object == None: return False
        return True

    def IsExistFile(self, file_path:str):
        # /file/detail 명령으로 체크함
        if self.GetFileDetail(file_path) == None: return False
        return True

    def DownloadFile(self, file_path:str, output_folder_path:str, progress:jSeaFileDownloadProgress = None):
        info = self.GetFileDetail(file_path)
        if info == None: return False

        file_name = jSeaFile.__GetFileName(file_path)
        if file_name == None: return False

        link = self.GetDownloadFileLink(file_path)
        if link == None: return False

        try:
            out_file_path = jSeaFile.GetCombinePath(output_folder_path, file_name)
            if progress == None:
                urllib.request.urlretrieve(link, out_file_path)
            else:
                urllib.request.urlretrieve(link, out_file_path, progress.Doing)

            tm = time.mktime(info.last_modified.timetuple())
            os.utime(out_file_path, (tm, tm))
            return True

        except Exception as e:
            return False

    def GetCombinePath(folder:str, file_name:str):
        path = folder
        if path[len(path) - 1:] != '/':
            path = path + '/'
        return path + file_name

    def GetDownloadFileLink(self, file_path:str):
        text = self.__GetResponseUsingToken("/api2/repos/" + self.repo_id + '/file/', {'p':file_path, 'reuse':'0'})
        if text == None: return ""
        return text

    def GetFileDetail(self, file_path:str):
        json_object = self.__GetResponseJsonUsingToken('/api2/repos/' + self.repo_id + '/file/detail/', {'p':file_path})
        if json_object == None: return None

        try:
            last_modified = datetime.strptime(json_object['last_modified'], "%Y-%m-%dT%H:%M:%S%z")
            last_modified_kst = last_modified.astimezone(self.KST)

            info = jSeaFileInfo()
            info.id = json_object['id']
            info.last_modifier_name = json_object['last_modifier_name']
            info.last_modified = last_modified_kst
            info.size = json_object['size']
            return info

        except:
            return None

    def GetRepositoryList(self):
        items:list[jSeaRepositoryInfo] = []

        json_object = self.__GetResponseJsonUsingToken('/api2/repos/')
        if json_object == None: return None

        try:
            for json_item in json_object:
                name = json_item['name']
                item = jSeaRepositoryInfo()
                item.name = json_item['name']
                item.id = json_item['id']
                item.permission = json_item['permission']
                items.append(item)

        except:
            return None

        return items

    def GetListItemsInDirectory(self, dir_path:str):
        items:list[jSeaFileItem] = []

        json_object = self.__GetResponseJsonUsingToken('/api2/repos/' + self.repo_id + '/dir/', {'p':dir_path})
        if json_object == None: return None

        try:
            for json_item in json_object:
                name = json_item['name']
                item = jSeaFileItem(jSeaFile.GetCombinePath(dir_path, name), name, json_item['type'] == 'dir')
                items.append(item)

        except:
            return None

        return items

    def AuthPing(self):
        text = self.__GetResponseUsingToken('/api2/auth/ping/')
        if text == None: return ""
        return text

    def Ping(self):
        try:
            connection:urllib.request._UrlopenRet = urllib.request.urlopen(self.url + '/api2/ping/')
            return jSeaFile.__ParseResponseText(connection.read().decode("utf-8"))

        except:
            return ""

    def __ParseResponseText(text:str):
        if len(text) >= 2:
            if text[0:1] == '\"' and text[len(text) - 1 : ] =='\"':
                # "" 로 묶여 있으면 없애주자
                return text[1 : len(text) - 1]
        
        return text

    def __GetFileName(path:str):
        file_name_start = path.rfind('/')
        if file_name_start < 0: return None

        file_name_start = file_name_start + 1
        return path[file_name_start:]

    def __GetResponseUsingToken(self, relative_url:str, parameters:dict[str,str] = None):
        url_address = self.url + relative_url
        if parameters != None:
            first = True
            for key, value in parameters.items():
                if first:
                    url_address = url_address + "?" + key + "="
                else:
                    url_address = url_address + "&" + key + "="

                url_address = url_address + urllib.parse.quote(value)
                first = False

        try:
            url = urllib.request.Request(url_address)
            url.add_header("Authorization", "Token " + self.api_token)
            url.add_header("Accept", "application/json; charset=utf-8 indent=4")
            connection:urllib.request._UrlopenRet = urllib.request.urlopen(url)
            return jSeaFile.__ParseResponseText(connection.read().decode("utf-8"))

        except Exception as e:
            return None

    def __GetResponseJsonUsingToken(self, relative_url:str, parameters:dict[str, str] = None):
        text = self.__GetResponseUsingToken(relative_url, parameters)
        if text == None: return None

        try:
            return json.loads(text)
        except:
            return None