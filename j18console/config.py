"""
 blog: https://junostudio.tistory.com/
 git: https://github.com/junostudio3/j18
 j18 config

"""

import configparser
import os


class jConfigParser:
    def __init__(self):
        self.file = configparser.ConfigParser()

    def Load(self, filePath: str):
        try:
            self.file.read(filePath, encoding="UTF8")

        except Exception:
            self.file.read(filePath)

    def Save(self, filePath: str):
        try:
            with open(filePath, 'wt', encoding="UTF8") as configfile:
                self.file.write(configfile)
                return True

        except Exception:
            return False

    def ReadBoolean(self, category: str, key: str, defaultValue: bool):
        return self.ReadInt(category, key, int(defaultValue)) != 0

    def ReadInt(self, category: str, key: str, defaultValue: int):
        return int(self.ReadText(category, key, str(defaultValue)))

    def ReadText(self, category: str, key: str, defaultValue: str):
        if category not in self.file:
            return defaultValue
        if key not in self.file[category]:
            return defaultValue

        return self.file[category][key]

    def WriteBoolean(self, category: str, key: str,
                     value: bool, default_value: bool):
        self.WriteInt(category, key, int(value), int(default_value))

    def WriteInt(self, category: str, key: str,
                 value: int, default_value: int):
        self.WriteText(category, key, str(value), str(default_value))

    def WriteText(self, category: str, key: str,
                  value: str, default_value: str):
        if value == default_value:
            return    # Default Value는 저장하지 않는다
        if category not in self.file:
            self.file[category] = {}

        self.file[category][key] = value


class j18Config():
    def __init__(self):
        self.file = jConfigParser()
        self.file.Load(os.path.expanduser("~/.j18/") + "config")
        self.address = ""
        self.token = ""
        self.reposId = ""

    def SetServer(self, server_name: str):
        category = "server_" + server_name
        self.address = self.file.ReadText(category, "address", "")
        self.token = self.file.ReadText(category, "token", "")

    def SetRepository(self, repository_name: str):
        category = "repos_" + repository_name
        self.reposId = self.file.ReadText(category, "id", "")

    def SetServerAndRepository(self, connection_name: str):
        category = "connection_" + connection_name
        server = self.file.ReadText(category, "server", "")
        repos = self.file.ReadText(category, "repos", "")

        self.SetServer(server)
        self.SetRepository(repos)
