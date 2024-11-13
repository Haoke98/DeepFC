import filecmp
import subprocess
import click
import os
import hashlib
from concurrent.futures import ThreadPoolExecutor, as_completed

from tools import storageFormat
from core import FileScanner

fileModels = {}
file_ext_list = []
fileExtModels = {}
TOTOAL = 0
FINISHED = 0


def arrow_choice(choices):
    prompt = 'Use arrow keys to choose, Enter to select:'
    options = [click.style(f' {choice} ', fg='white', bg='blue') for choice in choices]
    selected_index = 0

    while True:
        choices_str = ' '.join(options)
        click.clear()
        click.echo(f'{prompt} {choices_str}')

        key = click.getchar()
        if key == '\r':
            return choices[selected_index]
        elif key == click.Keys.UP:
            selected_index = (selected_index - 1) % len(choices)
        elif key == click.Keys.DOWN:
            selected_index = (selected_index + 1) % len(choices)


def convert_bytes(size):
    # 转换单位为可读性强的格式
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024.0:
            break
        size /= 1024.0
    return f"{size:.2f} {unit}"


def find_largest_files(directory):
    file_sizes = []

    for foldername, subfolders, filenames in os.walk(directory):
        for filename in filenames:
            filepath = os.path.join(foldername, filename)
            if os.path.exists(filepath):
                file_size = os.path.getsize(filepath)
                file_sizes.append((filepath, file_size))

    file_sizes.sort(key=lambda x: x[1], reverse=True)
    while True:
        print("Top 20 largest files in the directory:")
        options = []
        for i, (filepath, size) in enumerate(file_sizes[:20], start=1):
            size_readable = convert_bytes(size)
            print(f"{i}. {filepath} - {size_readable}")
            options.append(str(i))

        choice = input("Enter your choice: ")
        click.echo(f'You chose: {choice}')
        dir_path = os.path.dirname(file_sizes[int(choice)][0])
        print(choice, dir_path)
        subprocess.Popen(['open', dir_path])


@click.group()
def main():
    pass


@main.command(help="深度智能扫描(包含微信文件扫描+MacOS相册扫描)")
@click.option('-d', '--directory', required=True, type=click.Path(exists=True), help='Directory to scan.',
              prompt='Enter the directory to scan.')
def smart_deep_scan(directory):
    # 调用函数
    find_largest_files(directory)


def handle(special_file, root, ):
    # 如果指定前缀或者后缀
    tmpl = special_file.split(".")
    filename = tmpl[0]
    ext = tmpl[-1]
    # print(special_file, ext)
    if fileExtModels.keys().__contains__(ext):
        fileExtModels[ext] += 1
    else:
        fileExtModels.setdefault(ext, 0)
    absPath = os.path.join(root, special_file)
    with open(absPath, 'rb') as f:
        data = f.read()
    statinfo = os.stat(absPath)
    fMD5 = hashlib.md5(data).hexdigest()
    model = {
        "name": filename,
        "path": absPath,
        "ext": ext,
        "size": statinfo.st_size
    }
    if fileModels.keys().__contains__(fMD5):
        # errMsg = f"找到一样的文件:MD5:{fMD5}"+ \
        #          "\n            "+absPath+\
        #          "\n            "+fileModels[fMD5]["path"]
        # raise Exception(errMsg)
        fileModels[fMD5].append(model)
    else:
        fileModels.setdefault(fMD5, [model])


#         if postfix or prefix:
#             # 同时指定前缀和后缀
#             if postfix and prefix:
#                 if special_file.endswith(postfix) and special_file.startswith(prefix):
#                     file_list.append(os.path.join(root, special_file))
#                     continue
#
#             # 只指定后缀
#             elif postfix:
#                 if special_file.endswith(postfix):
#                     file_list.append(os.path.join(root, special_file))
#                     continue
#
#             # 只指定前缀
#             elif prefix:
#                 if special_file.startswith(prefix):
#                     file_list.append(os.path.join(root, special_file))
#                     continue
#
#         # 前缀后缀均未指定
#         else:
#             file_list.append(os.path.join(root, special_file))
#             continue

@main.command(help="浅扫描(目录级普通扫描)")
@click.option('-d', '--directory', required=True, type=click.Path(exists=True), help='Directory to scan.',
              prompt='Enter the directory to scan.')
def scan(directory):
    print(f"开始扫描[{directory}]......")
    global fileModels, fileExtModels, TOTOAL, FINISHED
    pool = ThreadPoolExecutor(max_workers=10)
    futs = []
    for root, sub_dirs, files in os.walk(directory):
        print(root)
        for special_file in files:
            TOTOAL += 1
            print(TOTOAL, "|----------------------------------", special_file)
            if special_file in [".DS_Store"]:
                continue
            th = pool.submit(handle, special_file, root)
            futs.append(th)
    # # print(file_list)	# 打印出扫描到的文件路径
    # return file_list
    as_completed(futs)

    file_ext_list = sorted(fileExtModels.keys(), key=lambda item: len(item), reverse=True)
    print(f"Sum of Ext is {len(file_ext_list)}:")
    colNum = 10
    for r in range(0, len(file_ext_list), colNum):
        linetxt = "  ".join(
            [f"({x},{fileExtModels[x]})" for x in file_ext_list[r: min(r + colNum, len(file_ext_list))]])
        print(linetxt)
    total = 0
    md5s = sorted(fileModels.keys(), key=lambda item: fileModels[item][0]["size"] * len(fileModels[item]), reverse=True)
    clearableSpace = 0
    for md in md5s:
        fs = fileModels[md]
        count = len(fs)
        if count > 1:
            total += 1
            _clearableSpace = fs[0]["size"] * (len(fs) - 1)
            clearableSpace += _clearableSpace
            print(total, md, count, storageFormat(fs[0]["size"]), storageFormat(_clearableSpace), ":")
            for f in fs:
                print("|-------------------", f["path"])
    print(f"There is {storageFormat(clearableSpace)} of space in you devices that can be clean.")


@main.command(help="比较两个文件的内容是否一致(有利于,同内容不同名文件的比较和唯一性确认和重复率计算)")
@click.option("-f1", "--file1", help="要比较的第一个文件", required=True, type=click.Path(exists=True),
              prompt="请输入要比较的文件1")
@click.option("-f2", "--file2", help="要比较的第二个文件", required=True, type=click.Path(exists=True),
              prompt="请输入要比较的文件2")
def compare(file1, file2):
    # 使用 filecmp 模块的cmp方法比较两个文件
    result = filecmp.cmp(file1, file2)

    if result:
        print(f"内容一致")
    else:
        print(f"内容不一致")


@main.command(help="扫描微信缓存文件")
@click.option('--min-size', default=10, help='最小文件大小（MB）', show_default=True)
def scan_wechat(min_size):
    """扫描微信中的大文件"""
    scanner = FileScanner()
    with click.progressbar(length=100, label='正在扫描微信文件...') as bar:
        scanner.scan_message_files(min_size_mb=min_size)
        bar.update(100)
    
    scanner.print_large_files()
    scanner.clean_selected_files()


@main.command(help="启动文件管理器界面")
@click.option('--port', default=5000, help='服务端口号')
def start_ui(port):
    import uvicorn
    uvicorn.run("api:app", host="127.0.0.1", port=port, reload=True)


# 按装订区域中的绿色按钮以运行脚本。
if __name__ == "__main__":
    main()
