"""
 blog: https://junostudio.tistory.com/
 git: https://github.com/junostudio3/j18
 j18 config

"""

import configparser
import os


class JConfigParser:
    def __init__(self):
        self.file = configparser.ConfigParser()

    def load(self, filepath: str):
        try:
            self.file.read(filepath, encoding="UTF8")

        except Exception:
            self.file.read(filepath)

    def save(self, filepath: str):
        try:
            with open(filepath, 'wt', encoding="UTF8") as configfile:
                self.file.write(configfile)
                return True

        except Exception:
            return False

    def read_boolean(self, category: str, key: str, default_value: bool):
        return self.read_int(category, key, int(default_value)) != 0

    def read_int(self, category: str, key: str, default_value: int):
        return int(self.read_text(category, key, str(default_value)))

    def read_text(self, category: str, key: str, default_value: str):
        if category not in self.file:
            return default_value
        if key not in self.file[category]:
            return default_value

        return self.file[category][key]

    def write_boolean(self, category: str, key: str,
                      value: bool, default_value: bool):
        self.write_int(category, key, int(value), int(default_value))

    def write_int(self, category: str, key: str,
                  value: int, default_value: int):
        self.write_text(category, key, str(value), str(default_value))

    def write_text(self, category: str, key: str,
                   value: str, default_value: str):
        if value == default_value:
            return    # Default Value는 저장하지 않는다
        if category not in self.file:
            self.file[category] = {}

        self.file[category][key] = value


class J18Config():
    def __init__(self):
        self.file = JConfigParser()
        self.file.load(os.path.expanduser("~/.j18/") + "config")
        self.address = ""
        self.token = ""
        self.repos_id = ""

    def set_server(self, server_name: str):
        category = "server_" + server_name
        self.address = self.file.read_text(category, "address", "")
        self.token = self.file.read_text(category, "token", "")

    def set_repository(self, repository_name: str):
        category = "repos_" + repository_name
        self.repos_id = self.file.read_text(category, "id", "")

    def set_server_and_repository(self, connection_name: str):
        category = "connection_" + connection_name
        server = self.file.read_text(category, "server", "")
        repos = self.file.read_text(category, "repos", "")

        self.set_server(server)
        self.set_repository(repos)
