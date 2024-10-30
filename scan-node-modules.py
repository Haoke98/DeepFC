# _*_ codign:utf8 _*_
"""====================================
@Author:Sadam·Sadik
@Email：1903249375@qq.com
@Date：2024/10/30
@Software: PyCharm
@disc:
======================================="""
import os
import sys


def get_node_modules_sizes(start_path):
    node_modules_sizes = {}

    for dirpath, dirnames, filenames in os.walk(start_path):
        if 'node_modules' in dirnames:
            node_modules_path = os.path.join(dirpath, 'node_modules')
            size = get_directory_size(node_modules_path)
            node_modules_sizes[node_modules_path] = size

    return node_modules_sizes


def get_directory_size(directory):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(directory):
        for filename in filenames:
            file_path = os.path.join(dirpath, filename)
            try:
                total_size += os.path.getsize(file_path)
            except FileNotFoundError:
                continue  # 忽略找不到的文件
    return total_size


def main(start_path='.'):
    """

    :param start_path:可以根据需要修改起始路径
    :return:
    """
    print(f"StartPath:[{start_path}]")
    node_modules_sizes = get_node_modules_sizes(start_path)

    # 按大小排序
    sorted_sizes = sorted(node_modules_sizes.items(), key=lambda x: x[1], reverse=True)

    # 输出结果
    n = 1
    for path, size in sorted_sizes:
        size_mb = size / 1024 / 1024
        if size_mb > 100:
            print(n, f"{path}: {size_mb:.2f} MB")
            n += 1


if __name__ == "__main__":
    main(sys.argv[1])
