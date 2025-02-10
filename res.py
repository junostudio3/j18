"""
 blog: https://junostudio.tistory.com/
 git: https://github.com/junostudio3/j18
 j18 resource

"""

import os
import sys


def get_apppath(relative_path):
    try:
        # PyInstaller에 의해 임시폴더에서 실행될 경우 임시폴더로 접근하는 함수
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    # Windows Path는 '\' 가 붙는데 Url 경로로 사용시 '\'가 들어가면 인식을 못한다
    # Windows File System은 '/'도 '\'처럼 잘 인식하므로 '/'로 다 바꾸어준다
    return os.path.join(base_path, relative_path).replace("\\", "/")


def get_resourcepath(relative_path):
    return get_apppath("resource/" + relative_path)


def load_resourcetext(relative_path):
    try:
        with open(get_resourcepath(relative_path), "r", encoding="utf-8") as f:
            return f.read()

    except Exception:
        return ""
