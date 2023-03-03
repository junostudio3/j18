"""
 blog: https://junostudio.tistory.com/
 git: https://github.com/junostudio3/j18
 j18 config

"""

from jlib.configparser import jConfigParser
import os

class j18Config():
    def __init__(self):
        self.file = jConfigParser()
        self.file.Load(os.path.expanduser("~/.j18/") + "config")
        self.address = ""
        self.token = ""
        self.repos_id = ""

    def SetServer(self, server_name:str):
        self.address = self.file.ReadText("server_" + server_name, "address", "")
        self.token = self.file.ReadText("server_" + server_name, "token", "")

    def SetRepository(self, repository_name:str):
        self.repos_id = self.file.ReadText("repos_" + repository_name, "id", "")

    def SetServerAndRepository(self, connection_name:str):
        server = self.file.ReadText("connection_" + connection_name, "server", "")
        repos = self.file.ReadText("connection_" + connection_name, "repos", "")

        self.SetServer(server)
        self.SetRepository(repos)
