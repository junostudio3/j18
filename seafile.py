"""
 blog: https://junostudio.tistory.com/
 git: https://github.com/junostudio3/j18
    Seafile Web API를 이용하여 파일을 다운 받거나 정보를 얻는 등의 작업을 하기 위한 클래스이다
    API Documents: https://download.seafile.com/published/web-api/home.md
"""

from datetime import datetime
import time
import os
import json

from requests_toolbelt import MultipartEncoder, MultipartEncoderMonitor
import requests
import urllib.request as urlReqeust
import urllib.parse


def GetCombinePath(folder: str, fileName: str):
    path = folder
    if path[len(path) - 1:] != '/' and fileName[0] != '/':
        path = path + '/'
    return path + fileName


class jSeaFileProgress:
    def __init__(self, target):
        self.target = target
        self.firstRun = True

    def SetStartSummary(self, totalSize):
        self.target.SetStartSummary(totalSize)

    def Init(self, fileName):
        self.firstRun = True
        self.fileName = fileName

    def Doing(self, blockNum, blockSize, totalSize):
        if self.firstRun is True:
            self.target.Start(self.fileName, totalSize)
            self.firstRun = False

        downloaded = min(totalSize, blockNum * blockSize)
        self.target.Proc(downloaded)

    def End(self):
        self.target.End()


class jSeafileUploadMonitor:
    def __init__(self, progress: jSeaFileProgress, filepath: str):
        self.progress = progress
        self.totalSize = os.path.getsize(filepath)

        if progress is not None:
            progress.SetStartSummary(self.totalSize)
            progress.Init(os.path.basename(filepath))

    def callback(self, monitor: MultipartEncoderMonitor):
        self.progress.Doing(1, monitor.bytes_read, self.totalSize)


class jSeaRepositoryInfo:
    def __init__(self):
        self.id = ""
        self.name = ""
        self.permission = ""


class jSeaFileInfo:
    def __init__(self):
        self.name = ""
        self.id = ""
        self.last_modifier_name = ""
        self.last_modified: datetime = None
        self.size = 0


class jSeaFileItem:
    def __init__(self, fullPath: str, name: str,
                 isDirectory: bool, mtime: int, size: int):
        self.full_path = fullPath
        self.name = name
        self.is_directory = isDirectory
        self.last_modified: datetime = datetime.fromtimestamp(mtime)
        self.size = size


