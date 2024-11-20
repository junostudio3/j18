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
    def __init__(self, progress: jSeaFileProgress, filePath: str):
        self.progress = progress
        self.totalSize = os.path.getsize(filePath)

        if progress is not None:
            progress.SetStartSummary(self.totalSize)
            progress.Init(os.path.basename(filePath))

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
        self.lastModifierName = ""
        self.lastModified: datetime = None
        self.size = 0


class jSeaFileItem:
    def __init__(self, fullPath: str, name: str,
                 isDirectory: bool, mtime: int, size: int):
        self.fullPath = fullPath
        self.name = name
        self.isDirectory = isDirectory
        self.lastModified: datetime = datetime.fromtimestamp(mtime)
        self.size = size


class jSeaFile:
    url: str = ""
    apiToken: str = ""
    repoId: str = ""

    def SetAddress(self, url: str):
        self.url = url

    def SetApiToken(self, token):
        self.apiToken = token

    def SetRepositoryId(self, repoId):
        self.repoId = repoId

    def GetApiToken(self, userName: str, password: str):
        try:
            postData = urllib.parse.urlencode({'username': userName,
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

    def IsExistDirectory(self, dirPath: str):
        # /dir/detail 명령이 동작하지 않아서 /dir/ 명령을 사용했다
        url = '/api2/repos/' + self.repoId + '/dir/'
        jsonObject = self.__GetResponseJsonUsingToken(url, {'p': dirPath})
        if jsonObject is None:
            return False

        return True

    def IsExistFile(self, file_path: str):
        # /file/detail 명령으로 체크함
        if self.GetFileDetail(file_path) is None:
            return False

        return True

    def CreateDirectory(self, path: str):
        text = self.__GetResponseUsingToken(
            '/api2/repos/' + self.repoId + '/dir/',
            {'p': path}, 'operation=mkdir')

        if text is None:
            return None

        try:
            return text == 'success'

        except Exception:
            return False

    def Download(self, seafilePath: str, outputFolderPath: str,
                 skipSameFile: bool, progress: jSeaFileProgress = None):
        masterPathIsFile = True

        if self.IsExistDirectory(seafilePath):
            # 대상이 폴더면 폴더를 만들고 시작하자
            fileName = __class__.__GetFileName(seafilePath)
            outputFolderPath = GetCombinePath(outputFolderPath, fileName)
            masterPathIsFile = False

            try:
                os.mkdir(outputFolderPath)
            except Exception:
                pass

        downloadItems: list[jSeaFileItem] = self.GetSubItemAll(seafilePath)
        if downloadItems is None:
            return False

        seaFileName = __class__.__GetFileName(seafilePath)

        if skipSameFile:
            itemIndex = -1
            while True:
                itemIndex = itemIndex + 1
                if itemIndex >= len(downloadItems):
                    break

                item = downloadItems[itemIndex]
                if masterPathIsFile:
                    # 선택된 대상이 파일이었으면 그대로 출력
                    outPath = GetCombinePath(outputFolderPath, seaFileName)
                else:
                    # 선택된 대상이 폴더였으면 파일 경로를 상대경로로 만들어 출력
                    relativePath = item.fullPath[len(seafilePath):]
                    outPath = GetCombinePath(outputFolderPath, relativePath)

                if os.path.exists(outPath) is False:
                    continue

                if item.isDirectory:
                    if os.path.isdir(outPath) is False:
                        # 디렉토리와 같은 이름의 파일이 있다.
                        # 이러면 다운로드가 불가능하다
                        return False

                    # 이미 디렉토리가 있다
                    del downloadItems[itemIndex]
                    itemIndex = itemIndex - 1
                    continue

                # 파일이다
                if os.path.isdir(outPath) is True:
                    # 파일과 같은 디렉토리가 있다.
                    # 이러면 다운로드가 불가능하다
                    return False

                if os.path.getsize(outPath) != item.size:
                    continue

                fileModifed = datetime.fromtimestamp(os.path.getmtime(outPath))
                if fileModifed != item.lastModified:
                    continue

                # 이미 파일이 있다
                del downloadItems[itemIndex]
                itemIndex = itemIndex - 1

        totalSize = 0
        for item in downloadItems:
            totalSize += item.size

        if progress is not None:
            progress.SetStartSummary(totalSize)

        for item in downloadItems:
            if masterPathIsFile:
                # 선택된 대상이 파일이었으면 그대로 출력
                outPath = GetCombinePath(outputFolderPath, seaFileName)
            else:
                # 선택된 대상이 폴더였으면 파일 경로를 상대경로로 만들어 출력
                relativePath = item.fullPath[len(seafilePath):]
                outPath = GetCombinePath(outputFolderPath,
                                         relativePath)

            if item.isDirectory:
                try:
                    os.mkdir(outPath)
                except Exception:
                    pass

            else:
                link = self.GetDownloadFileLink(item.fullPath)
                if link is None:
                    return False

                try:
                    if progress is None:
                        urlReqeust.urlretrieve(link, outPath)
                    else:
                        progress.Init(item.name)
                        urlReqeust.urlretrieve(link,
                                               outPath,
                                               progress.Doing)
                        progress.End()

                    tm = time.mktime(item.lastModified.timetuple())
                    os.utime(outPath, (tm, tm))

                except Exception:
                    return False

        return True

    def GetDownloadFileLink(self, filePath: str):
        url = '/api2/repos/' + self.repoId + '/file/'
        text = self.__GetResponseUsingToken(url, {'p': filePath, 'reuse': '0'})
        if text is None:
            return ""
        return text

    def GetFileDetail(self, filePath: str):
        url = '/api2/repos/' + self.repoId + '/file/detail/'
        json_object = self.__GetResponseJsonUsingToken(url, {'p': filePath})
        if json_object is None:
            return None

        try:
            last_modified = datetime.fromtimestamp(int(json_object['mtime']))

            info = jSeaFileInfo()
            info.name = json_object['name']
            info.id = json_object['id']
            info.lastModifierName = json_object['last_modifier_name']
            info.lastModified = last_modified
            info.size = json_object['size']
            return info

        except Exception:
            return None

    def GetRepositoryList(self):
        items: list[jSeaRepositoryInfo] = []

        jsonObject = self.__GetResponseJsonUsingToken('/api2/repos/')
        if jsonObject is None:
            return None

        try:
            for jsonItem in jsonObject:
                item = jSeaRepositoryInfo()
                item.name = jsonItem['name']
                item.id = jsonItem['id']
                item.permission = jsonItem['permission']
                items.append(item)

        except Exception:
            return None

        return items

    def GetSubItemAll(self, seafilePath: str):
        collect_items: list[jSeaFileItem] = []

        info = self.GetFileDetail(seafilePath)
        if info is not None:
            # 파일이다
            collect_items.append(jSeaFileItem(seafilePath,
                                              info.name,
                                              False,
                                              info.lastModified.timestamp(),
                                              info.size))
            return collect_items

        items: list[jSeaFileItem] = []

        url = '/api2/repos/' + self.repoId + '/dir/'
        jsonObject = self.__GetResponseJsonUsingToken(url, {'p': seafilePath,
                                                             'recursive': '1'})
        if jsonObject is None:
            return None

        try:
            for jsonItem in jsonObject:
                name = jsonItem['name']
                isDirectory = jsonItem['type'] == 'dir'
                if 'parent_dir' in jsonItem:
                    parent_dir = jsonItem['parent_dir']
                else:
                    parent_dir = "/"
                mtime = int(jsonItem['mtime'])
                size = 0
                if isDirectory is False:
                    size = int(jsonItem['size'])
                item = jSeaFileItem(GetCombinePath(parent_dir, name),
                                    name,
                                    isDirectory,
                                    mtime,
                                    size)
                items.append(item)

        except Exception:
            return None

        return items

    def GetListItemsInDirectory(self, dirPath: str):
        items: list[jSeaFileItem] = []

        url = '/api2/repos/' + self.repoId + '/dir/'
        jsonObject = self.__GetResponseJsonUsingToken(url, {'p': dirPath})
        if jsonObject is None:
            return None

        try:
            for jsonItem in jsonObject:
                name = jsonItem['name']
                isDirectory = jsonItem['type'] == 'dir'
                if 'parent_dir' in jsonItem:
                    parentDir = jsonItem['parent_dir']
                else:
                    parentDir = "/"
                mtime = int(jsonItem['mtime'])
                size = 0
                if isDirectory is False:
                    size = int(jsonItem['size'])
                item = jSeaFileItem(GetCombinePath(parentDir, name),
                                    name,
                                    isDirectory,
                                    mtime,
                                    size)
                items.append(item)

        except Exception:
            return None

        return items

    def GetUploadFileLink(self, path: str):
        url = self.url + '/api2/repos/' + self.repoId + '/upload-link/'
        text = self.__GetResponseUsingToken(url, {'p': path})
        if text is None:
            return ""
        return text

    def UploadFile(seafileUploadFileLink: str,
                   seafileFolder: str,
                   filePath: str,
                   progress: jSeaFileProgress = None):
        # Multipart/form-data format으로 전달해야 함

        try:
            e = MultipartEncoder(fields={
                    'parent_dir': seafileFolder,
                    'file': (os.path.basename(filePath), open(filePath, 'rb')),
                    'replace': '1'
                })

            callbackClass = jSeafileUploadMonitor(progress, filePath)
            m = MultipartEncoderMonitor(e, callbackClass.callback)
            requests.post(seafileUploadFileLink,
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
        fileNameStart = path.rfind('/')
        if fileNameStart < 0:
            return None

        fileNameStart = fileNameStart + 1
        return path[fileNameStart:]

    def __GetResponseUsingToken(self, relativeUrl: str,
                                parameters: dict[str, str] = None,
                                post: str = None):
        urlAddress = self.url + relativeUrl
        if parameters is not None:
            first = True
            for key, value in parameters.items():
                if first:
                    urlAddress = urlAddress + "?" + key + "="
                else:
                    urlAddress = urlAddress + "&" + key + "="

                urlAddress = urlAddress + urllib.parse.quote(value)
                first = False

        try:
            if post is not None:
                post = post.encode('utf-8')

            url = urlReqeust.Request(urlAddress, post)
            url.add_header("Authorization", "Token " + self.apiToken)
            url.add_header("Accept",
                           "application/json; charset=utf-8 indent=4")

            connection = urlReqeust.urlopen(url)
            text = connection.read().decode("utf-8")
            return jSeaFile.__ParseResponseText(text)

        except Exception:
            return None

    def __GetResponseJsonUsingToken(self, relativeUrl: str,
                                    parameters: dict[str, str] = None,
                                    post: str = None):
        text = self.__GetResponseUsingToken(relativeUrl, parameters, post)
        if text is None:
            return None

        try:
            return json.loads(text)
        except Exception:
            return None
