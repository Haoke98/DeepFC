# _*_ codign:utf8 _*_
"""====================================
@Author:Sadam·Sadik
@Email：1903249375@qq.com
@Date：2024/11/13
@Software: PyCharm
@disc:
======================================="""


class DirectoryNotExistError(Exception):
    def __init__(self, path):
        self.path = path
        super().__init__(f'Directory does not exist. [{path}]')
