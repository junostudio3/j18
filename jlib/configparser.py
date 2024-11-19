"""
 blog: https://junostudio.tistory.com/
 git: https://github.com/junostudio3/j18
 safe configparser

"""

import configparser


class jConfigParser:
    def __init__(self):
        self.file = configparser.ConfigParser()

    def Load(self, file_path: str):
        try:
            self.file.read(file_path, encoding="UTF8")

        except Exception:
            self.file.read(file_path)

    def Save(self, file_path: str):
        try:
            with open(file_path, 'wt', encoding="UTF8") as configfile:
                self.file.write(configfile)
                return True

        except Exception:
            return False

    def ReadBoolean(self, category: str, key: str, default_value: bool):
        return self.ReadInt(category, key, int(default_value)) != 0

    def ReadInt(self, category: str, key: str, default_value: int):
        return int(self.ReadText(category, key, str(default_value)))

    def ReadText(self, category: str, key: str, default_value: str):
        if category not in self.file:
            return default_value
        if key not in self.file[category]:
            return default_value

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