class jSeaFile:
    url: str = ""
    apiToken: str = ""
    repo_id: str = ""

    def SetAddress(self, url: str):
        self.url = url

    def SetApiToken(self, token):
        self.apiToken = token

    def SetRepositoryId(self, repo_id):
        self.repo_id = repo_id

    def GetApiToken(self, user_name: str, password: str):
        try:
            postData = urllib.parse.urlencode({'username': user_name,
                                               'password': password})
            url = urlReqeust.Request(self.url + '/api2/auth-token/',
                                     postData.encode('UTF-8'))
            connection: urlReqeust._UrlopenRet = urlReqeust.urlopen(url)

            data = connection.read().decode("utf-8")
            jsonObject = json.loads(data)
            return jsonObject['token']
        except Exception:
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

    def IsExistDirectory(self, dir_path: str):
        # /dir/detail 명령이 동작하지 않아서 /dir/ 명령을 사용했다
        url = '/api2/repos/' + self.repo_id + '/dir/'
        json_object = self.__GetResponseJsonUsingToken(url, {'p': dir_path})
        if json_object is None:
            return False

        return True

    def IsExistFile(self, filepath: str):
        # /file/detail 명령으로 체크함
        if self.GetFileDetail(filepath) is None:
            return False

        return True

    def CreateDirectory(self, path: str):
        text = self.__GetResponseUsingToken(
            '/api2/repos/' + self.repo_id + '/dir/',
            {'p': path}, 'operation=mkdir')

        if text is None:
            return None

        try:
            return text == 'success'

        except Exception:
            return False

    def Download(self, seafile_path: str, output_folder_path: str,
                 skip_same_file: bool, progress: jSeaFileProgress = None):
        master_path_is_file = True

        if self.IsExistDirectory(seafile_path):
            # 대상이 폴더면 폴더를 만들고 시작하자
            file_name = __class__.__GetFileName(seafile_path)
            output_folder_path = GetCombinePath(output_folder_path, file_name)
            master_path_is_file = False

            try:
                os.mkdir(output_folder_path)
            except Exception:
                pass

        download_items: list[jSeaFileItem] = self.GetSubItemAll(seafile_path)
        if download_items is None:
            return False

        seafilename = __class__.__GetFileName(seafile_path)

        if skip_same_file:
            item_index = -1
            while True:
                item_index = item_index + 1
                if item_index >= len(download_items):
                    break

                item = download_items[item_index]
                if master_path_is_file:
                    # 선택된 대상이 파일이었으면 그대로 출력
                    out_path = GetCombinePath(output_folder_path, seafilename)
                else:
                    # 선택된 대상이 폴더였으면 파일 경로를 상대경로로 만들어 출력
                    relative_path = item.full_path[len(seafile_path):]
                    out_path = GetCombinePath(output_folder_path, relative_path)

                if os.path.exists(out_path) is False:
                    continue

                if item.is_directory:
                    if os.path.isdir(out_path) is False:
                        # 디렉토리와 같은 이름의 파일이 있다.
                        # 이러면 다운로드가 불가능하다
                        return False

                    # 이미 디렉토리가 있다
                    del download_items[item_index]
                    item_index = item_index - 1
                    continue

                # 파일이다
                if os.path.isdir(out_path) is True:
                    # 파일과 같은 디렉토리가 있다.
                    # 이러면 다운로드가 불가능하다
                    return False

                if os.path.getsize(out_path) != item.size:
                    continue

                file_modifed = datetime.fromtimestamp(os.path.getmtime(out_path))
                if file_modifed != item.last_modified:
                    continue

                # 이미 파일이 있다
                del download_items[item_index]
                item_index = item_index - 1

        total_size = 0
        for item in download_items:
            total_size += item.size

        if progress is not None:
            progress.SetStartSummary(total_size)

        for item in download_items:
            if master_path_is_file:
                # 선택된 대상이 파일이었으면 그대로 출력
                out_path = GetCombinePath(output_folder_path, seafilename)
            else:
                # 선택된 대상이 폴더였으면 파일 경로를 상대경로로 만들어 출력
                relative_path = item.full_path[len(seafile_path):]
                out_path = GetCombinePath(output_folder_path,
                                          relative_path)

            if item.is_directory:
                try:
                    os.mkdir(out_path)
                except Exception:
                    pass

            else:
                link = self.GetDownloadFileLink(item.full_path)
                if link is None:
                    return False

                try:
                    if progress is None:
                        urlReqeust.urlretrieve(link, out_path)
                    else:
                        progress.Init(item.name)
                        urlReqeust.urlretrieve(link,
                                               out_path,
                                               progress.Doing)
                        progress.End()

                    tm = time.mktime(item.last_modified.timetuple())
                    os.utime(out_path, (tm, tm))

                except Exception:
                    return False

        return True

    def GetDownloadFileLink(self, filepath: str):
        url = '/api2/repos/' + self.repo_id + '/file/'
        text = self.__GetResponseUsingToken(url,
                                            {'p': filepath, 'reuse': '0'})
        if text is None:
            return ""
        return text

    def GetFileDetail(self, filepath: str):
        url = '/api2/repos/' + self.repo_id + '/file/detail/'
        json_object = self.__GetResponseJsonUsingToken(url, {'p': filepath})
        if json_object is None:
            return None

        try:
            last_modified = datetime.fromtimestamp(int(json_object['mtime']))

            info = jSeaFileInfo()
            info.name = json_object['name']
            info.id = json_object['id']
            info.last_modifier_name = json_object['last_modifier_name']
            info.last_modified = last_modified
            info.size = json_object['size']
            return info

        except Exception:
            return None

    def GetRepositoryList(self):
        items: list[jSeaRepositoryInfo] = []

        json_object = self.__GetResponseJsonUsingToken('/api2/repos/')
        if json_object is None:
            return None

        try:
            for json_item in json_object:
                item = jSeaRepositoryInfo()
                item.name = json_item['name']
                item.id = json_item['id']
                item.permission = json_item['permission']
                items.append(item)

        except Exception:
            return None

        return items

    def GetSubItemAll(self, seafilepath: str):
        collect_items: list[jSeaFileItem] = []

        info = self.GetFileDetail(seafilepath)
        if info is not None:
            # 파일이다
            collect_items.append(jSeaFileItem(seafilepath,
                                              info.name,
                                              False,
                                              info.last_modified.timestamp(),
                                              info.size))
            return collect_items

        items: list[jSeaFileItem] = []

        url = '/api2/repos/' + self.repo_id + '/dir/'
        json_object = self.__GetResponseJsonUsingToken(url, {'p': seafilepath,
                                                             'recursive': '1'})
        if json_object is None:
            return None

        try:
            for json_item in json_object:
                name = json_item['name']
                is_directory = json_item['type'] == 'dir'
                if 'parent_dir' in json_item:
                    parent_dir = json_item['parent_dir']
                else:
                    parent_dir = "/"
                mtime = int(json_item['mtime'])
                size = 0
                if is_directory is False:
                    size = int(json_item['size'])
                item = jSeaFileItem(GetCombinePath(parent_dir, name),
                                    name,
                                    is_directory,
                                    mtime,
                                    size)
                items.append(item)

        except Exception:
            return None

        return items

    def GetListItemsInDirectory(self, dir_path: str):
        items: list[jSeaFileItem] = []

        url = '/api2/repos/' + self.repo_id + '/dir/'
        jsonObject = self.__GetResponseJsonUsingToken(url, {'p': dir_path})
        if jsonObject is None:
            return None

        try:
            for jsonItem in jsonObject:
                name = jsonItem['name']
                is_directory = jsonItem['type'] == 'dir'
                if 'parent_dir' in jsonItem:
                    parent_dir = jsonItem['parent_dir']
                else:
                    parent_dir = "/"
                mtime = int(jsonItem['mtime'])
                size = 0
                if is_directory is False:
                    size = int(jsonItem['size'])
                item = jSeaFileItem(GetCombinePath(parent_dir, name),
                                    name,
                                    is_directory,
                                    mtime,
                                    size)
                items.append(item)

        except Exception:
            return None

        return items

    def GetUploadFileLink(self, path: str):
        url = self.url + '/api2/repos/' + self.repo_id + '/upload-link/'
        text = self.__GetResponseUsingToken(url, {'p': path})
        if text is None:
            return ""
        return text

    def UploadFile(seafile_uploadfilelink: str,
                   seafile_folder: str,
                   filepath: str,
                   progress: jSeaFileProgress = None):
        # Multipart/form-data format으로 전달해야 함

        try:
            e = MultipartEncoder(fields={
                'parent_dir': seafile_folder,
                'file': (os.path.basename(filepath), open(filepath, 'rb')),
                'replace': '1'
                })

            callback_class = jSeafileUploadMonitor(progress, filepath)
            m = MultipartEncoderMonitor(e, callback_class.callback)
            requests.post(seafile_uploadfilelink,
                          data=m,
                          headers={'Content-Type': m.content_type})
            return True
        except Exception:
            return False

    def AuthPing(self):
        text = self.__GetResponseUsingToken('/api2/auth/ping/')
        if text is None:
            return ""
        return text

    def Ping(self):
        try:
            connection = urlReqeust.urlopen(self.url + '/api2/ping/')
            text = connection.read().decode("utf-8")
            return __class__.__ParseResponseText(text)

        except Exception:
            return ""

    def RequestCancel(self):
        # 아직 구현되지 않음
        pass

    def __ParseResponseText(text: str):
        if len(text) >= 2:
            if text[0:1] == '\"' and text[len(text) - 1:] == '\"':
                # "" 로 묶여 있으면 없애주자
                return text[1: len(text) - 1]

        return text

    def __GetFileName(path: str):
        filename_start = path.rfind('/')
        if filename_start < 0:
            return None

        filename_start = filename_start + 1
        return path[filename_start:]

    def __GetResponseUsingToken(self, relative_url: str,
                                parameters: dict[str, str] = None,
                                post: str = None):
        url_address = self.url + relative_url
        if parameters is not None:
            first = True
            for key, value in parameters.items():
                if first:
                    url_address = url_address + "?" + key + "="
                else:
                    url_address = url_address + "&" + key + "="

                url_address = url_address + urllib.parse.quote(value)
                first = False

        try:
            if post is not None:
                post = post.encode('utf-8')

            url = urlReqeust.Request(url_address, post)
            url.add_header("Authorization", "Token " + self.apiToken)
            url.add_header("Accept",
                           "application/json; charset=utf-8 indent=4")

            connection = urlReqeust.urlopen(url)
            text = connection.read().decode("utf-8")
            return jSeaFile.__ParseResponseText(text)

        except Exception:
            return None

    def __GetResponseJsonUsingToken(self, relative_url: str,
                                    parameters: dict[str, str] = None,
                                    post: str = None):
        text = self.__GetResponseUsingToken(relative_url, parameters, post)
        if text is None:
            return None

        try:
            return json.loads(text)
        except Exception:
            return None
